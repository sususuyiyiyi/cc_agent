#!/usr/bin/env python3
"""
测试调度器
"""

import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))

try:
    from apscheduler.schedulers.background import BackgroundScheduler
    from apscheduler.triggers.cron import CronTrigger
    from apscheduler.events import EVENT_JOB_EXECUTED, EVENT_JOB_ERROR
    APSCHEDULER_AVAILABLE = True
    print("✅ APScheduler 可用")
except ImportError as e:
    print(f"❌ APScheduler 不可用: {e}")
    APSCHEDULER_AVAILABLE = False

if __name__ == "__main__":
    if APSCHEDULER_AVAILABLE:
        # 创建调度器
        scheduler = BackgroundScheduler()
        scheduler.start()

        # 添加一个测试任务
        def test_job():
            print("🧪 测试任务执行成功")

        scheduler.add_job(
            func=test_job,
            trigger=CronTrigger(second='*/2'),  # 每2秒执行一次
            id='test_job'
        )

        print("✅ 调度器已启动")
        print("等待6秒执行测试任务...")

        import time
        time.sleep(6)

        # 停止调度器
        scheduler.shutdown(wait=True)
        print("✅ 调度器已停止")
    else:
        print("请安装 APScheduler: pip3 install apscheduler")