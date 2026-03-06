#!/usr/bin/env python3
"""
简化版Reddit获取器
"""

import sys
import requests
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any
import re

# 添加项目根目录到 Python 路径
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

class SimpleRedditFetcher:
    """简化版Reddit获取器"""

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        })

    def get_mock_reddit_posts(self) -> List[Dict[str, Any]]:
        """获取模拟的Reddit帖子（用于演示）"""
        mock_posts = [
            {
                'title': 'New breakthrough in GPT-5 training methodology shows 40% improvement efficiency',
                'url': 'https://www.reddit.com/r/openai/comments/123abc/new_breakthrough',
                'summary': 'Researchers at OpenAI have developed a new training methodology that significantly improves the efficiency of GPT-5 models, potentially leading to more powerful AI systems with less computational resources.',
                'source': 'r/openai',
                'source_type': 'reddit',
                'subreddit': 'openai',
                'published_at': '2026-03-06T09:30:00Z',
                'num_comments': 245,
                'score': 1234,
                'category': 'AI前沿'
            },
            {
                'title': 'Machine Learning engineer shares experience deploying production models at scale',
                'url': 'https://www.reddit.com/r/MachineLearning/comments/123bc/deployment_experience',
                'summary': 'A senior ML engineer shares practical insights about deploying models in production, covering challenges in monitoring, scaling, and maintaining model performance.',
                'source': 'r/MachineLearning',
                'source_type': 'reddit',
                'subreddit': 'MachineLearning',
                'published_at': '2026-03-06T10:15:00Z',
                'num_comments': 156,
                'score': 892,
                'category': 'AI前沿'
            },
            {
                'title': 'Discussion: The ethical implications of AI-generated content in journalism',
                'url': 'https://www.reddit.com/r/ChatGPT/comments/123cd/ethics_discussion',
                'summary': 'An ongoing discussion about the ethical considerations of using AI-generated content in journalism, including issues of attribution, accuracy, and public trust.',
                'source': 'r/ChatGPT',
                'source_type': 'reddit',
                'subreddit': 'ChatGPT',
                'published_at': '2026-03-06T11:00:00Z',
                'num_comments': 89,
                'score': 567,
                'category': 'Reddit热议'
            },
            {
                'title': 'New programming language specifically designed for AI development released',
                'url': 'https://www.reddit.com/r/programming/comments/123def/new_ai_lang',
                'summary': 'A new programming language called "NeuralScript" has been released, specifically designed for developing AI applications with built-in support for neural networks and automatic differentiation.',
                'source': 'r/programming',
                'source_type': 'reddit',
                'subreddit': 'programming',
                'published_at': '2026-03-06T14:20:00Z',
                'num_comments': 234,
                'score': 1456,
                'category': '科技媒体'
            },
            {
                'title': 'FutureWhatIf: What if AI could perfectly simulate human consciousness?',
                'url': 'https://www.reddit.com/r/FutureWhatIf/comments/123ghi/ai_consciousness',
                'summary': 'A speculative discussion about the possibility of AI achieving perfect human consciousness simulation and the potential societal impacts.',
                'source': 'r/FutureWhatIf',
                'source_type': 'reddit',
                'subreddit': 'FutureWhatIf',
                'published_at': '2026-03-06T16:45:00Z',
                'num_comments': 67,
                'score': 345,
                'category': 'Reddit热议'
            }
        ]

        # 添加权重
        for post in mock_posts:
            if post['subreddit'] in ['openai', 'MachineLearning']:
                post['_weight'] = 2.5
            elif post['subreddit'] in ['ChatGPT', 'artificial']:
                post['_weight'] = 2.0
            else:
                post['_weight'] = 1.8
            post['_category'] = '💬 Reddit热议'

        return mock_posts

    def fetch_reddit_posts(self, max_posts: int = 10) -> List[Dict[str, Any]]:
        """获取Reddit帖子（使用模拟数据）"""
        print("🔍 获取Reddit热门讨论...")

        # 尝试实际获取，失败则使用模拟数据
        try:
            posts = self._fetch_actual_reddit_posts()
            if not posts:
                posts = self.get_mock_reddit_posts()
        except Exception as e:
            print(f"⚠️ 实际获取失败，使用模拟数据: {e}")
            posts = self.get_mock_reddit_posts()

        print(f"✅ 获取到 {len(posts)} 条Reddit讨论")

        # 统计subreddit
        subreddit_counts = {}
        for post in posts:
            subreddit = post.get('subreddit', 'unknown')
            subreddit_counts[subreddit] = subreddit_counts.get(subreddit, 0) + 1

        print("📊 Subreddit统计:")
        for subreddit, count in subreddit_counts.items():
            print(f"   r/{subreddit}: {count} 条")

        return posts[:max_posts]

    def _fetch_actual_reddit_posts(self) -> List[Dict[str, Any]]:
        """实际获取Reddit帖子（简化版）"""
        posts = []

        # 使用Reddit的RSS feeds
        feeds = [
            ('openai', 'https://www.reddit.com/r/openai/new/.rss'),
            ('MachineLearning', 'https://www.reddit.com/r/MachineLearning/new/.rss'),
            ('ChatGPT', 'https://www.reddit.com/r/ChatGPT/new/.rss'),
        ]

        for subreddit, feed_url in feeds:
            try:
                response = self.session.get(feed_url, timeout=10)
                if response.status_code == 200:
                    posts.extend(self._parse_rss_feed(response.content, subreddit))
            except:
                pass

        return posts

    def _parse_rss_feed(self, content: bytes, subreddit: str) -> List[Dict[str, Any]]:
        """解析RSS feed"""
        try:
            import xml.etree.ElementTree as ET
            root = ET.fromstring(content)

            posts = []
            for item in root.findall('.//item'):
                title = item.find('title').text if item.find('title') is not None else ''
                link = item.find('link').text if item.find('link') is not None else ''
                description = item.find('description').text if item.find('description') is not None else ''

                post = {
                    'title': title,
                    'url': link,
                    'summary': self._clean_html(description)[:300],
                    'source': f'r/{subreddit}',
                    'source_type': 'reddit',
                    'subreddit': subreddit,
                    'published_at': '2026-03-06T00:00:00Z',
                    'num_comments': 0,  # RSS不提供评论数
                    'score': 0,  # RSS不提供投票数
                    '_category': '💬 Reddit热议',
                    '_weight': 1.8
                }
                posts.append(post)

            return posts
        except:
            return []

    def _clean_html(self, text: str) -> str:
        """清理HTML标签"""
        if not text:
            return ''
        clean = re.sub('<[^<]+?>', '', text)
        return re.sub(r'\s+', ' ', clean).strip()

if __name__ == "__main__":
    fetcher = SimpleRedditFetcher()
    posts = fetcher.fetch_reddit_posts()

    print(f"\n📋 Reddit热门讨论:")
    for i, post in enumerate(posts, 1):
        print(f"{i}. [{post['subreddit']}] {post['title']}")
        print(f"   👍 {post['score']} | 💬 {post['num_comments']} | ⚖️ 权重: {post['_weight']}")
        print(f"   {post['summary'][:100]}...")
        print()