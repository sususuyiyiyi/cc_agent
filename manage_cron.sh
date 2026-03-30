#!/bin/bash

# Cron 任务管理脚本

PROJECT_ROOT="$(cd "$(dirname "$0")" && pwd)"
CRON_COMMENT="# CC Agent 定时任务"

echo "============================================================"
echo "🕐 CC Agent Cron 任务管理"
echo "============================================================"

show_status() {
    echo ""
    echo "📊 当前 Cron 任务:"
    echo ""

    if crontab -l 2>/dev/null | grep -q "$CRON_COMMENT"; then
        crontab -l 2>/dev/null | grep "$CRON_COMMENT"
    else
        echo "⚠️ 未配置任何 Cron 任务"
    fi
    echo ""
}

install_jobs() {
    echo ""
    echo "📦 安装 Cron 任务..."

    # 创建临时文件
    TEMP_CRON=$(mktemp)

    # 保留现有的非 CC Agent 任务
    if crontab -l 2>/dev/null | grep -v "$CRON_COMMENT" > "$TEMP_CRON"; then
        : # 已保留现有任务
    else
        touch "$TEMP_CRON"
    fi

    # 添加 CC Agent 任务
    echo "# $CRON_COMMENT - 安装时间: $(date)" >> "$TEMP_CRON"
    echo "0 9 * * * cd $PROJECT_ROOT && bash scripts/run_job.sh news" >> "$TEMP_CRON"
    echo "30 8 * * * cd $PROJECT_ROOT && bash scripts/run_job.sh wellness" >> "$TEMP_CRON"
    echo "0 20 * * * cd $PROJECT_ROOT && bash scripts/run_job.sh review" >> "$TEMP_CRON"

    # 安装新 crontab
    crontab "$TEMP_CRON"
    rm "$TEMP_CRON"

    echo "✅ Cron 任务已安装"
    echo ""
    echo "已配置以下任务:"
    echo "  - 每日新闻: 每天 09:00"
    echo "  - 健康提醒: 每天 08:30"
    echo "  - 晚间回顾: 每天 20:00"
    echo ""
}

uninstall_jobs() {
    echo ""
    echo "🗑️ 卸载 Cron 任务..."

    # 创建临时文件
    TEMP_CRON=$(mktemp)

    # 保留现有的非 CC Agent 任务
    if crontab -l 2>/dev/null | grep -v "$CRON_COMMENT" > "$TEMP_CRON"; then
        # 检查是否还有任务
        if [ -s "$TEMP_CRON" ]; then
            crontab "$TEMP_CRON"
            echo "✅ Cron 任务已卸载"
        else
            crontab -r 2>/dev/null
            echo "✅ Cron 任务已卸载（crontab 已清空）"
        fi
    else
        echo "⚠️ 未找到 Cron 任务"
    fi

    rm "$TEMP_CRON"
    echo ""
}

stop_scheduler_daemon() {
    echo ""
    echo "🛑 停止旧调度器守护进程..."

    # 停止 launchd 服务
    if launchctl list | grep -q "com.susu.ccaagent.scheduler"; then
        launchctl unload "$HOME/Library/LaunchAgents/com.susu.ccaagent.scheduler.plist" 2>/dev/null
        echo "✅ 已停止 launchd 服务"
    fi

    # 停止残留进程
    PIDS=$(pgrep -f "scheduler_daemon.py")
    if [ -n "$PIDS" ]; then
        kill $PIDS
        echo "✅ 已停止调度器进程"
    fi
    echo ""
}

test_job() {
    JOB_NAME="$1"
    if [ -z "$JOB_NAME" ]; then
        echo "❌ 请指定要测试的任务名称: news, wellness, 或 review"
        exit 1
    fi

    echo ""
    echo "🧪 测试任务: $JOB_NAME"
    bash "$PROJECT_ROOT/scripts/run_job.sh" "$JOB_NAME"
}

case "$1" in
    install)
        stop_scheduler_daemon
        install_jobs
        show_status
        ;;

    uninstall)
        uninstall_jobs
        ;;

    status)
        show_status
        ;;

    test)
        test_job "$2"
        ;;

    start|enable)
        echo ""
        echo "⚠️ 请使用 'install' 命令安装 Cron 任务"
        echo ""
        ;;

    stop|disable)
        echo ""
        echo "⚠️ 请使用 'uninstall' 命令卸载 Cron 任务"
        echo ""
        ;;

    *)
        echo ""
        echo "用法: ./manage_cron.sh {install|uninstall|status|test [job_name]}"
        echo ""
        echo "命令说明:"
        echo "  install    - 安装 Cron 任务（会自动停止旧的调度器）"
        echo "  uninstall  - 卸载 Cron 任务"
        echo "  status     - 查看当前 Cron 任务"
        echo "  test [job] - 测试运行指定的任务（news/wellness/review）"
        echo ""
        echo "============================================================"
        exit 1
        ;;
esac

echo "============================================================"
