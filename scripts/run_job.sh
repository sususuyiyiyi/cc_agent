#!/bin/bash
# 作业运行脚本
# 用于 cron 调度

PROJECT_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$PROJECT_ROOT"

# 加载环境变量
if [ -f .env ]; then
    export $(cat .env | grep -v '^#' | xargs)
fi

JOB_NAME="$1"
LOG_FILE="logs/cron_${JOB_NAME}.log"
mkdir -p logs

echo "========================================" >> "$LOG_FILE"
echo "$(date '+%Y-%m-%d %H:%M:%S') - 开始执行: $JOB_NAME" >> "$LOG_FILE"
echo "========================================" >> "$LOG_FILE"

case "$JOB_NAME" in
    news)
        echo "执行新闻任务..." >> "$LOG_FILE"
        python3 news_agent.py >> "$LOG_FILE" 2>&1
        ;;
    wellness)
        echo "执行健康提醒任务..." >> "$LOG_FILE"
        python3 wellness_agent.py >> "$LOG_FILE" 2>&1
        ;;
    review)
        echo "执行回顾任务..." >> "$LOG_FILE"
        # 使用 echo 传递 EOF 给 review_agent
        echo "" | python3 review_agent.py >> "$LOG_FILE" 2>&1
        ;;
    *)
        echo "未知的任务: $JOB_NAME" >> "$LOG_FILE"
        exit 1
        ;;
esac

echo "$(date '+%Y-%m-%d %H:%M:%S') - 任务完成: $JOB_NAME" >> "$LOG_FILE"
echo "========================================" >> "$LOG_FILE"
echo "" >> "$LOG_FILE"
