#!/bin/bash

# CC Agent 调度器停止脚本

echo "============================================================"
echo "🛑 CC Agent 调度器停止"
echo "============================================================"

# 查找调度器进程
PIDS=$(pgrep -f "python3.*scheduler.py")

if [ -z "$PIDS" ]; then
    echo "⚠️ 调度器未在运行"
    exit 0
fi

echo ""
echo "找到调度器进程:"
ps -p $PIDS -o pid,cmd

echo ""
echo "正在停止调度器..."

# 停止进程
kill $PIDS

# 等待进程结束
sleep 2

# 检查进程是否已停止
if pgrep -f "python3.*scheduler.py" > /dev/null; then
    echo "⚠️ 进程未响应，强制停止..."
    pkill -9 -f "python3.*scheduler.py"
    sleep 1
fi

# 最终检查
if pgrep -f "python3.*scheduler.py" > /dev/null; then
    echo "❌ 调度器停止失败"
    exit 1
else
    echo "✅ 调度器已停止"
fi

echo ""
echo "============================================================"
