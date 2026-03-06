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
            # 使用权重新闻获取器（优先级和热点）
            from scripts.fetch_news_weighted import WeightedNewsFetcher
            fetcher = WeightedNewsFetcher()
            news_items = fetcher.fetch_daily_news(max_news=10)

        return news_items

    def create_briefing(self, news_items: List[Dict[str, str]]) -> str:
        """创建新闻简报"""
        today = datetime.now()
        date_str = today.strftime('%Y-%m-%d')
        weekday_str = today.strftime('%A')

        # 优先用模型把新闻"整理 + 归纳 + 输出可直接发飞书的 Markdown"
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
                "你是资讯su，请把下面的新闻条目整理成一份精美的中文 Markdown 简报。\n"
                "要求：\n"
                "1) 标题为\"# 📰 今日新闻简报\"，副标题使用日期（如 *2026年3月6日 星期五*）\n"
                "2) 开头添加一个简短的导语，说明今日新闻概况和热点领域\n"
                "3) 添加一个\"🔥 今日热点\"部分，精选 3-5 条最重要的新闻（考虑来源权重和相关性）\n"
                "4) 按照以下分类整理新闻（使用对应的emoji）：\n"
                "   🤖 AI前沿 - AI垂直媒体和研究机构新闻\n"
                "   📰 AI日报 - AI日报类媒体精选\n"
                "   📱 科技媒体 - 科技媒体深度报道\n"
                "   🌍 国际科技 - 国际科技媒体新闻\n"
                "   🏢 行业资讯 - 产业动态和商业新闻\n"
                "   🔬 科学研究 - 科研机构和技术创新\n"
                "5) 每条新闻格式：\n"
                "   - 使用 ## 类标题\n"
                "   - 标题前添加emoji（根据类别）\n"
                "   - 新闻标题使用超链接格式：[标题](原始URL)\n"
                "   - 标题下方显示来源和权重（如 *来源：OpenAI | 权重：3.0*）\n"
                "   - 内容用简洁的语言描述，突出重点\n"
                "6) 优先显示高权重新闻（权重>=2.0）\n"
                "7) 结尾添加权重统计和生成时间\n"
                "8) 语言风格：专业但不失活泼，适合职场人士阅读\n"
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
        briefing = f"""# 📰 今日新闻简报

***{date_str} {weekday_str}***

📱 今日共收录 {len(news_items)} 条重要新闻，涵盖 AI、科技、行业动态等

## 🔥 今日热点

"""

        # 使用权重信息进行分类
        categorized_news = {
            '🤖 AI前沿': [],
            '📰 AI日报': [],
            '💬 Reddit热议': [],
            '📱 科技媒体': [],
            '🌍 国际科技': [],
            '🏢 行业资讯': [],
            '🔬 科学研究': []
        }

        for item in news_items:
            category = item.get('_category', '🔬 科学研究')
            if category in categorized_news:
                categorized_news[category].append(item)

        # 按分类添加新闻，优先显示有内容的分类
        for category, items in categorized_news.items():
            if items:
                briefing += f"\n## {category}\n\n"
                for i, item in enumerate(items[:3], 1):  # 每个分类最多3条
                    title = item.get('title', '')
                    url = item.get('url', '')
                    weight = item.get('_weight', 1.0)
                    source = item.get('source', '未知来源')
                    summary = item.get('summary', '')

                    # 添加超链接到新闻标题
                    if url and url.startswith('http'):
                        linked_title = f"[{title}]({url})"
                    else:
                        linked_title = title

                    briefing += f"### {i}. **{linked_title}**\n"
                    if summary:
                        if len(summary) > 200:
                            summary = summary[:200] + "..."
                        briefing += f"{summary}\n"
                    briefing += f"*来源：{source} | 权重：{weight}*\n\n"

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

        # 使用新的卡片消息格式（支持超链接）
        success = client.send_news_briefing(news_items, date_str)
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