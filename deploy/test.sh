#!/bin/bash
#
# CC Agent 测试脚本
# 用于测试各项功能是否正常
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

# 测试函数
test_service() {
    print_step "测试服务状态"

    if systemctl is-active --quiet "$SERVICE_NAME"; then
        print_success "服务运行正常"
    else
        print_error "服务未运行"
        return 1
    fi
}

test_python_env() {
    print_step "测试 Python 环境"

    if [ -f "$PROJECT_DIR/venv/bin/python3" ]; then
        print_success "虚拟环境存在"

        cd "$PROJECT_DIR"
        source "$PROJECT_DIR/venv/bin/activate"

        python3 --version
        print_success "Python 环境正常"
    else
        print_error "虚拟环境不存在"
        return 1
    fi
}

test_dependencies() {
    print_step "测试依赖包"

    cd "$PROJECT_DIR"
    source "$PROJECT_DIR/venv/bin/activate"

    python3 -c "import yaml; import requests; print('依赖包检查通过')" 2>/dev/null || {
        print_error "依赖包不完整"
        return 1
    }

    print_success "依赖包完整"
}

test_config() {
    print_step "测试配置文件"

    if [ -f "$PROJECT_DIR/config/config.yaml" ]; then
        print_success "配置文件存在"

        # 检查 webhook 配置
        if grep -q "YOUR_FEISHU_WEBHOOK_URL_HERE" "$PROJECT_DIR/config/config.yaml"; then
            print_warning "请配置飞书 webhook URL"
            print_info "运行: bash deploy/quick_config.sh"
        else
            print_success "飞书 webhook 已配置"
        fi
    else
        print_error "配置文件不存在"
        return 1
    fi
}

test_news_function() {
    print_step "测试新闻功能"

    cd "$PROJECT_DIR"
    source "$PROJECT_DIR/venv/bin/activate"

    print_info "尝试获取新闻（这可能需要一些时间）..."
    python3 -c "
from news_agent import NewsAgent
agent = NewsAgent()
print('新闻 Agent 初始化成功')
" 2>/dev/null || {
        print_error "新闻功能测试失败"
        return 1
    }

    print_success "新闻功能正常"
}

test_log_dir() {
    print_step "测试日志目录"

    if [ -d "$PROJECT_DIR/logs" ]; then
        print_success "日志目录存在"

        # 检查日志文件
        if [ -f "$PROJECT_DIR/logs/cc_agent_service.log" ]; then
            print_info "服务日志存在"
            echo "最近 5 行:"
            tail -5 "$PROJECT_DIR/logs/cc_agent_service.log"
        else
            print_warning "服务日志尚未创建"
        fi
    else
        print_error "日志目录不存在"
        return 1
    fi
}

test_cron() {
    print_step "测试定时任务"

    if crontab -l 2>/dev/null | grep -q "news_agent"; then
        print_success "新闻定时任务已配置"
        crontab -l | grep "news_agent"
    else
        print_warning "新闻定时任务未配置"
    fi

    if crontab -l 2>/dev/null | grep -q "wellness_agent"; then
        print_success "健康提醒定时任务已配置"
        crontab -l | grep "wellness_agent"
    else
        print_warning "健康提醒定时任务未配置"
    fi
}

# 主测试函数
main() {
    print_step "CC Agent 功能测试"

    all_passed=true

    # 运行各项测试
    test_service || all_passed=false
    test_python_env || all_passed=false
    test_dependencies || all_passed=false
    test_config || all_passed=false
    test_news_function || all_passed=false
    test_log_dir || all_passed=false
    test_cron

    # 总结
    echo ""
    echo -e "${GREEN}============================================================${NC}"
    if [ "$all_passed" = true ]; then
        echo -e "${GREEN} ✅ 所有测试通过！${NC}"
        print_success "CC Agent 已准备就绪"
    else
        echo -e "${RED} ⚠️  部分测试失败${NC}"
        print_warning "请检查失败的测试项"
    fi
    echo -e "${GREEN}============================================================${NC}"
}

# 执行测试
main
