#!/usr/bin/env python3
"""
新闻聚合器 - 整合多个新闻源
"""
import sys
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any

# 添加项目根目录到 Python 路径
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# 导入各个新闻获取器
from scripts.fetch_news_api import RealNewsFetcher
from scripts.fetch_news_reddit_api import RedditNewsFetcher

class NewsAggregator:
    """新闻聚合器 - 整合多个新闻源"""

    def __init__(self):
        self.config = self._load_config()
        self.fetchers = {
            'chinese': RealNewsFetcher(),
            'reddit': RedditNewsFetcher()
        }

    def _load_config(self) -> Dict[str, Any]:
        """加载配置"""
        import yaml

        config_path = PROJECT_ROOT / "config" / "news_apis.yaml"
        if not config_path.exists():
            return {}

        with open(config_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)

    def fetch_from_all_sources(self) -> List[Dict[str, Any]]:
        """从所有启用的源获取新闻"""
        all_news = []

        # 中文新闻源
        print("🌐 获取中文新闻...")
        try:
            chinese_news = self.fetchers['chinese'].fetch_daily_news(max_news=5)
            for item in chinese_news:
                item['source_type'] = 'chinese'
            all_news.extend(chinese_news)
        except Exception as e:
            print(f"⚠️ 中文新闻获取失败: {e}")

        # Reddit 新闻源
        reddit_config = self.config.get('reddit', {})
        if reddit_config.get('enabled'):
            print("🔴 获取 Reddit 新闻...")
            try:
                reddit_news = self.fetchers['reddit'].fetch_daily_news(max_news=5)
                for item in reddit_news:
                    item['source_type'] = 'reddit'
                all_news.extend(reddit_news)
            except Exception as e:
                print(f"⚠️ Reddit 新闻获取失败: {e}")
        else:
            print("ℹ️ Reddit 未启用，跳过")

        return all_news

    def deduplicate_news(self, news_items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """去重新闻"""
        seen_titles = set()
        unique_news = []

        for item in news_items:
            title = item.get('title', '').strip().lower()
            if title and title not in seen_titles:
                seen_titles.add(title)
                unique_news.append(item)

        return unique_news

    def rank_news(self, news_items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """排序新闻"""
        def get_score(item):
            source_type = item.get('source_type', '')
            if source_type == 'reddit':
                # Reddit 新闻按 upvotes 和 comments 排序
                return item.get('rank_score', 0)
            else:
                # 中文新闻固定分数
                return 100

        return sorted(news_items, key=get_score, reverse=True)

    def format_news_briefing(self, news_items: List[Dict[str, Any]]) -> str:
        """格式化新闻简报"""
        today = datetime.now().strftime('%Y-%m-%d')

        briefing = f"""# 今日新闻简报
**日期**: {today}
**来源**: 多源聚合
"""

        for i, item in enumerate(news_items, 1):
            title = item.get('title', '')
            source = item.get('source', '未知来源')
            source_type = item.get('source_type', '')

            if source_type == 'reddit':
                # Reddit 新闻
                subreddit = item.get('subreddit', '')
                score = item.get('score', 0)
                comments = item.get('num_comments', 0)

                briefing += f"\n### {i}. {title}\n"
                briefing += f"📍 r/{subreddit} | ⬆️ {score} | 💬 {comments}\n"
                if item.get('snippet'):
                    briefing += f"{item['snippet'][:150]}...\n"
            else:
                # 中文新闻
                briefing += f"\n### {i}. {title}\n"
                if item.get('snippet'):
                    briefing += f"{item['snippet'][:200]}\n"
                briefing += f"📍 来源: {source}\n"

        briefing += f"""
---
*生成时间: {datetime.now().strftime('%H:%M:%S')}*
*共 {len(news_items)} 条新闻*
"""

        return briefing

    def fetch_daily_news(self, max_news: int = 10) -> List[Dict[str, Any]]:
        """获取每日新闻"""
        print("\n" + "=" * 60)
        print("📰 新闻聚合器 - 获取今日新闻")
        print("=" * 60)

        # 从所有源获取
        all_news = self.fetch_from_all_sources()

        # 去重
        unique_news = self.deduplicate_news(all_news)

        # 排序
        ranked_news = self.rank_news(unique_news)

        # 限制数量
        final_news = ranked_news[:max_news]

        print(f"✅ 获取到 {len(final_news)} 条新闻")

        # 统计来源
        source_stats = {}
        for item in final_news:
            source_type = item.get('source_type', 'unknown')
            source_stats[source_type] = source_stats.get(source_type, 0) + 1

        print(f"📊 来源统计: {source_stats}")

        return final_news

def main():
    """主函数"""
    aggregator = NewsAggregator()
    news_items = aggregator.fetch_daily_news()

    if news_items:
        briefing = aggregator.format_news_briefing(news_items)
        print("\n" + briefing)
    else:
        print("❌ 未能获取到新闻")

if __name__ == "__main__":
    main()
