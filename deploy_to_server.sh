#!/bin/bash
#
# CC Agent 服务器部署脚本
# 适用于 Alibaba Cloud Linux (OpenAnolis)
#

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# 打印函数
print_info() { echo -e "${BLUE}[INFO]${NC} $1"; }
print_success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
print_error() { echo -e "${RED}[ERROR]${NC} $1"; }
print_step() {
    echo ""
    echo -e "${GREEN}============================================================${NC}"
    echo -e "${GREEN} $1${NC}"
    echo -e "${GREEN}============================================================${NC}"
}

# 检查是否为 root
if [ "$EUID" -ne 0 ]; then
    print_error "请使用 root 用户运行此脚本"
    print_info "使用: sudo bash deploy_to_server.sh"
    exit 1
fi

print_step "CC Agent 服务器部署"

# 1. 更新系统
print_step "更新系统"
yum update -y
yum upgrade -y

# 2. 安装基础工具
print_step "安装基础工具"
yum install -y git python3 python3-pip python3-devel curl wget vim

# 3. 创建项目目录
print_step "创建项目目录"
mkdir -p /opt
cd /opt

# 4. 克隆代码
print_step "克隆代码"
if [ ! -d "cc_agent" ]; then
    git clone https://github.com/sususuyiyiyi/cc_agent.git
else
    cd cc_agent
    git pull origin main
    cd ..
fi

cd cc_agent

# 5. 创建虚拟环境
print_step "创建 Python 虚拟环境"
python3 -m venv venv
source venv/bin/activate

# 6. 升级 pip 并安装依赖
print_step "安装 Python 依赖"
pip install --upgrade pip
pip install -r requirements.txt

# 7. 创建目录
print_step "创建必要目录"
mkdir -p logs data backups data/news data/reviews

# 8. 创建 systemd 服务文件
print_step "创建 systemd 服务"
cat > /etc/systemd/system/cc-agent.service << 'EOF'
[Unit]
Description=CC Agent Scheduler - Manages news, wellness, and review tasks
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/opt/cc_agent
Environment="PATH=/opt/cc_agent/venv/bin"
Environment="PYTHONPATH=/opt/cc_agent"
ExecStart=/opt/cc_agent/venv/bin/python3 /opt/cc_agent/scheduler_daemon.py
Restart=always
RestartSec=10
StandardOutput=append:/opt/cc_agent/logs/scheduler_service.log
StandardError=append:/opt/cc_agent/logs/scheduler_service_error.log

[Install]
WantedBy=multi-user.target
EOF

# 9. 创建 .env 文件模板
print_step "创建环境变量文件"
if [ ! -f ".env" ]; then
    cat > .env << 'ENVEOF'
ANTHROPIC_BASE_URL=https://open.bigmodel.cn/api/anthropic
ANTHROPIC_AUTH_TOKEN=your_api_key_here
ANTHROPIC_MODEL=glm-4.5-air
TZ=Asia/Shanghai
ENVEOF
    chmod 600 .env
    print_success ".env 文件已创建"
else
    print_info ".env 文件已存在，跳过创建"
fi

# 10. 重载 systemd 并启动服务
print_step "启动服务"
systemctl daemon-reload
systemctl enable cc-agent
systemctl start cc-agent

# 11. 显示状态
print_step "部署完成"
print_success "CC Agent 已成功部署！"
print_success "服务已启动并设置开机自启"

echo ""
print_info "后续步骤："
echo "1. 编辑 API 密钥：vim /opt/cc_agent/.env"
echo "2. 重启服务：systemctl restart cc-agent"
echo "3. 查看服务状态：systemctl status cc-agent"
echo "4. 查看日志：tail -f /opt/cc_agent/logs/scheduler_execution.log"

echo ""
systemctl status cc-agent

print_step "部署信息"
echo "项目目录：/opt/cc_agent"
echo "服务名称：cc-agent"
echo "飞书 Webhook：已在 config.yaml 中配置"
