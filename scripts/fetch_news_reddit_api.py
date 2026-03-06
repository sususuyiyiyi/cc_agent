#!/usr/bin/env python3
"""
使用 Reddit API 获取新闻
需要 Reddit API 凭据
"""
import sys
import json
import requests
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any
import base64

# 添加项目根目录到 Python 路径
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

class RedditAPIClient:
    """Reddit API 客户端"""

    def __init__(self, client_id: str = None, client_secret: str = None, user_agent: str = None):
        """
        初始化 Reddit API 客户端

        Args:
            client_id: Reddit App Client ID
            client_secret: Reddit App Client Secret
            user_agent: User-Agent 字符串
        """
        self.client_id = client_id
        self.client_secret = client_secret
        self.access_token = None

        # User-Agent 格式: <platform>:<appID>:<version string> (by /u/<Reddit username>)
        if user_agent:
            self.user_agent = user_agent
        else:
            self.user_agent = 'CC-Agent:v1.0:by /u/CCAgent'

        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': self.user_agent
        })

    def authenticate(self) -> bool:
        """使用 OAuth 2.0 获取访问令牌"""
        if not self.client_id or not self.client_secret:
            print("⚠️ 未配置 Reddit API 凭据")
            return False

        try:
            auth = base64.b64encode(
                f"{self.client_id}:{self.client_secret}".encode()
            ).decode()

            headers = {
                'Authorization': f'Basic {auth}',
                'User-Agent': self.user_agent
            }

            data = {
                'grant_type': 'client_credentials'
            }

            response = self.session.post(
                'https://www.reddit.com/api/v1/access_token',
                headers=headers,
                data=data
            )

            if response.status_code == 200:
                token_data = response.json()
                self.access_token = token_data.get('access_token')
                print("✅ Reddit API 认证成功")
                return True
            else:
                print(f"❌ Reddit API 认证失败: {response.status_code}")
                return False

        except Exception as e:
            print(f"❌ Reddit API 认证错误: {e}")
            return False

    def get_subreddit_posts(self, subreddit: str, limit: int = 25, sort: str = 'hot') -> List[Dict[str, Any]]:
        """
        从指定 subreddit 获取帖子

        Args:
            subreddit: 子版块名称
            limit: 获取数量
            sort: 排序方式 (hot, new, top, rising)
        """
        if not self.access_token:
            print("⚠️ 未认证，请先调用 authenticate()")
            return []

        try:
            headers = {
                'Authorization': f'Bearer {self.access_token}',
                'User-Agent': self.user_agent
            }

            url = f"https://oauth.reddit.com/r/{subreddit}/{sort}?limit={limit}"
            response = self.session.get(url, headers=headers, timeout=10)

            if response.status_code == 200:
                data = response.json()
                posts = []

                for post in data['data']['children'][:limit]:
                    post_data = post['data']
                    posts.append({
                        'title': post_data.get('title', ''),
                        'url': post_data.get('url', ''),
                        'permalink': f"https://reddit.com{post_data.get('permalink', '')}",
                        'snippet': post_data.get('selftext', '')[:300],
                        'author': post_data.get('author', ''),
                        'score': post_data.get('score', 0),
                        'subreddit': subreddit,
                        'created': datetime.fromtimestamp(post_data.get('created', 0)).strftime('%Y-%m-%d'),
                        'num_comments': post_data.get('num_comments', 0),
                        'upvote_ratio': post_data.get('upvote_ratio', 0)
                    })

                return posts
            else:
                print(f"⚠️ 获取 {subreddit} 失败: {response.status_code}")
                return []

        except Exception as e:
            print(f"⚠️ 获取 {subreddit} 失败: {e}")
            return []

    def search_posts(self, query: str, subreddit: str = None, limit: int = 25) -> List[Dict[str, Any]]:
        """搜索帖子"""
        if not self.access_token:
            print("⚠️ 未认证，请先调用 authenticate()")
            return []

        try:
            headers = {
                'Authorization': f'Bearer {self.access_token}',
                'User-Agent': self.user_agent
            }

            if subreddit:
                url = f"https://oauth.reddit.com/r/{subreddit}/search?q={query}&limit={limit}"
            else:
                url = f"https://oauth.reddit.com/search?q={query}&limit={limit}"

            response = self.session.get(url, headers=headers, timeout=10)

            if response.status_code == 200:
                data = response.json()
                posts = []

                for post in data['data']['children'][:limit]:
                    post_data = post['data']
                    posts.append({
                        'title': post_data.get('title', ''),
                        'url': post_data.get('url', ''),
                        'permalink': f"https://reddit.com{post_data.get('permalink', '')}",
                        'snippet': post_data.get('selftext', '')[:300],
                        'author': post_data.get('author', ''),
                        'score': post_data.get('score', 0),
                        'subreddit': post_data.get('subreddit', ''),
                        'created': datetime.fromtimestamp(post_data.get('created', 0)).strftime('%Y-%m-%d'),
                        'num_comments': post_data.get('num_comments', 0)
                    })

                return posts
            else:
                print(f"⚠️ 搜索失败: {response.status_code}")
                return []

        except Exception as e:
            print(f"⚠️ 搜索失败: {e}")
            return []

