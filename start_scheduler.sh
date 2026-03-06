#!/bin/bash

# CC Agent 调度器启动脚本

echo "============================================================"
echo "🚀 CC Agent 调度器启动"
echo "============================================================"

# 检查是否已运行
if pgrep -f "python3.*scheduler.py" > /dev/null; then
    echo "⚠️ 调度器已在运行中"
    echo ""
    echo "运行中的进程:"
    ps aux | grep "python3.*scheduler.py" | grep -v grep
    echo ""
    echo "如需重启，请先运行: ./stop_scheduler.sh"
    exit 1
fi

# 进入项目目录
cd "$(dirname "$0")"

# 创建日志目录
mkdir -p logs

# 启动调度器
echo ""
echo "📅 启动调度器..."
echo "📍 目录: $(pwd)"
echo "⏰ 时区: Asia/Shanghai (UTC+8)"
echo ""

# 使用 nohup 后台运行
nohup python3 scheduler.py > logs/scheduler.log 2>&1 &
SCHEDULER_PID=$!

# 等待进程启动
sleep 2

# 检查进程是否成功启动
if ps -p $SCHEDULER_PID > /dev/null; then
    echo "✅ 调度器启动成功"
    echo "   PID: $SCHEDULER_PID"
    echo "   日志: logs/scheduler.log"
    echo ""
    echo "查看日志: tail -f logs/scheduler.log"
    echo "停止调度器: ./stop_scheduler.sh"
    echo ""
    echo "============================================================"
else
    echo "❌ 调度器启动失败"
    echo "查看日志: cat logs/scheduler.log"
    exit 1
fi
