#!/bin/bash
#
# CC Agent 快速配置脚本
# 用于快速配置飞书 webhook
#

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# 配置变量
PROJECT_DIR="/opt/cc_agent"
CONFIG_FILE="$PROJECT_DIR/config/config.yaml"
SERVICE_NAME="cc_agent"

# 打印函数
print_info() { echo -e "${BLUE}[INFO]${NC} $1"; }
print_success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
print_warning() { echo -e "${YELLOW}[WARNING]${NC} $1"; }
print_error() { echo -e "${RED}[ERROR]${NC} $1"; }
print_step() {
    echo ""
    echo -e "${GREEN}============================================================${NC}"
    echo -e "${GREEN} $1${NC}"
    echo -e "${GREEN}============================================================${NC}"
}

# 检查文件是否存在
if [ ! -f "$CONFIG_FILE" ]; then
    print_error "配置文件不存在: $CONFIG_FILE"
    exit 1
fi

print_step "快速配置飞书 Webhook"

print_info "请按照以下步骤获取飞书 Webhook URL："
echo ""
echo "1. 打开飞书群组"
echo "2. 群设置 → 机器人 → 自定义机器人"
echo "3. 创建机器人并复制 Webhook URL"
echo ""

read -p "请输入飞书 Webhook URL: " webhook_url

if [ -z "$webhook_url" ]; then
    print_error "Webhook URL 不能为空"
    exit 1
fi

# 备份原配置
print_info "备份原配置..."
cp "$CONFIG_FILE" "${CONFIG_FILE}.backup_$(date +%Y%m%d_%H%M%S)"

# 更新配置
print_info "更新配置文件..."
sed -i "s|webhook_url: 'YOUR_FEISHU_WEBHOOK_URL_HERE'|webhook_url: '$webhook_url'|g" "$CONFIG_FILE"

print_success "配置文件已更新"

# 重启服务
print_info "重启服务..."
systemctl restart "$SERVICE_NAME" || print_warning "服务重启失败"

# 测试
echo ""
read -p "是否测试飞书通知？(yes/no): " test_confirm

if [ "$test_confirm" = "yes" ]; then
    print_info "发送测试消息..."
    cd "$PROJECT_DIR"
    source "$PROJECT_DIR/venv/bin/activate"
    python3 -c "
from feishu_client import FeishuClient
client = FeishuClient('$webhook_url')
client.send_card_message('测试消息', '🎉 CC Agent 部署成功！这是一条测试消息。')
"
    print_success "测试消息已发送，请检查飞书群组"
fi

print_step "配置完成"
print_info "如果测试消息发送成功，配置完成！"
print_info "如需修改其他配置，请编辑: $CONFIG_FILE"
