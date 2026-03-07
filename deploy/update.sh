#!/bin/bash
#
# CC Agent 更新脚本
# 用于更新到最新版本
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
SERVICE_NAME="cc_agent"
BACKUP_DIR="/opt/cc_agent_backups"

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

# 检查 root
if [ "$EUID" -ne 0 ]; then
    print_error "请使用 root 用户运行此脚本"
    exit 1
fi

print_step "CC Agent 更新"

# 创建备份
print_info "创建备份..."
BACKUP_NAME="backup_$(date +%Y%m%d_%H%M%S)"
mkdir -p "$BACKUP_DIR"
cp -r "$PROJECT_DIR" "$BACKUP_DIR/$BACKUP_NAME"
print_success "备份完成: $BACKUP_DIR/$BACKUP_NAME"

# 停止服务
print_info "停止服务..."
systemctl stop "$SERVICE_NAME" || print_warning "服务未运行"

# 更新代码
print_info "更新代码..."
cd "$PROJECT_DIR"
git fetch origin
git pull origin main || {
    print_error "代码更新失败"
    print_info "正在恢复备份..."
    systemctl start "$SERVICE_NAME" || true
    exit 1
}

# 更新依赖
print_info "更新 Python 依赖..."
source "$PROJECT_DIR/venv/bin/activate"
pip install -r requirements.txt || print_warning "依赖更新失败，继续..."

# 启动服务
print_info "重启服务..."
systemctl start "$SERVICE_NAME"
systemctl enable "$SERVICE_NAME"

# 显示状态
print_step "更新完成"
systemctl status "$SERVICE_NAME" --no-pager || true

echo ""
print_success "更新成功！"
print_info "备份位置: $BACKUP_DIR/$BACKUP_NAME"
