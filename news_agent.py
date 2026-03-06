#!/usr/bin/env python3
"""
资讯su - 每日新闻简报 Agent
"""

import sys
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any

# 添加项目根目录到 Python 路径
PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))

from feishu_client import FeishuClient, load_config

class NewsAgent:
    """资讯 Agent"""

    def __init__(self):
        self.config = self._load_config()
        self.data_dir = PROJECT_ROOT / "data" / "news"

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
        print("\n早上好！☀️")
        print("让我为您获取今天的新闻...")

    def fetch_news(self) -> List[Dict[str, str]]:
        """获取新闻"""
        # 检查是否使用聚合器
        use_aggregator = self.config.get('preferences', {}).get('news', {}).get('use_aggregator', False)

        if use_aggregator:
            # 使用新闻聚合器（支持多个源）
            from scripts.news_aggregator import NewsAggregator
            aggregator = NewsAggregator()
            news_items = aggregator.fetch_daily_news(max_news=10)
        else:
            # 使用单一新闻源（中文网站）
            from scripts.fetch_news_api import RealNewsFetcher
            fetcher = RealNewsFetcher()
            news_items = fetcher.fetch_daily_news(max_news=10)

        return news_items

    def create_briefing(self, news_items: List[Dict[str, str]]) -> str:
        """创建新闻简报"""
        today = datetime.now()
        date_str = today.strftime('%Y-%m-%d')

        briefing = f"""# 今日新闻简报
**日期**: {date_str}

## 科技资讯
"""

        for i, item in enumerate(news_items, 1):
            title = item.get('title', '')
            summary = item.get('summary', item.get('snippet', ''))
            source = item.get('source', '未知来源')
            source_type = item.get('source_type', '')

            briefing += f"\n### {i}. {title}\n"

            if summary:
                # 限制摘要长度
                if len(summary) > 200:
                    summary = summary[:200] + "..."
                briefing += f"{summary}\n"

            if source_type == 'reddit':
                # Reddit 新闻显示 subreddit 信息
                subreddit = item.get('subreddit', '')
                score = item.get('score', 0)
                briefing += f"📍 r/{subreddit} | ⬆️ {score}\n"
            elif source:
                briefing += f"📍 {source}\n"

            briefing += "\n"

        briefing += f"""
---
*生成时间: {datetime.now().strftime('%H:%M:%S')}*
*共 {len(news_items)} 条新闻*
"""

        return briefing

    def save_briefing(self, briefing: str):
        """保存新闻简报"""
        today = datetime.now()
        news_dir = self.data_dir / str(today.year) / f"{today.month:02d}" / f"{today.day:02d}"
        news_dir.mkdir(parents=True, exist_ok=True)

        news_file = news_dir / "今日新闻.md"
        with open(news_file, 'w', encoding='utf-8') as f:
            f.write(briefing)

        print(f"✅ 新闻简报已保存到: {news_file}")
        return news_file

    def send_to_feishu(self, briefing: str, news_items: List[Dict[str, str]]):
        """发送到飞书"""
        if not self.config.get('feishu', {}).get('enabled'):
            print("⚠️ 飞书未配置，跳过发送")
            return

        if not self.config.get('feishu', {}).get('message', {}).get('news_enabled'):
            print("⚠️ 新闻消息发送未启用，跳过发送")
            return

        webhook_url = self.config.get('feishu', {}).get('webhook_url')
        if not webhook_url:
            print("⚠️ 飞书 Webhook URL 未配置")
            return

        print("\n📤 发送到飞书...")
        client = FeishuClient(webhook_url)

        today = datetime.now()
        date_str = today.strftime('%Y-%m-%d')

        # 构建飞书消息内容
        title = f"📰 今日新闻简报 - {date_str}"

        content = [[{"tag": "text", "text": "科技资讯"}]]

        for item in news_items:
            title_text = item.get('title', '')
            source_type = item.get('source_type', '')

            if source_type == 'reddit':
                # Reddit 新闻格式
                subreddit = item.get('subreddit', '')
                score = item.get('score', 0)
                comments = item.get('num_comments', 0)

                content.append([
                    {"tag": "text", "text": f"\n• {title_text}"}
                ])
                content.append([
                    {"tag": "text", "text": f"  📍 r/{subreddit} | ⬆️ {score} | 💬 {comments}"}
                ])
            else:
                # 中文新闻格式
                source_text = item.get('source', '')
                snippet_text = item.get('snippet', '')

                content.append([
                    {"tag": "text", "text": f"\n• {title_text}"}
                ])

                if snippet_text and len(snippet_text) > 10:
                    snippet_short = snippet_text[:150] + "..." if len(snippet_text) > 150 else snippet_text
                    content.append([
                        {"tag": "text", "text": f"  {snippet_short}"}
                    ])

                if source_text:
                    content.append([
                        {"tag": "text", "text": f"  📍 {source_text}"}
                    ])

        success = client.send_post(title, content)
        if success:
            print("✅ 已发送到飞书")
        else:
            print("❌ 发送到飞书失败")

    def run(self):
        """运行完整的新闻简报流程"""
        print("\n" + "=" * 60)
        print("📰 资讯su - 开始工作")
        print("=" * 60)

        # 1. 问候用户
        self.greet_user()

        # 2. 获取新闻
        news_items = self.fetch_news()
        print(f"\n📋 获取到 {len(news_items)} 条新闻")

        # 3. 创建简报
        briefing = self.create_briefing(news_items)

        print("\n📄 新闻简报:")
        print(briefing)

        # 4. 保存简报
        self.save_briefing(briefing)

        # 5. 发送到飞书
        self.send_to_feishu(briefing, news_items)

        print("\n" + "=" * 60)
        print("✅ 资讯su - 工作完成")
        print("=" * 60)

if __name__ == "__main__":
    agent = NewsAgent()
    agent.run()
