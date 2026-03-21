#!/usr/bin/env python3
"""
任务调度器
使用 APScheduler 管理定时任务
"""

import os
import sys
from pathlib import Path
from datetime import datetime
from typing import Callable

try:
    from apscheduler.schedulers.blocking import BlockingScheduler
    from apscheduler.triggers.cron import CronTrigger
    from apscheduler.events import EVENT_JOB_EXECUTED, EVENT_JOB_ERROR
    APSCHEDULER_AVAILABLE = True
except ImportError:
    APSCHEDULER_AVAILABLE = False

# 添加项目根目录到 Python 路径
PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))

class CCScheduler:
    """CC Agent 任务调度器"""

    def __init__(self):
        if not APSCHEDULER_AVAILABLE:
            raise ImportError(
                "APScheduler 未安装。请运行: pip3 install apscheduler"
            )

        self.scheduler = BlockingScheduler()
        self.jobs = {}

    def add_daily_job(
        self,
        job_id: str,
        func: Callable,
        hour: int,
        minute: int,
        timezone: str = "Asia/Shanghai"
    ):
        """添加每日定时任务"""
        trigger = CronTrigger(
            hour=hour,
            minute=minute,
            timezone=timezone
        )

        self.scheduler.add_job(
            func=func,
            trigger=trigger,
            id=job_id,
            name=f"{job_id} - 每日 {hour:02d}:{minute:02d}",
            misfire_grace_time=3600,  # 允许错过1小时内仍执行
            coalesce=False  # 不合并错过的执行
        )

        self.jobs[job_id] = {
            "hour": hour,
            "minute": minute,
            "timezone": timezone,
            "enabled": True
        }

        print(f"✅ 任务已添加: {job_id} (每天 {hour:02d}:{minute:02d} {timezone})")

    def remove_job(self, job_id: str):
        """移除任务"""
        if job_id in self.jobs:
            self.scheduler.remove_job(job_id)
            del self.jobs[job_id]
            print(f"❌ 任务已移除: {job_id}")
        else:
            print(f"⚠️ 任务不存在: {job_id}")

    def list_jobs(self):
        """列出所有任务"""
        print("\n" + "=" * 60)
        print("⏰ 定时任务列表")
        print("=" * 60)

        if not self.jobs:
            print("\n❌ 未配置任何定时任务")
            return

        for job_id, job_info in self.jobs.items():
            status = "✅ 已启用" if job_info.get("enabled") else "❌ 已禁用"
            print(f"\n📋 {job_id}")
            print(f"   时间: {job_info['hour']:02d}:{job_info['minute']:02d}")
            print(f"   时区: {job_info['timezone']}")
            print(f"   状态: {status}")

        print("\n" + "=" * 60)

    def start(self):
        """启动调度器"""
        print("\n" + "=" * 60)
        print("🚀 CC Agent 调度器启动")
        print("=" * 60)
        print(f"\n启动时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"已配置任务: {len(self.jobs)} 个\n")

        try:
            self.scheduler.start()
        except KeyboardInterrupt:
            print("\n\n👋 调度器已停止")
            self.scheduler.shutdown()

    def stop(self):
        """停止调度器"""
        self.scheduler.shutdown()

def load_config():
    """加载配置"""
    import yaml

    config_path = PROJECT_ROOT / "config" / "config.yaml"
    if not config_path.exists():
        return None

    with open(config_path, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)

    return config

def setup_scheduler():
    """设置并启动调度器"""
    config = load_config()

    if not config or not config.get('scheduling', {}).get('enabled'):
        print("⚠️ 定时任务未启用")
        print("请先配置 config.yaml 中的 scheduling.enabled = True")
        print("或运行: python3 configure.py --enable-scheduling")
        return None

    # 获取时区配置
    timezone = config.get('scheduling', {}).get('timezone', 'Asia/Shanghai')
    print(f"🌍 使用时区: {timezone} (UTC+8)")

    # 创建调度器
    scheduler = CCScheduler()

    # 导入 agents
    from news_agent import NewsAgent
    from wellness_agent import WellnessAgent
    from review_agent import ReviewAgent

    # 配置 news-su
    news_config = config.get('scheduling', {}).get('news_su', {})
    if news_config.get('enabled'):
        time_str = news_config.get('time', '08:00')
        hour, minute = map(int, time_str.split(':'))

        def run_news():
            agent = NewsAgent()
            agent.run()

        scheduler.add_daily_job(
            job_id='news_su',
            func=run_news,
            hour=hour,
            minute=minute,
            timezone=timezone
        )

    # 配置 wellness-su
    wellness_config = config.get('scheduling', {}).get('wellness_su', {})
    if wellness_config.get('enabled'):
        time_str = wellness_config.get('time', '08:30')
        hour, minute = map(int, time_str.split(':'))

        def run_wellness():
            agent = WellnessAgent()
            agent.run()

        scheduler.add_daily_job(
            job_id='wellness_su',
            func=run_wellness,
            hour=hour,
            minute=minute,
            timezone=timezone
        )

    # 配置 review-su
    review_config = config.get('scheduling', {}).get('review_su', {})
    if review_config.get('enabled'):
        time_str = review_config.get('time', '20:00')
        hour, minute = map(int, time_str.split(':'))

        def run_review():
            agent = ReviewAgent()
            agent.run()

        scheduler.add_daily_job(
            job_id='review_su',
            func=run_review,
            hour=hour,
            minute=minute,
            timezone=timezone
        )

    return scheduler

if __name__ == "__main__":
    if not APSCHEDULER_AVAILABLE:
        print("❌ APScheduler 未安装")
        print("请运行: pip3 install apscheduler")
        sys.exit(1)

    # 设置并启动调度器
    scheduler = setup_scheduler()

    if scheduler:
        scheduler.list_jobs()
        scheduler.start()
