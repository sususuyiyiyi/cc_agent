#!/bin/bash
#
# CC Agent 自动化部署脚本 - 阿里云版本
# 适用于 Ubuntu 20.04/22.04
#

set -e  # 遇到错误立即退出

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 配置变量
PROJECT_DIR="/opt/cc_agent"
PYTHON_VERSION="3.8"
VENV_NAME="venv"
SERVICE_NAME="cc_agent"
REPO_URL="https://github.com/sususuyiyiyi/cc_agent.git"

# 打印带颜色的消息
print_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_step() {
    echo ""
    echo -e "${GREEN}============================================================${NC}"
    echo -e "${GREEN} $1${NC}"
    echo -e "${GREEN}============================================================${NC}"
}

# 检查是否为 root 用户
check_root() {
    print_step "检查用户权限"
    if [ "$EUID" -ne 0 ]; then
        print_error "请使用 root 用户运行此脚本"
        print_info "使用: sudo bash install.sh"
        exit 1
    fi
    print_success "正在使用 root 用户"
}

# 检查系统信息
check_system() {
    print_step "检查系统信息"

    # 检查系统版本
    if [ -f /etc/os-release ]; then
        . /etc/os-release
        print_info "操作系统: $PRETTY_NAME"
    else
        print_error "无法检测操作系统"
        exit 1
    fi

    # 检查架构
    ARCH=$(uname -m)
    print_info "系统架构: $ARCH"

    # 检查内存
    MEM=$(free -m | awk 'NR==2{print $2}')
    print_info "系统内存: ${MEM}MB"

    if [ "$MEM" -lt 512 ]; then
        print_warning "内存较少，建议至少 512MB"
    fi

    # 检查磁盘空间
    DISK=$(df -h / | awk 'NR==2{print $4}' | sed 's/G//')
    print_info "可用磁盘: ${DISK}GB"

    if (( $(echo "$DISK < 10" | bc -l) )); then
        print_warning "磁盘空间较少，建议至少 10GB"
    fi
}

# 更新系统
update_system() {
    print_step "更新系统"

    print_info "更新软件包列表..."
    apt update

    print_info "升级已安装的软件包..."
    DEBIAN_FRONTEND=noninteractive apt upgrade -y

    print_success "系统更新完成"
}

# 安装基础工具
install_basic_tools() {
    print_step "安装基础工具"

    print_info "安装必要的软件包..."
    apt install -y \
        git \
        python3 \
        python3-pip \
        python3-venv \
        curl \
        wget \
        vim \
        htop \
        bc \
        jq \
        nginx \
        certbot \
        python3-certbot-nginx \
        unzip

    # 升级 pip
    print_info "升级 pip..."
    python3 -m pip install --upgrade pip

    print_success "基础工具安装完成"
}

# 设置时区
setup_timezone() {
    print_step "设置时区"

    print_info "设置时区为 Asia/Shanghai..."
    timedatectl set-timezone Asia/Shanghai

    # 显示时间
    CURRENT_TIME=$(date '+%Y-%m-%d %H:%M:%S')
    print_info "当前时间: $CURRENT_TIME"
    print_info "时区: $(date '+%Z')"

    print_success "时区设置完成"
}

# 设置防火墙
setup_firewall() {
    print_step "配置防火墙"

    print_info "检查 UFW 状态..."
    if ! command -v ufw &> /dev/null; then
        apt install -y ufw
    fi

    print_info "允许 SSH 连接..."
    ufw allow OpenSSH

    print_info "允许 HTTP/HTTPS..."
    ufw allow 80/tcp
    ufw allow 443/tcp

    print_info "启用防火墙..."
    echo "y" | ufw enable

    print_success "防火墙配置完成"
}

# 创建项目目录
create_project_dir() {
    print_step "创建项目目录"

    if [ -d "$PROJECT_DIR" ]; then
        print_warning "项目目录已存在，正在备份..."
        BACKUP_DIR="${PROJECT_DIR}_backup_$(date +%Y%m%d_%H%M%S)"
        mv "$PROJECT_DIR" "$BACKUP_DIR"
        print_info "旧版本已备份到: $BACKUP_DIR"
    fi

    mkdir -p "$PROJECT_DIR"
    print_success "项目目录创建完成: $PROJECT_DIR"
}

# 部署代码
deploy_code() {
    print_step "部署代码"

    cd "$PROJECT_DIR"

    # 检查是否从 GitHub 克隆
    print_info "从 GitHub 克隆代码..."
    if git clone "$REPO_URL" .; then
        print_success "代码克隆成功"
    else
        print_error "代码克隆失败"
        print_info "请检查网络连接或仓库地址"
        exit 1
    fi

    # 设置权限
    chmod -R 755 "$PROJECT_DIR"

    print_success "代码部署完成"
}

