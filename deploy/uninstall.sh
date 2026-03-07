#!/bin/bash
#
# CC Agent 卸载脚本
# 用于完全移除 CC Agent
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

# 确认卸载
print_warning "警告: 此操作将删除 CC Agent 及所有数据！"
echo ""
read -p "确定要继续吗？(yes/no): " confirm

if [ "$confirm" != "yes" ]; then
    print_info "取消卸载"
    exit 0
fi

print_step "卸载 CC Agent"

# 停止服务
print_info "停止服务..."
systemctl stop "$SERVICE_NAME" 2>/dev/null || true
systemctl disable "$SERVICE_NAME" 2>/dev/null || true

# 删除服务文件
print_info "删除 systemd 服务..."
rm -f "/etc/systemd/system/${SERVICE_NAME}.service"
systemctl daemon-reload

# 备份选项
echo ""
read -p "是否备份数据？(yes/no): " backup_confirm

if [ "$backup_confirm" = "yes" ]; then
    print_info "备份数据..."
    BACKUP_NAME="backup_before_uninstall_$(date +%Y%m%d_%H%M%S)"
    mkdir -p "$BACKUP_DIR"
    cp -r "$PROJECT_DIR" "$BACKUP_DIR/$BACKUP_NAME"
    print_success "备份完成: $BACKUP_DIR/$BACKUP_NAME"
fi

# 删除项目目录
print_info "删除项目目录..."
rm -rf "$PROJECT_DIR"

print_step "卸载完成"
print_success "CC Agent 已完全卸载"

if [ "$backup_confirm" = "yes" ]; then
    print_info "备份数据位于: $BACKUP_DIR/$BACKUP_NAME"
fi
