#!/usr/bin/env python3
"""
任务调度器守护进程版本
使用 BackgroundScheduler 在后台运行
"""

import os
import sys
import signal
import time
import json
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, List

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

        # 日志文件路径
        self.log_dir = PROJECT_ROOT / "logs"
        self.log_dir.mkdir(exist_ok=True)
        self.execution_log = self.log_dir / "scheduler_execution.log"
        self.health_check_file = self.log_dir / "scheduler_health.json"

        # 期望的任务列表
        self.expected_jobs = ['news_su', 'wellness_su', 'review_su']

        # 任务执行记录
        self.job_history: Dict[str, Dict] = {}

    def _signal_handler(self, signum, frame):
        """处理退出信号"""
        self._log_message(f"收到信号 {signum}，正在停止调度器...")
        print(f"\n收到信号 {signum}，正在停止调度器...")
        self.stop()

    def _log_message(self, message: str, level: str = "INFO"):
        """记录日志到文件"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        log_entry = f"[{timestamp}] [{level}] {message}\n"

        # 打印到控制台
        print(message)

        # 写入日志文件
        try:
            with open(self.execution_log, 'a', encoding='utf-8') as f:
                f.write(log_entry)
        except Exception as e:
            print(f"⚠️ 写入日志失败: {e}")

    def _log_job_execution(self, job_id: str, success: bool, error: Optional[str] = None):
        """记录任务执行情况"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        # 更新任务历史
        self.job_history[job_id] = {
            'last_execution': timestamp,
            'last_success': success,
            'last_error': error,
            'total_executions': self.job_history.get(job_id, {}).get('total_executions', 0) + 1,
            'total_failures': self.job_history.get(job_id, {}).get('total_failures', 0) + (0 if success else 1)
        }

        # 写入执行日志
        status = "✅ 成功" if success else "❌ 失败"
        log_message = f"任务 {job_id} {status} - {timestamp}"
        if error:
            log_message += f"\n   错误信息: {error}"

        self._log_message(log_message, "INFO" if success else "ERROR")

        # 保存健康检查数据
        self._save_health_check()

    def _send_feishu_notification(self, title: str, content: str, urgent: bool = False):
        """发送飞书通知"""
        try:
            from feishu_client import FeishuClient

            # 加载配置
            import yaml
            config_path = PROJECT_ROOT / "config" / "config.yaml"
            if not config_path.exists():
                return False

            with open(config_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)

            if not config.get('feishu', {}).get('enabled'):
                return False

            # 创建飞书客户端
            webhook_url = config['feishu'].get('webhook_url')
            if not webhook_url:
                return False

            client = FeishuClient(webhook_url)

            # 构建消息内容
            emoji = "🚨" if urgent else "⚠️"
            message = f"{emoji} **{title}**\n\n{content}"

            # 发送消息
            client.send_card_message(title, message)
            self._log_message(f"已发送飞书通知: {title}")
            return True

        except Exception as e:
            self._log_message(f"发送飞书通知失败: {e}", "ERROR")
            return False

    def _save_health_check(self):
        """保存健康检查数据"""
        health_data = {
            'last_check': datetime.now().isoformat(),
            'jobs': self.job_history.copy(),
            'scheduler_running': self.running,
            'jobs_in_scheduler': [job.id for job in self.scheduler.get_jobs()] if self.scheduler else []
        }

        try:
            with open(self.health_check_file, 'w', encoding='utf-8') as f:
                json.dump(health_data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            self._log_message(f"保存健康检查数据失败: {e}", "ERROR")

    def _perform_health_check(self):
        """执行健康检查"""
        try:
            # 检查是否有任务丢失
            current_jobs = {job.id for job in self.scheduler.get_jobs()}
            missing_jobs = set(self.expected_jobs) - current_jobs

            if missing_jobs:
                error_msg = f"⚠️ 健康检查警告：发现丢失的任务: {', '.join(missing_jobs)}"
                self._log_message(error_msg, "WARNING")
                self._send_feishu_notification("调度器健康检查警告", error_msg, urgent=True)
                return False

            # 检查是否有长时间未执行的任务
            now = datetime.now()
            for job_id in self.expected_jobs:
                if job_id in self.job_history:
                    last_exec = self.job_history[job_id].get('last_execution')
                    if last_exec:
                        last_exec_time = datetime.strptime(last_exec, '%Y-%m-%d %H:%M:%S')
                        hours_since = (now - last_exec_time).total_seconds() / 3600

                        # 如果超过36小时没有执行（最多错过1天）
                        if hours_since > 36:
                            warning_msg = f"⚠️ 任务 {job_id} 已超过 {int(hours_since)} 小时未执行"
                            self._log_message(warning_msg, "WARNING")
                            self._send_feishu_notification(f"任务 {job_id} 未执行警告", warning_msg)

            return True

        except Exception as e:
            self._log_message(f"健康检查失败: {e}", "ERROR")
            return False

    def _job_executed(self, event):
        """任务执行成功回调"""
        job_name = {
            'news_su': '每日新闻',
            'wellness_su': '健康提醒',
            'review_su': '晚间回顾'
        }.get(event.job_id, event.job_id)

        self._log_job_execution(event.job_id, True)
        print(f"✅ 任务执行成功: {job_name} ({event.job_id})")

    def _job_error(self, event):
        """任务执行失败回调"""
        error_msg = str(event.exception) if event.exception else "未知错误"
        job_name = {
            'news_su': '每日新闻',
            'wellness_su': '健康提醒',
            'review_su': '晚间回顾'
        }.get(event.job_id, event.job_id)

        self._log_job_execution(event.job_id, False, error_msg)
        print(f"❌ 任务执行失败: {job_name} - {error_msg}")

        # 发送飞书通知
        notification_msg = f"任务: {job_name}\n错误: {error_msg}\n时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        self._send_feishu_notification("任务执行失败通知", notification_msg, urgent=True)

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
                    try:
                        agent = NewsAgent()
                        agent.run()
                    except Exception as e:
                        self._log_message(f"NewsAgent 执行异常: {e}", "ERROR")
                        raise

                self.scheduler.add_job(
                    func=run_news,
                    trigger=CronTrigger(hour=hour, minute=minute, timezone='Asia/Shanghai'),
                    id='news_su',
                    name='每日新闻',
                    misfire_grace_time=300,  # 5 分钟的错过执行宽容时间
                    coalesce=True,  # 合并错过的执行
                    max_instances=1  # 只允许一个实例
                )
                self._log_message(f"✅ 任务已添加: news_su (每天 {hour:02d}:{minute:02d} Asia/Shanghai)")

            # 配置 wellness-su
            wellness_config = config.get('scheduling', {}).get('wellness_su', {})
            if wellness_config.get('enabled', True):
                time_str = wellness_config.get('time', '08:30')
                hour, minute = map(int, time_str.split(':'))

                def run_wellness():
                    try:
                        agent = WellnessAgent()
                        agent.run()
                    except Exception as e:
                        self._log_message(f"WellnessAgent 执行异常: {e}", "ERROR")
                        raise

                self.scheduler.add_job(
                    func=run_wellness,
                    trigger=CronTrigger(hour=hour, minute=minute, timezone='Asia/Shanghai'),
                    id='wellness_su',
                    name='健康提醒',
                    misfire_grace_time=300,
                    coalesce=True,
                    max_instances=1
                )
                self._log_message(f"✅ 任务已添加: wellness_su (每天 {hour:02d}:{minute:02d} Asia/Shanghai)")

            # 配置 review-su
            review_config = config.get('scheduling', {}).get('review_su', {})
            if review_config.get('enabled', True):
                time_str = review_config.get('time', '20:00')
                hour, minute = map(int, time_str.split(':'))

                def run_review():
                    try:
                        agent = ReviewAgent()
                        agent.run()
                    except Exception as e:
                        self._log_message(f"ReviewAgent 执行异常: {e}", "ERROR")
                        raise

                self.scheduler.add_job(
                    func=run_review,
                    trigger=CronTrigger(hour=hour, minute=minute, timezone='Asia/Shanghai'),
                    id='review_su',
                    name='晚间回顾',
                    misfire_grace_time=300,
                    coalesce=True,
                    max_instances=1
                )
                self._log_message(f"✅ 任务已添加: review_su (每天 {hour:02d}:{minute:02d} Asia/Shanghai)")

            # 保存初始健康检查数据
            self._save_health_check()

            return True

        except Exception as e:
            self._log_message(f"❌ 设置调度器失败: {e}", "ERROR")
            import traceback
            traceback.print_exc()
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