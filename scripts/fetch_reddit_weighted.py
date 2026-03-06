#!/usr/bin/env python3
"""
Reddit 权重新闻获取器
"""

import sys
import requests
import json
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Dict, Any, Tuple
from urllib.parse import urljoin, quote
import re
import yaml

# 添加项目根目录到 Python 路径
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

class RedditNewsFetcher:
    """Reddit新闻获取器"""

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        })
        self.config = self._load_config()
        self.reddit_config = self._get_reddit_config()

    def _load_config(self) -> Dict[str, Any]:
        """加载配置"""
        config_path = PROJECT_ROOT / "config" / "config.yaml"
        if config_path.exists():
            with open(config_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        return {}

    def _get_reddit_config(self) -> Dict[str, Any]:
        """获取Reddit配置"""
        return {
            'client_id': 'YOUR_CLIENT_ID',  # 需要在Reddit申请
            'client_secret': 'YOUR_CLIENT_SECRET',  # 需要在Reddit申请
            'user_agent': 'cc_agent/1.0 by susu',
            'subreddits': [
                'artificial',  # AI相关讨论
                'MachineLearning',  # 机器学习
                'ChatGPT',  # ChatGPT讨论
                'openai',  # OpenAI相关
                'technology',  # 科技新闻
                'programming',  # 编程
                'compsci',  # 计算机科学
                'FutureWhatIf',  # 未来科技假设
                'Singularity',  # 技术奇点
                'AIExplain'  # AI解释
            ],
            'post_limit': 5  # 每个subreddit获取的帖子数量
        }

    def fetch_reddit_posts(self, max_posts: int = 20) -> List[Dict[str, Any]]:
        """获取Reddit帖子"""
        all_posts = []

        # 由于没有API密钥，我们使用RSS feed（公开的）
        subreddit_feeds = {
            'artificial': 'https://www.reddit.com/r/artificial/new/.rss',
            'MachineLearning': 'https://www.reddit.com/r/MachineLearning/new/.rss',
            'ChatGPT': 'https://www.reddit.com/r/ChatGPT/new/.rss',
            'openai': 'https://www.reddit.com/r/openai/new/.rss',
            'technology': 'https://www.reddit.com/r/technology/new/.rss',
            'programming': 'https://www.reddit.com/r/programming/new/.rss',
            'compsci': 'https://www.reddit.com/r/compsci/new/.rss'
        }

        for subreddit, rss_url in subreddit_feeds.items():
            try:
                posts = self._fetch_from_rss(rss_url, subreddit)
                all_posts.extend(posts)
            except Exception as e:
                print(f"❌ 获取 r/{subreddit} 失败: {e}")

        # 按权重排序
        weighted_posts = []
        for post in all_posts:
            weight = self._calculate_post_weight(post)
            post['_weight'] = weight
            post['_category'] = '💬 Reddit热议'
            weighted_posts.append(post)

        # 去重和排序
        unique_posts = self._deduplicate_posts(weighted_posts)
        sorted_posts = sorted(unique_posts,
                          key=lambda x: (x.get('_weight', 0), x.get('score', 0)),
                          reverse=True)

        return sorted_posts[:max_posts]

    def _fetch_from_rss(self, rss_url: str, subreddit: str) -> List[Dict[str, Any]]:
        """从RSS获取Reddit帖子"""
        try:
            response = self.session.get(rss_url, timeout=10)
            response.raise_for_status()

            import xml.etree.ElementTree as ET
            root = ET.fromstring(response.content)

            posts = []
            for item in root.findall('.//item')[:5]:  # 每个subreddit最多5条
                title = item.find('title').text if item.find('title') is not None else ''
                link = item.find('link').text if item.find('link') is not None else ''
                description = item.find('description').text if item.find('description') is not None else ''
                pub_date = item.find('pubDate').text if item.find('pubDate') is not None else ''

                # 提取评论区数
                num_comments = self._extract_comments_count(description)

                # 提取投票数（可能需要从URL解析）
                score = self._extract_score(description)

                post = {
                    'title': title,
                    'url': link,
                    'summary': self._clean_description(description)[:300],
                    'source': f'r/{subreddit}',
                    'source_type': 'reddit',
                    'subreddit': subreddit,
                    'published_at': pub_date,
                    'num_comments': num_comments,
                    'score': score,
                    'category': subreddit
                }

                posts.append(post)

            return posts
        except Exception as e:
            print(f"❌ RSS获取失败: {e}")
            return []

    def _extract_comments_count(self, description: str) -> int:
        """提取评论数"""
        if not description:
            return 0

        # 寻找评论数模式
        match = re.search(r'(\d+)\s*comment', description, re.IGNORECASE)
        if match:
            return int(match.group(1))

        # 如果没有找到，返回估计值
        return 0

    def _extract_score(self, description: str) -> int:
        """提取投票数"""
        if not description:
            return 0

        # Reddit投票数通常在描述中不明显，这里返回一个基础值
        # 实际应用中可能需要解析页面
        return 0

    def _clean_description(self, description: str) -> str:
        """清理RSS描述"""
        if not description:
            return ''

        # 移除HTML标签
        clean_text = re.sub('<[^<]+?>', '', description)

        # 移除多余的空格
        clean_text = re.sub(r'\s+', ' ', clean_text).strip()

        return clean_text

    def _calculate_post_weight(self, post: Dict[str, Any]) -> float:
        """计算Reddit帖子权重"""
        weight = 1.0  # 基础权重

        subreddit = post.get('subreddit', '')
        score = post.get('score', 0)
        num_comments = post.get('num_comments', 0)

        # 高质量subreddit权重
        high_quality_subreddits = ['MachineLearning', 'artificial', 'ChatGPT', 'openai']
        if subreddit in high_quality_subreddits:
            weight += 1.5

        # 根据评论数增加权重
        if num_comments > 10:
            weight += 0.5
        if num_comments > 50:
            weight += 1.0

        # 根据投票数增加权重
        if score > 100:
            weight += 1.0

        # 包含特定关键词的帖子
        title = post.get('title', '').lower()
        if any(keyword in title for keyword in ['breakthrough', 'paper', 'research', 'study']):
            weight += 0.5

        return weight

    def _deduplicate_posts(self, posts: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """去重Reddit帖子"""
        unique_posts = []
        seen_titles = set()

        for post in posts:
            title = post.get('title', '').lower().strip()
            if title and title not in seen_titles:
                seen_titles.add(title)
                unique_posts.append(post)

        return unique_posts

    def fetch_daily_reddit_news(self, max_posts: int = 20) -> List[Dict[str, Any]]:
        """获取每日Reddit新闻"""
        print("🔍 开始获取Reddit热门讨论...")

        # 获取Reddit帖子
        posts = self.fetch_reddit_posts(max_posts)

        # 按subreddit分类
        subreddit_counts = {}
        for post in posts:
            subreddit = post.get('subreddit', 'unknown')
            subreddit_counts[subreddit] = subreddit_counts.get(subreddit, 0) + 1

        print(f"✅ 获取到 {len(posts)} 条Reddit讨论")
        print("📊 Subreddit统计:")
        for subreddit, count in subreddit_counts.items():
            print(f"   r/{subreddit}: {count} 条")

        return posts

if __name__ == "__main__":
    fetcher = RedditNewsFetcher()
    posts = fetcher.fetch_daily_reddit_news()

    print(f"\n📋 前 5 条讨论（按权重排序）:")
    for i, post in enumerate(posts[:5], 1):
        print(f"{i}. [{post.get('subreddit', '')}] {post['title']}")
        print(f"   来源: {post.get('source', '')} | 权重: {post.get('_weight', 1.0)} | 评论: {post.get('num_comments', 0)}")
        print()