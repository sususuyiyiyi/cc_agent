#!/bin/bash
# 检查调度器健康状态脚本

echo "============================================================"
echo "🏥 CC Agent 调度器健康检查"
echo "============================================================"
echo ""

# 检查 launchd 服务
echo "📊 Launchd 服务状态:"
if launchctl list | grep -q "com.susu.ccaagent.scheduler"; then
    PID=$(launchctl list | grep "com.susu.ccaagent.scheduler" | awk '{print $1}')
    echo "✅ 服务正在运行 (PID: $PID)"
else
    echo "❌ 服务未运行"
fi
echo ""

# 检查进程
echo "📋 进程状态:"
if pgrep -f "scheduler_daemon.py" > /dev/null; then
    PID=$(pgrep -f "scheduler_daemon.py" | head -1)
    ELAPSED=$(ps -p $PID -o etime= | tr -d ' ')
    echo "✅ 进程存在 (PID: $PID, 运行时长: $ELAPSED)"
else
    echo "❌ 进程不存在"
fi
echo ""

# 检查日志文件
echo "📄 日志文件状态:"
if [ -f "logs/scheduler_execution.log" ]; then
    LINES=$(wc -l < logs/scheduler_execution.log)
    echo "✅ 执行日志存在 ($LINES 行)"
else
    echo "⚠️  执行日志不存在"
fi
echo ""

if [ -f "logs/scheduler_health.json" ]; then
    echo "✅ 健康检查数据存在"
    echo ""
    echo "📊 健康检查数据:"
    python3 -c "
import json
try:
    with open('logs/scheduler_health.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    print(f'   最后检查: {data.get(\"last_check\", \"无\")}')
    print(f'   调度器运行中: {data.get(\"scheduler_running\", False)}')
    print(f'   调度器中的任务: {data.get(\"jobs_in_scheduler\", [])}')
    if data.get('jobs'):
        print(f'   任务历史: {len(data[\"jobs\"])} 个任务有执行记录')
        for job_id, info in data['jobs'].items():
            last_exec = info.get('last_execution', '从未执行')
            success_count = info.get('total_executions', 0) - info.get('total_failures', 0)
            fail_count = info.get('total_failures', 0)
            print(f'      {job_id}: 最后执行 {last_exec}, 成功 {success_count} 次, 失败 {fail_count} 次')
except Exception as e:
    print(f'   读取失败: {e}')
"
else
    echo "⚠️  健康检查数据不存在"
fi
echo ""

# 检查最近的执行记录
echo "📝 最近的任务执行记录:"
if [ -f "logs/scheduler_execution.log" ]; then
    echo "   成功的任务:"
    grep "✅" logs/scheduler_execution.log | tail -5 | sed 's/^/      /'
    echo ""
    echo "   失败的任务:"
    grep "❌" logs/scheduler_execution.log | tail -5 | sed 's/^/      /'
fi
echo ""

# 检查是否有错误
echo "🚨 错误检查:"
ERROR_COUNT=0
if [ -f "logs/scheduler_execution.log" ]; then
    ERROR_COUNT=$(grep '\[ERROR\]' logs/scheduler_execution.log | wc -l | tr -d ' ')
fi

if [ "$ERROR_COUNT" = "0" ]; then
    echo "✅ 没有发现错误"
else
    echo "⚠️  发现 $ERROR_COUNT 个错误"
    echo ""
    echo "   最近的错误:"
    grep '\[ERROR\]' logs/scheduler_execution.log | tail -3 | sed 's/^/      /'
fi
echo ""

# 总结
echo "============================================================"
echo "📋 总结"
echo "============================================================"
if [ -f "logs/scheduler_health.json" ]; then
    python3 << 'PYTHON_EOF'
import json
from datetime import datetime
try:
    with open('logs/scheduler_health.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    jobs = data.get('jobs_in_scheduler', [])
    expected_jobs = ['news_su', 'wellness_su', 'review_su']
    missing = set(expected_jobs) - set(jobs)

    if missing:
        print('⚠️  警告: 发现丢失的任务: ' + ', '.join(missing))
    else:
        print('✅ 所有预期任务都已加载')

    # 检查是否有任务长时间未执行
    last_check = data.get('last_check', '')
    if last_check:
        check_time = datetime.fromisoformat(last_check)
        hours_ago = (datetime.now() - check_time).total_seconds() / 3600
        if hours_ago > 24:
            print('⚠️  警告: 健康检查数据超过 ' + str(int(hours_ago)) + ' 小时未更新')
        else:
            print('✅ 健康检查数据正常 (' + str(int(hours_ago)) + ' 小时前更新)')
except Exception as e:
    print('⚠️  无法分析健康数据: ' + str(e))
PYTHON_EOF
fi

echo "============================================================"
