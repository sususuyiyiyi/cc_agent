#!/usr/bin/env python3
"""
使用 Reddit MCP 获取新闻
"""
import sys
import json
import requests
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any
import re

# 添加项目根目录到 Python 路径
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

class RedditNewsFetcher:
    """使用 Reddit 获取新闻"""

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 CC-Agent/1.0'
        })

    def get_subreddit_posts(self, subreddit: str, limit: int = 10, sort: str = 'hot') -> List[Dict[str, Any]]:
        """
        从指定 subreddit 获取帖子

        Args:
            subreddit: 子版块名称
            limit: 获取数量
            sort: 排序方式 (hot, new, top)
        """
        try:
            url = f"https://www.reddit.com/r/{subreddit}/{sort}.json?limit={limit}"
            response = self.session.get(url, timeout=10)

            if response.status_code == 429:
                print(f"⚠️ 请求过于频繁，等待中...")
                return []

            response.raise_for_status()
            data = response.json()

            posts = []
            for post in data['data']['children'][:limit]:
                post_data = post['data']
                posts.append({
                    'title': post_data.get('title', ''),
                    'url': f"https://reddit.com{post_data.get('permalink', '')}",
                    'snippet': post_data.get('selftext', '')[:300],
                    'author': post_data.get('author', ''),
                    'score': post_data.get('score', 0),
                    'subreddit': subreddit,
                    'created': datetime.fromtimestamp(post_data.get('created', 0)).strftime('%Y-%m-%d'),
                    'num_comments': post_data.get('num_comments', 0)
                })

            return posts

        except Exception as e:
            print(f"⚠️ 获取 {subreddit} 失败: {e}")
            return []

    def fetch_ai_news(self) -> List[Dict[str, Any]]:
        """获取 AI 相关新闻"""
        all_news = []

        # AI 相关的 subreddits
        ai_subreddits = [
            ('artificial', 5),
            ('MachineLearning', 5),
            ('ArtificialIntelligence', 5),
            ('ChatGPT', 3),
            ('openai', 3),
            ('localLLaMA', 2)
        ]

        for subreddit, limit in ai_subreddits:
            print(f"🔍 获取 r/{subreddit}...")
            posts = self.get_subreddit_posts(subreddit, limit=limit)
            all_news.extend(posts)

        return all_news

    def fetch_tech_news(self) -> List[Dict[str, Any]]:
        """获取科技新闻"""
        all_news = []

        # 科技相关的 subreddits
        tech_subreddits = [
            ('technology', 5),
            ('programming', 3),
            ('compsci', 2),
            ('Python', 2),
            ('MachineLearning', 3)
        ]

        for subreddit, limit in tech_subreddits:
            print(f"🔍 获取 r/{subreddit}...")
            posts = self.get_subreddit_posts(subreddit, limit=limit)
            all_news.extend(posts)

        return all_news

    def fetch_custom_subreddit(self, subreddit: str, limit: int = 10) -> List[Dict[str, Any]]:
        """获取自定义 subreddit"""
        print(f"🔍 获取 r/{subreddit}...")
        return self.get_subreddit_posts(subreddit, limit=limit)

    def filter_news(self, news_items: List[Dict[str, Any]], keywords: List[str] = None) -> List[Dict[str, Any]]:
        """过滤新闻"""
        if not keywords:
            return news_items

        filtered = []
        for item in news_items:
            title = item.get('title', '').lower()
            snippet = item.get('snippet', '').lower()

            # 检查是否包含关键词
            relevant = any(
                keyword.lower() in title or keyword.lower() in snippet
                for keyword in keywords
            )

            if relevant:
                filtered.append(item)

        return filtered

    def rank_news(self, news_items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """按热度排序新闻"""
        # 计算综合得分: upvotes + comments * 0.5
        for item in news_items:
            score = item.get('score', 0)
            comments = item.get('num_comments', 0)
            item['rank_score'] = score + (comments * 0.5)

        return sorted(news_items, key=lambda x: x.get('rank_score', 0), reverse=True)

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

    def fetch_daily_news(self, max_news: int = 10, categories: List[str] = None) -> List[Dict[str, Any]]:
        """
        获取每日新闻

        Args:
            max_news: 最大新闻数量
            categories: 类别列表 (ai, tech, all)
        """
        print("\n" + "=" * 60)
        print("📰 从 Reddit 获取新闻")
        print("=" * 60)

        all_news = []

        if categories is None or not categories:
            categories = ['ai', 'tech']

        for category in categories:
            if category == 'ai':
                print("🤖 获取 AI 新闻...")
                all_news.extend(self.fetch_ai_news())
            elif category == 'tech':
                print("💻 获取科技新闻...")
                all_news.extend(self.fetch_tech_news())

        # 去重
        unique_news = self.deduplicate_news(all_news)

        # 排序
        ranked_news = self.rank_news(unique_news)

        # 限制数量
        final_news = ranked_news[:max_news]

        print(f"✅ 获取到 {len(final_news)} 条新闻")
        return final_news

    def format_news_briefing(self, news_items: List[Dict[str, Any]]) -> str:
        """格式化新闻简报"""
        today = datetime.now().strftime('%Y-%m-%d')

        briefing = f"""# Reddit 新闻简报
**日期**: {today}
**来源**: Reddit

## 热门讨论
"""

        for i, item in enumerate(news_items, 1):
            title = item.get('title', '')
            subreddit = item.get('subreddit', '')
            score = item.get('score', 0)
            comments = item.get('num_comments', 0)
            url = item.get('url', '')
            snippet = item.get('snippet', '')

            briefing += f"\n### {i}. {title}\n"
            briefing += f"📍 r/{subreddit} | ⬆️ {score} | 💬 {comments}\n"

            if snippet and len(snippet) > 10:
                briefing += f"{snippet[:150]}...\n"

            briefing += f"🔗 {url}\n\n"

        briefing += f"""
---
*生成时间: {datetime.now().strftime('%H:%M:%S')}*
*共 {len(news_items)} 条新闻*
"""

        return briefing

def main():
    """主函数"""
    import argparse

    parser = argparse.ArgumentParser(description='Reddit 新闻获取脚本')
    parser.add_argument('--category', type=str, nargs='*', default=['ai', 'tech'],
                       help='新闻类别: ai, tech, all')
    parser.add_argument('--subreddit', type=str, help='指定 subreddit')
    parser.add_argument('--max', type=int, default=10, help='最大新闻数量')

    args = parser.parse_args()

    fetcher = RedditNewsFetcher()

    if args.subreddit:
        # 获取指定 subreddit
        news_items = fetcher.fetch_custom_subreddit(args.subreddit, args.max)
    else:
        # 获取新闻
        news_items = fetcher.fetch_daily_news(max_news=args.max, categories=args.category)

    if news_items:
        briefing = fetcher.format_news_briefing(news_items)
        print("\n" + briefing)
    else:
        print("❌ 未能获取到新闻")

if __name__ == "__main__":
    main()
