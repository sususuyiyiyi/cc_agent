#!/bin/bash

# CC Agent 调度器状态查看脚本

echo "============================================================"
echo "📊 CC Agent 调度器状态"
echo "============================================================"

# 检查进程是否运行
PIDS=$(pgrep -f "python3.*scheduler.py")

if [ -z "$PIDS" ]; then
    echo ""
    echo "❌ 调度器未运行"
    echo ""
    echo "启动调度器: ./start_scheduler.sh"
    echo "============================================================"
    exit 0
fi

echo ""
echo "✅ 调度器运行中"
echo ""
echo "进程信息:"
ps -p $PIDS -o pid,etime,%cpu,%mem,cmd

echo ""
echo "定时任务配置:"
python3 -c "from scheduler import setup_scheduler; scheduler = setup_scheduler(); scheduler.list_jobs() if scheduler else print('配置未启用')"

echo ""
echo "最近日志 (最后20行):"
echo "============================================================"
if [ -f "logs/scheduler.log" ]; then
    tail -n 20 logs/scheduler.log
else
    echo "⚠️ 日志文件不存在"
fi

echo ""
echo "============================================================"
echo "查看完整日志: tail -f logs/scheduler.log"
echo "停止调度器: ./stop_scheduler.sh"
echo "============================================================"