# 创建虚拟环境
create_venv() {
    print_step "创建 Python 虚拟环境"

    cd "$PROJECT_DIR"

    print_info "创建虚拟环境..."
    python3 -m venv "$VENV_NAME"

    print_info "激活虚拟环境..."
    source "$VENV_NAME/bin/activate"

    # 升级 pip
    pip install --upgrade pip

    print_success "虚拟环境创建完成"
}

# 安装依赖
install_dependencies() {
    print_step "安装 Python 依赖"

    cd "$PROJECT_DIR"
    source "$VENV_NAME/bin/activate"

    # 检查 requirements.txt
    if [ -f "requirements.txt" ]; then
        print_info "安装 requirements.txt 中的依赖..."
        pip install -r requirements.txt
    else
        print_warning "requirements.txt 不存在，跳过依赖安装"
    fi

    # 安装额外的依赖（如果需要）
    print_info "安装额外依赖..."
    pip install requests beautifulsoup4 pyyaml

    print_success "依赖安装完成"
}

# 创建配置文件
create_config() {
    print_step "创建配置文件"

    CONFIG_DIR="$PROJECT_DIR/config"
    mkdir -p "$CONFIG_DIR"

    if [ ! -f "$CONFIG_DIR/config.yaml" ]; then
        print_info "创建默认配置文件..."

        cat > "$CONFIG_DIR/config.yaml" << 'EOF'
# CC Agent 配置文件
# 部署到服务器后，请根据需要修改配置

feishu:
  app_id: ''
  app_secret: ''
  enabled: true
  message:
    news_enabled: true
    review_enabled: true
    wellness_enabled: true
  webhook_url: 'YOUR_FEISHU_WEBHOOK_URL_HERE'

logging:
  backup_count: 5
  file: ./logs/cc_agent.log
  level: INFO
  max_size_mb: 10

preferences:
  news:
    categories:
      - AI垂直
      - 科技媒体
      - 国际科技
      - AI研究
      - AI日报
    language: zh
    sources:
      - https://www.zhidx.com
      - https://www.leiphone.com
      - https://www.cvmart.net
      - https://www.syncedreview.com
      - https://www.infoq.cn/topic/ai
      - https://www.jiqizhixin.com
      - https://www.qbitai.com
      - https://www.aiteach.com
      - https://36kr.com
      - https://www.huxiu.com
      - https://www.geekpark.net
      - https://www.tmtpost.com
      - https://www.latepost.com
      - https://www.pingwest.com
      - https://techcrunch.com
      - https://venturebeat.com/ai
      - https://www.theinformation.com
      - https://www.technologyreview.com
      - https://openai.com/blog
      - https://deepmind.google/blog
      - https://huggingface.co/blog
      - https://www.anthropic.com/news
      - https://www.deeplearning.ai/the-batch/
      - https://www.therundown.ai
      - https://tldr.tech/ai
      - https://www.bensbites.co
      - https://www.reddit.com/r/artificial
      - https://www.reddit.com/r/MachineLearning
      - https://www.reddit.com/r/ChatGPT
      - https://www.reddit.com/r/openai
      - https://www.reddit.com/r/technology
      - https://www.reddit.com/r/programming
      - https://www.reddit.com/r/compsci
      - https://www.ithome.com
    priority_sources:
      - https://openai.com/blog
      - https://deepmind.google/blog
      - https://www.anthropic.com/news
      - https://www.therundown.ai
      - https://tldr.tech/ai
      - https://www.bensbites.co
      - https://www.zhidx.com
      - https://36kr.com
    weighting:
      research_sources:
        - https://openai.com/blog
        - https://deepmind.google/blog
        - https://huggingface.co/blog
        - https://www.anthropic.com/news
      research_weight: 3.0
      daily_sources:
        - https://www.therundown.ai
        - https://tldr.tech/ai
        - https://www.bensbites.co
      daily_weight: 2.5
      ai_vertical_sources:
        - https://www.zhidx.com
        - https://www.leiphone.com
        - https://www.cvmart.net
        - https://www.syncedreview.com
      ai_vertical_weight: 2.0
      reddit_sources:
        - https://www.reddit.com/r/artificial
        - https://www.reddit.com/r/MachineLearning
        - https://www.reddit.com/r/ChatGPT
        - https://www.reddit.com/r/openai
      reddit_weight: 1.8
      tech_media_sources:
        - https://36kr.com
        - https://www.huxiu.com
        - https://www.geekpark.net
      tech_media_weight: 1.5
      international_sources:
        - https://techcrunch.com
        - https://venturebeat.com/ai
        - https://www.theinformation.com
      international_weight: 1.8
  review:
    auto_save: true
    template: default
  wellness:
    include_diet: true
    include_outfit: true
    temperature_unit: celsius

scheduling:
  enabled: true
  timezone: Asia/Shanghai
  news_su:
    enabled: true
    time: "08:00"
  wellness_su:
    enabled: true
    time: "08:30"
  review_su:
    enabled: false
    time: "20:00"

storage:
  backup_dir: ./backups
  backup_enabled: false
  backup_retention_days: 30
  data_dir: ./data

user:
  location:
    city: Shanghai
    country: China
    lat: 31.2304
    lon: 121.4737
  name: susu
  timezone: Asia/Shanghai

weather:
  enabled: false
  openweathermap:
    api_key: ''
    units: metric
  provider: openweathermap
  qweather:
    api_key: ''
    units: metric

websearch:
  enabled: false
  max_results: 10
  search_engine: default
  timeout: 30
EOF

        print_success "配置文件创建完成"
    else
        print_info "配置文件已存在，跳过创建"
    fi

    print_warning "请记得修改 config.yaml 中的 webhook_url！"
}

