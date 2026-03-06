#!/usr/bin/env python3
"""
任务调度器守护进程版本
使用 BackgroundScheduler 在后台运行
"""

import os
import sys
import signal
import time
from pathlib import Path
from datetime import datetime
from typing import Optional

try:
    from apscheduler.schedulers.background import BackgroundScheduler
    from apscheduler.triggers.cron import CronTrigger
    from apscheduler.events import EVENT_JOB_EXECUTED, EVENT_JOB_ERROR
    APSCHEDULER_AVAILABLE = True
except ImportError:
    APSCHEDULER_AVAILABLE = False

# 添加项目根目录到 Python 路径
PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))

class CCSchedulerDaemon:
    """CC Agent 任务调度器守护进程"""

    def __init__(self):
        if not APSCHEDULER_AVAILABLE:
            raise ImportError("APScheduler 未安装，请运行: pip3 install apscheduler")

        self.scheduler = BackgroundScheduler()
        self.running = False

        # 设置信号处理
        signal.signal(signal.SIGTERM, self._signal_handler)
        signal.signal(signal.SIGINT, self._signal_handler)

    def _signal_handler(self, signum, frame):
        """处理退出信号"""
        print(f"\n收到信号 {signum}，正在停止调度器...")
        self.stop()

    def _job_executed(self, event):
        """任务执行成功回调"""
        print(f"✅ 任务执行成功: {event.job_id}")

    def _job_error(self, event):
        """任务执行失败回调"""
        print(f"❌ 任务执行失败: {event.job_id} - {event.exception}")

    def setup_scheduler(self):
        """设置调度器"""
        try:
            import yaml
            from news_agent import NewsAgent
            from wellness_agent import WellnessAgent
            from review_agent import ReviewAgent

            # 加载配置
            config_path = PROJECT_ROOT / "config" / "config.yaml"
            if config_path.exists():
                with open(config_path, 'r', encoding='utf-8') as f:
                    config = yaml.safe_load(f)
            else:
                config = {}

            # 设置时区
            from apscheduler.schedulers.base import BaseScheduler
            BaseScheduler.timezone = 'Asia/Shanghai'

            # 注册事件监听器
            self.scheduler.add_listener(self._job_executed, EVENT_JOB_EXECUTED)
            self.scheduler.add_listener(self._job_error, EVENT_JOB_ERROR)

            # 配置 news-su
            news_config = config.get('scheduling', {}).get('news_su', {})
            if news_config.get('enabled', True):
                time_str = news_config.get('time', '08:00')
                hour, minute = map(int, time_str.split(':'))

                def run_news():
                    agent = NewsAgent()
                    agent.run()

                self.scheduler.add_job(
                    func=run_news,
                    trigger=CronTrigger(hour=hour, minute=minute, timezone='Asia/Shanghai'),
                    id='news_su',
                    name='每日新闻'
                )

            # 配置 wellness-su
            wellness_config = config.get('scheduling', {}).get('wellness_su', {})
            if wellness_config.get('enabled', True):
                time_str = wellness_config.get('time', '08:30')
                hour, minute = map(int, time_str.split(':'))

                def run_wellness():
                    agent = WellnessAgent()
                    agent.run()

                self.scheduler.add_job(
                    func=run_wellness,
                    trigger=CronTrigger(hour=hour, minute=minute, timezone='Asia/Shanghai'),
                    id='wellness_su',
                    name='健康提醒'
                )

            # 配置 review-su
            review_config = config.get('scheduling', {}).get('review_su', {})
            if review_config.get('enabled', True):
                time_str = review_config.get('time', '20:00')
                hour, minute = map(int, time_str.split(':'))

                def run_review():
                    agent = ReviewAgent()
                    agent.run()

                self.scheduler.add_job(
                    func=run_review,
                    trigger=CronTrigger(hour=hour, minute=minute, timezone='Asia/Shanghai'),
                    id='review_su',
                    name='晚间回顾'
                )

            return True

        except Exception as e:
            print(f"❌ 设置调度器失败: {e}")
            return False

    def start(self):
        """启动调度器"""
        if not self.setup_scheduler():
            return False

        print("🚀 CC Agent 调度器启动")
        print("=" * 60)
        print(f"启动时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"时区: Asia/Shanghai")
        print("=" * 60)

        # 显示配置的任务
        jobs = self.scheduler.get_jobs()
        if jobs:
            print("\n📋 已配置任务:")
            for job in jobs:
                print(f"   {job.id} - {job.name} ({job.trigger})")
        else:
            print("⚠️ 没有配置任何任务")

        print("\n✅ 调度器已启动，等待任务执行...")
        print("按 Ctrl+C 停止\n")

        self.running = True
        self.scheduler.start()

        # 保持运行
        try:
            while self.running:
                time.sleep(1)
        except KeyboardInterrupt:
            self.stop()

        return True

    def stop(self):
        """停止调度器"""
        if self.running:
            self.running = False
            self.scheduler.shutdown(wait=True)
            print("\n🛑 调度器已停止")

    def status(self) -> dict:
        """获取调度器状态"""
        return {
            'running': self.running,
            'jobs_count': len(self.scheduler.get_jobs()) if self.scheduler else 0
        }

if __name__ == "__main__":
    if not APSCHEDULER_AVAILABLE:
        print("❌ APScheduler 未安装")
        print("请运行: pip3 install apscheduler")
        sys.exit(1)

    # 设置并启动调度器
    scheduler_daemon = CCSchedulerDaemon()

    if scheduler_daemon.start():
        print("\n✅ 调度器守护进程运行完成")
    else:
        print("\n❌ 调度器启动失败")
        sys.exit(1)