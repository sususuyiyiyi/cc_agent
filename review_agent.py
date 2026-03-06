#!/usr/bin/env python3
"""
复盘su - 每日复盘 Agent
"""

import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, Any

# 添加项目根目录到 Python 路径
PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))

from feishu_client import FeishuClient

class ReviewAgent:
    """复盘 Agent"""

    def __init__(self):
        self.config = self._load_config()
        self.data_dir = PROJECT_ROOT / "data" / "reviews"

    def _load_config(self) -> Dict[str, Any]:
        """加载配置"""
        import yaml

        config_path = PROJECT_ROOT / "config" / "config.yaml"
        if config_path.exists():
            with open(config_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        return {}

    def greet_user(self):
        """问候用户"""
        print("\n晚上好！🌙")
        print("让我们来回顾今天...")

    def collect_activities(self) -> list:
        """收集用户的活动"""
        print("\n今天都做了什么呢？")
        print("(请输入您今天做的事情，完成后输入 '完成' 或 'done' 继续)")

        activities = []
        try:
            while True:
                user_input = input("\n> ").strip()
                if user_input.lower() in ['完成', 'done', 'exit', 'quit']:
                    break
                if user_input:
                    activities.append(user_input)
        except (KeyboardInterrupt, EOFError):
            print("\n\n已取消输入")
            return []

        return activities

    def collect_reflections(self) -> str:
        """收集用户的心得和感悟"""
        print("\n今天有什么心得或感悟吗？")
        print("(直接输入您的想法，完成后输入 '完成' 或 'done' 继续)")

        reflections = []
        try:
            while True:
                user_input = input("\n> ").strip()
                if user_input.lower() in ['完成', 'done', 'exit', 'quit']:
                    break
                if user_input:
                    reflections.append(user_input)
        except (KeyboardInterrupt, EOFError):
            pass

        return "\n\n".join(reflections) if reflections else ""

    def collect_plans(self) -> list:
        """收集明天的计划"""
        print("\n明天有什么计划吗？")
        print("(输入您的计划，完成后输入 '完成' 或 'done' 继续)")

        plans = []
        try:
            while True:
                user_input = input("\n> ").strip()
                if user_input.lower() in ['完成', 'done', 'exit', 'quit']:
                    break
                if user_input:
                    plans.append(user_input)
        except (KeyboardInterrupt, EOFError):
            pass

        return plans

    def create_report(self, activities: list, reflections: str, plans: list) -> str:
        """创建日报"""
        today = datetime.now()
        date_str = today.strftime('%Y-%m-%d')

        report = f"""# 日报
**日期**: {date_str}

## 今日完成事项
"""

        if activities:
            for i, activity in enumerate(activities, 1):
                report += f"{i}. {activity}\n"
        else:
            report += "暂无活动记录\n"

        report += "\n## 心得/感悟\n"
        if reflections:
            report += reflections
        else:
            report += "暂无心得记录\n"

        report += "\n## 明日计划\n"
        if plans:
            for i, plan in enumerate(plans, 1):
                report += f"{i}. {plan}\n"
        else:
            report += "暂无计划\n"

        report += f"""
---
*生成时间: {datetime.now().strftime('%H:%M:%S')}*
"""

        return report

    def save_report(self, report: str):
        """保存日报"""
        today = datetime.now()
        report_dir = self.data_dir / str(today.year) / f"{today.month:02d}" / f"{today.day:02d}"
        report_dir.mkdir(parents=True, exist_ok=True)

        report_file = report_dir / "日报.md"
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report)

        print(f"✅ 日报已保存到: {report_file}")
        return report_file

    def send_to_feishu(self, report: str):
        """发送到飞书"""
        if not self.config.get('feishu', {}).get('enabled'):
            print("⚠️ 飞书未配置，跳过发送")
            return

        if not self.config.get('feishu', {}).get('message', {}).get('review_enabled'):
            print("⚠️ 日报消息发送未启用，跳过发送")
            return

        webhook_url = self.config.get('feishu', {}).get('webhook_url')
        if not webhook_url:
            print("⚠️ 飞书 Webhook URL 未配置")
            return

        print("\n📤 发送到飞书...")
        client = FeishuClient(webhook_url)

        today = datetime.now()
        date_str = today.strftime('%Y-%m-%d')

        # 发送富文本消息
        title = f"📝 今日日报 - {date_str}"

        content = [
            [
                {
                    "tag": "text",
                    "text": report
                }
            ]
        ]

        success = client.send_post(title, content)
        if success:
            print("✅ 已发送到飞书")
        else:
            print("❌ 发送到飞书失败")

    def run(self):
        """运行完整的复盘流程"""
        print("\n" + "=" * 60)
        print("📝 复盘su - 开始工作")
        print("=" * 60)

        # 1. 问候用户
        self.greet_user()

        # 2. 收集信息
        activities = self.collect_activities()
        reflections = self.collect_reflections()
        plans = self.collect_plans()

        # 3. 创建日报
        print("\n📊 正在生成日报...")
        report = self.create_report(activities, reflections, plans)

        print("\n📄 日报:")
        print(report)

        # 4. 保存日报
        self.save_report(report)

        # 5. 发送到飞书
        self.send_to_feishu(report)

        print("\n" + "=" * 60)
        print("✅ 复盘su - 工作完成")
        print("=" * 60)

if __name__ == "__main__":
    agent = ReviewAgent()
    agent.run()