# 创建日志目录
create_log_dirs() {
    print_step "创建日志和数据目录"

    mkdir -p "$PROJECT_DIR/logs"
    mkdir -p "$PROJECT_DIR/data"
    mkdir -p "$PROJECT_DIR/backups"
    mkdir -p "$PROJECT_DIR/data/news"
    mkdir -p "$PROJECT_DIR/data/reviews"

    print_success "目录创建完成"
}

# 创建 systemd 服务
create_systemd_service() {
    print_step "创建 systemd 服务"

    SERVICE_FILE="/etc/systemd/system/${SERVICE_NAME}.service"

    print_info "创建服务文件: $SERVICE_FILE"

    cat > "$SERVICE_FILE" << EOF
[Unit]
Description=CC Agent News Service
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=$PROJECT_DIR
Environment="PATH=$PROJECT_DIR/$VENV_NAME/bin"
Environment="PYTHONPATH=$PROJECT_DIR"
ExecStart=$PROJECT_DIR/$VENV_NAME/bin/python3 $PROJECT_DIR/news_agent.py
Restart=always
RestartSec=10
StandardOutput=append:$PROJECT_DIR/logs/cc_agent_service.log
StandardError=append:$PROJECT_DIR/logs/cc_agent_service_error.log

[Install]
WantedBy=multi-user.target
EOF

    # 重载 systemd
    systemctl daemon-reload

    print_success "systemd 服务创建完成"
}

# 创建 cron 服务（用于定时任务）
create_cron_service() {
    print_step "配置定时任务"

    # 获取 Python 路径
    PYTHON_PATH="$PROJECT_DIR/$VENV_NAME/bin/python3"
    LOG_DIR="$PROJECT_DIR/logs"

    print_info "配置定时任务..."
    print_info "每天 08:00 发送新闻"
    print_info "每天 08:30 发送健康提醒"

    # 创建 crontab
    cat > /tmp/cc_agent_cron << EOF
# CC Agent 定时任务
# 每天早上 8 点发送新闻
0 8 * * * cd $PROJECT_DIR && $PYTHON_PATH news_agent.py >> $LOG_DIR/news_cron.log 2>&1

# 每天早上 8:30 发送健康提醒
30 8 * * * cd $PROJECT_DIR && $PYTHON_PATH wellness_agent.py >> $LOG_DIR/wellness_cron.log 2>&1
EOF

    # 安装 crontab
    crontab /tmp/cc_agent_cron
    rm /tmp/cc_agent_cron

    print_success "定时任务配置完成"
}