class RedditNewsFetcher:
    """使用 Reddit 获取新闻"""

    def __init__(self):
        self.config = self._load_config()
        self.api_client = self._create_api_client()

    def _load_config(self) -> Dict[str, Any]:
        """加载配置"""
        import yaml

        config_path = PROJECT_ROOT / "config" / "news_apis.yaml"
        if not config_path.exists():
            return {}

        with open(config_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)

    def _create_api_client(self) -> RedditAPIClient:
        """创建 Reddit API 客户端"""
        reddit_config = self.config.get('reddit', {})

        client_id = reddit_config.get('client_id')
        client_secret = reddit_config.get('client_secret')
        user_agent = reddit_config.get('user_agent')

        return RedditAPIClient(client_id, client_secret, user_agent)

    def authenticate(self) -> bool:
        """认证 Reddit API"""
        return self.api_client.authenticate()

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
            posts = self.api_client.get_subreddit_posts(subreddit, limit=limit)
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
            ('Python', 2)
        ]

        for subreddit, limit in tech_subreddits:
            print(f"🔍 获取 r/{subreddit}...")
            posts = self.api_client.get_subreddit_posts(subreddit, limit=limit)
            all_news.extend(posts)

        return all_news

    def fetch_daily_news(self, max_news: int = 10, categories: List[str] = None) -> List[Dict[str, Any]]:
        """获取每日新闻"""
        print("\n" + "=" * 60)
        print("📰 从 Reddit 获取新闻")
        print("=" * 60)

        # 尝试认证
        if not self.authenticate():
            print("⚠️ Reddit API 认证失败，请配置 API 凭据")
            return []

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
        unique_news = self._deduplicate_news(all_news)

        # 排序
        ranked_news = self._rank_news(unique_news)

        # 限制数量
        final_news = ranked_news[:max_news]

        print(f"✅ 获取到 {len(final_news)} 条新闻")
        return final_news

    def _deduplicate_news(self, news_items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """去重新闻"""
        seen_titles = set()
        unique_news = []

        for item in news_items:
            title = item.get('title', '').strip().lower()
            if title and title not in seen_titles:
                seen_titles.add(title)
                unique_news.append(item)

        return unique_news

    def _rank_news(self, news_items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """按热度排序新闻"""
        for item in news_items:
            score = item.get('score', 0)
            comments = item.get('num_comments', 0)
            upvote_ratio = item.get('upvote_ratio', 0)
            item['rank_score'] = score + (comments * 0.5) + (upvote_ratio * 100)

        return sorted(news_items, key=lambda x: x.get('rank_score', 0), reverse=True)

def main():
    """主函数"""
    import argparse

    parser = argparse.ArgumentParser(description='Reddit API 新闻获取脚本')
    parser.add_argument('--category', type=str, nargs='*', default=['ai', 'tech'],
                       help='新闻类别: ai, tech, all')
    parser.add_argument('--max', type=int, default=10, help='最大新闻数量')

    args = parser.parse_args()

    fetcher = RedditNewsFetcher()
    news_items = fetcher.fetch_daily_news(max_news=args.max, categories=args.category)

    if news_items:
        print("\n📋 Reddit 新闻:")
        for i, item in enumerate(news_items, 1):
            print(f"\n{i}. {item['title']}")
            print(f"   📍 r/{item['subreddit']} | ⬆️ {item['score']} | 💬 {item['num_comments']}")
            print(f"   🔗 {item['permalink']}")
    else:
        print("❌ 未能获取到新闻")

if __name__ == "__main__":
    main()
