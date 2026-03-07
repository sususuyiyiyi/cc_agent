#!/bin/bash

# CC Agent Launchd 管理脚本

PROJECT_ROOT="$(cd "$(dirname "$0")" && pwd)"
PLIST_DEST="$HOME/Library/LaunchAgents/com.susu.ccaagent.scheduler.plist"
PLIST_TEMPLATE="$PROJECT_ROOT/config/launchd/com.susu.ccaagent.scheduler.plist.template"

echo "============================================================"
echo "🚀 CC Agent 调度器 Launchd 管理"
echo "============================================================"

case "$1" in
    install)
        echo ""
        echo "📦 安装 launchd 配置（首次使用或项目路径变更时执行）..."
        if [ ! -f "$PLIST_TEMPLATE" ]; then
            echo "❌ 模板不存在: $PLIST_TEMPLATE"
            exit 1
        fi
        mkdir -p "$(dirname "$PLIST_DEST")"
        sed "s|__PROJECT_ROOT__|$PROJECT_ROOT|g" "$PLIST_TEMPLATE" > "$PLIST_DEST"
        echo "✅ 已写入: $PLIST_DEST"
        echo ""
        echo "请确保项目根目录有 .env 并配置模型环境变量，例如："
        echo "  ANTHROPIC_BASE_URL=https://open.bigmodel.cn/api/anthropic"
        echo "  ANTHROPIC_AUTH_TOKEN=你的key"
        echo "  ANTHROPIC_MODEL=glm-4.5-air"
        echo ""
        echo "然后执行: ./manage_launchd.sh start"
        ;;

    status)
        echo ""
        echo "📊 服务状态:"
        echo ""
        if launchctl list | grep -q "com.susu.ccaagent.scheduler"; then
            echo "✅ 服务已加载"
            PID=$(launchctl list | grep "com.susu.ccaagent.scheduler" | awk '{print $1}')
            echo "   PID: $PID"

            if ps -p $PID > /dev/null 2>&1; then
                echo "   状态: 运行中"
                ps -p $PID -o pid,etime,%cpu,%mem,cmd
            else
                echo "   状态: 进程已停止"
            fi
        else
            echo "❌ 服务未加载"
        fi

        echo ""
        echo "📋 定时任务:"
        python3 -c "from scheduler import setup_scheduler; scheduler = setup_scheduler(); scheduler.list_jobs() if scheduler else print('配置未启用')"
        ;;

    start)
        echo ""
        echo "🚀 启动服务..."
        if [ ! -f "$PLIST_DEST" ]; then
            echo "❌ 未安装 plist。请先执行: ./manage_launchd.sh install"
            exit 1
        fi
        if launchctl list | grep -q "com.susu.ccaagent.scheduler"; then
            echo "⚠️ 服务已在运行，尝试重启..."
            launchctl unload "$PLIST_DEST"
            sleep 1
        fi
        launchctl load "$PLIST_DEST"
        sleep 2
        echo "✅ 服务已启动"
        launchctl list | grep "com.susu.ccaagent.scheduler"
        ;;

    stop)
        echo ""
        echo "🛑 停止服务..."
        if launchctl list | grep -q "com.susu.ccaagent.scheduler"; then
            launchctl unload "$PLIST_DEST"
            echo "✅ 服务已停止"
        else
            echo "⚠️ 服务未运行"
        fi

        # 清理残留进程
        PIDS=$(pgrep -f "python3.*scheduler.py")
        if [ -n "$PIDS" ]; then
            echo "🧹 清理残留进程..."
            kill $PIDS
            sleep 1
        fi
        ;;

    restart)
        echo ""
        echo "🔄 重启服务..."
        ./manage_launchd.sh stop
        sleep 2
        ./manage_launchd.sh start
        ;;

    logs)
        echo ""
        echo "📄 服务日志:"
        echo "============================================================"
        if [ -f "$PROJECT_ROOT/logs/scheduler.stdout.log" ]; then
            echo "标准输出 (最近 20 行):"
            tail -20 "$PROJECT_ROOT/logs/scheduler.stdout.log"
        else
            echo "⚠️ 标准输出日志文件不存在"
        fi

        echo ""
        if [ -f "$PROJECT_ROOT/logs/scheduler.stderr.log" ]; then
            echo "标准错误 (最近 20 行):"
            tail -20 "$PROJECT_ROOT/logs/scheduler.stderr.log"
        else
            echo "⚠️ 标准错误日志文件不存在"
        fi
        echo "============================================================"
        ;;

    *)
        echo ""
        echo "用法: ./manage_launchd.sh {install|status|start|stop|restart|logs}"
        echo ""
        echo "命令说明:"
        echo "  install  - 首次使用：安装 launchd plist 到 ~/Library/LaunchAgents"
        echo "  status   - 查看服务状态和定时任务"
        echo "  start    - 启动服务"
        echo "  stop     - 停止服务"
        echo "  restart  - 重启服务"
        echo "  logs     - 查看服务日志"
        echo ""
        echo "============================================================"
        exit 1
        ;;
esac

echo ""
echo "============================================================"
