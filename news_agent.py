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

        # 优先用模型把新闻“整理 + 归纳 + 输出可直接发飞书的 Markdown”
        try:
            from llm_client import anthropic_messages_create

            # 限制输入长度，避免 payload 过大
            compact_items = []
            for item in news_items[:12]:
                compact_items.append(
                    {
                        "title": (item.get("title") or "").strip(),
                        "snippet": (item.get("summary") or item.get("snippet") or "").strip()[:300],
                        "source": (item.get("source") or "").strip(),
                        "url": (item.get("url") or "").strip(),
                        "source_type": (item.get("source_type") or "").strip(),
                        "subreddit": (item.get("subreddit") or "").strip(),
                        "score": item.get("score", 0),
                    }
                )

            user_prompt = (
                "你是“资讯su”，请把下面的新闻条目整理成一份中文 Markdown 简报。\n"
                "要求：\n"
                "1) 标题为“# 今日新闻简报”，包含日期\n"
                "2) 先给出 3 条“今日要点”（用项目符号）\n"
                "3) 再按条目列出新闻（最多 10 条），每条包含：标题、1-2 句摘要、来源（如有 URL 则附上）\n"
                "4) 摘要要客观，不要编造不存在的信息；如果信息不足就写“细节待确认”。\n"
                f"日期：{date_str}\n\n"
                f"新闻条目(JSON)：{compact_items}\n"
            )

            briefing = anthropic_messages_create(
                system="输出必须是 Markdown；语言为简体中文；不要输出代码块围栏。",
                user=user_prompt,
                max_tokens=1400,
                temperature=0.2,
            )

            # 兜底：确保包含生成时间与统计
            briefing = briefing.strip()
            if "---" not in briefing:
                briefing += "\n\n---\n"
            briefing += f"*生成时间: {datetime.now().strftime('%H:%M:%S')}*\n"
            briefing += f"*共 {len(news_items)} 条新闻（输入 {min(len(news_items), 12)} 条给模型）*\n"
            return briefing
        except Exception as e:
            print(f"⚠️ 模型生成简报失败，改用本地模板：{e}")

        # 本地模板（无模型/模型失败时）
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
                if len(summary) > 200:
                    summary = summary[:200] + "..."
                briefing += f"{summary}\n"

            if source_type == 'reddit':
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