# 设置权限
setup_permissions() {
    print_step "设置文件权限"

    chmod -R 755 "$PROJECT_DIR"
    chmod +x "$PROJECT_DIR"/*.sh 2>/dev/null || true

    print_success "权限设置完成"
}

# 安装监控脚本
install_monitor_script() {
    print_step "安装监控脚本"

    MONITOR_SCRIPT="$PROJECT_DIR/monitor.sh"

    cat > "$MONITOR_SCRIPT" << 'EOF'
#!/bin/bash
# CC Agent 监控脚本

PROJECT_DIR="/opt/cc_agent"
LOG_FILE="$PROJECT_DIR/logs/monitor.log"
MAX_LOG_SIZE=10485760  # 10MB

# 检查并轮转日志
rotate_log() {
    if [ -f "$LOG_FILE" ] && [ $(stat -f%z "$LOG_FILE" 2>/dev/null || stat -c%s "$LOG_FILE") -gt $MAX_LOG_SIZE ]; then
        mv "$LOG_FILE" "${LOG_FILE}.old"
    fi
}

# 主监控逻辑
rotate_log

echo "[$(date '+%Y-%m-%d %H:%M:%S')] 开始健康检查..." >> $LOG_FILE

# 检查磁盘空间
DISK_USAGE=$(df / | awk 'NR==2{print $5}' | sed 's/%//')
if [ $DISK_USAGE -gt 80 ]; then
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] 警告: 磁盘空间不足 ${DISK_USAGE}%" >> $LOG_FILE
fi

# 检查内存
MEM_USAGE=$(free | awk 'NR==2{printf "%.0f", $3*100/$2}')
if [ $MEM_USAGE -gt 90 ]; then
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] 警告: 内存使用过高 ${MEM_USAGE}%" >> $LOG_FILE
fi

echo "[$(date '+%Y-%m-%d %H:%M:%S')] 健康检查完成" >> $LOG_FILE
EOF

    chmod +x "$MONITOR_SCRIPT"

    # 添加到 crontab（每小时运行）
    (crontab -l 2>/dev/null | grep -v "monitor.sh"; echo "0 * * * * $MONITOR_SCRIPT") | crontab -

    print_success "监控脚本安装完成"
}

# 启动服务
start_service() {
    print_step "启动服务"

    print_info "启动 CC Agent 服务..."
    systemctl start "$SERVICE_NAME"

    print_info "设置开机自启..."
    systemctl enable "$SERVICE_NAME"

    print_success "服务启动完成"
}

# 显示服务状态
show_status() {
    print_step "服务状态"

    print_info "systemd 服务状态:"
    systemctl status "$SERVICE_NAME" --no-pager || true

    echo ""
    print_info "定时任务列表:"
    crontab -l | grep -E "(news|wellness)" || true

    echo ""
    print_info "最近的日志:"
    if [ -f "$PROJECT_DIR/logs/cc_agent_service.log" ]; then
        tail -10 "$PROJECT_DIR/logs/cc_agent_service.log"
    else
        print_warning "日志文件尚未创建"
    fi
}

# 显示部署信息
show_deployment_info() {
    echo ""
    echo -e "${GREEN}============================================================${NC}"
    echo -e "${GREEN} 🎉 部署完成！${NC}"
    echo -e "${GREEN}============================================================${NC}"
    echo ""
    echo "项目目录: $PROJECT_DIR"
    echo "服务名称: $SERVICE_NAME"
    echo ""
    echo -e "${YELLOW}重要提示：${NC}"
    echo "1. 请修改配置文件中的 webhook_url："
    echo "   vim $PROJECT_DIR/config/config.yaml"
    echo ""
    echo "2. 修改配置后重启服务："
    echo "   systemctl restart $SERVICE_NAME"
    echo ""
    echo "3. 查看服务状态："
    echo "   systemctl status $SERVICE_NAME"
    echo ""
    echo "4. 查看日志："
    echo "   tail -f $PROJECT_DIR/logs/cc_agent_service.log"
    echo ""
    echo "5. 测试新闻功能："
    echo "   cd $PROJECT_DIR && source venv/bin/activate && python3 news_agent.py"
    echo ""
    echo "6. 常用命令："
    echo "   systemctl start $SERVICE_NAME   # 启动服务"
    echo "   systemctl stop $SERVICE_NAME    # 停止服务"
    echo "   systemctl restart $SERVICE_NAME # 重启服务"
    echo "   systemctl enable $SERVICE_NAME # 开机自启"
    echo ""
    echo -e "${GREEN}============================================================${NC}"
}

# 主函数
main() {
    echo ""
    echo -e "${GREEN}"
    echo "============================================================"
    echo "       CC Agent 自动化部署脚本 - 阿里云版本"
    echo "============================================================"
    echo -e "${NC}"
    echo ""

    # 检查环境
    check_root
    check_system

    # 更新系统
    update_system

    # 安装基础工具
    install_basic_tools

    # 配置系统
    setup_timezone
    setup_firewall

    # 部署项目
    create_project_dir
    deploy_code
    create_venv
    install_dependencies
    create_config
    create_log_dirs

    # 配置服务
    create_systemd_service
    create_cron_service
    setup_permissions
    install_monitor_script

    # 启动服务
    start_service

    # 显示状态
    show_status

    # 显示部署信息
    show_deployment_info

    exit 0
}

# 执行主函数
main
