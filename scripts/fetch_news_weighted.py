#!/usr/bin/env python3
"""
增强版新闻获取器
基于权重和热点分类获取新闻
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

class WeightedNewsFetcher:
    """权重新闻获取器"""

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        })
        self.config = self._load_config()
        self.source_weights = self._get_source_weights()

    def _load_config(self) -> Dict[str, Any]:
        """加载配置"""
        config_path = PROJECT_ROOT / "config" / "config.yaml"
        if config_path.exists():
            with open(config_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        return {}

    def _get_source_weights(self) -> Dict[str, float]:
        """获取源权重配置"""
        weights = {}
        prefs = self.config.get('preferences', {}).get('news', {})
        weighting = prefs.get('weighting', {})

        # 研究源
        for source in weighting.get('research_sources', []):
            weights[source] = weighting.get('research_weight', 3.0)

        # AI日报
        for source in weighting.get('daily_sources', []):
            weights[source] = weighting.get('daily_weight', 2.5)

        # AI垂直
        for source in weighting.get('ai_vertical_sources', []):
            weights[source] = weighting.get('ai_vertical_weight', 2.0)

        # Reddit社区
        for source in weighting.get('reddit_sources', []):
            weights[source] = weighting.get('reddit_weight', 1.8)

        # 科技媒体
        for source in weighting.get('tech_media_sources', []):
            weights[source] = weighting.get('tech_media_weight', 1.5)

        # 国际科技
        for source in weighting.get('international_sources', []):
            weights[source] = weighting.get('international_weight', 1.8)

        # 默认权重
        default_sources = self.config.get('preferences', {}).get('news', {}).get('sources', [])
        for source in default_sources:
            if source not in weights:
                weights[source] = 1.0

        return weights

    def _get_hot_queries(self) -> List[str]:
        """获取热点查询词"""
        return [
            "artificial intelligence", "AI", "machine learning", "deep learning",
            "ChatGPT", "GPT-4", "OpenAI", "Claude", "Anthropic",
            "generative AI", "大语言模型", "人工智能", "机器学习",
            "自动驾驶", "机器人", "计算机视觉", "自然语言处理",
            "科技新闻", "创新", "startup", "venture"
        ]

    def fetch_with_weighting(self, max_news: int = 15) -> List[Dict[str, Any]]:
        """获取带权重的新闻"""
        all_news = []

        # 从 Google News 获取 AI 相关新闻
        for query in self._get_hot_queries()[:5]:  # 使用前5个热点词
            news = self.fetch_from_google_news(query, max_results=8)
            all_news.extend(news)

        # 尝试获取 Reddit 内容（如果配置了）
        try:
            from scripts.fetch_reddit_weighted import RedditNewsFetcher
            reddit_fetcher = RedditNewsFetcher()
            reddit_posts = reddit_fetcher.fetch_daily_reddit_news(max_news//2)
            all_news.extend(reddit_posts)
        except Exception as e:
            print(f"⚠️ Reddit获取失败: {e}")

        # 获取权重并排序
        weighted_news = []
        for item in all_news:
            url = item.get('url', '')
            base_url = self._extract_base_url(url)

            # 如果是Reddit，使用特殊权重
            if 'reddit.com/r/' in url:
                item['_weight'] = item.get('_weight', 1.8)  # Reddit默认权重
            else:
                item['_weight'] = self.source_weights.get(base_url, 1.0)

            # 根据权重调整新闻的排序优先级
            item['_category'] = self._categorize_news(item)
            weighted_news.append(item)

        # 按权重和去重后排序
        unique_news = self._deduplicate_news(weighted_news)
        sorted_news = sorted(unique_news,
                          key=lambda x: (x.get('_weight', 1.0), x.get('score', 0)),
                          reverse=True)

        return sorted_news[:max_news]

    def _extract_base_url(self, url: str) -> str:
        """提取基础 URL"""
        if not url:
            return ''
        try:
            # 移除协议和路径
            base = url.split('//')[1] if '//' in url else url
            base = base.split('/')[0]
            # 添加协议
            return 'https://' + base
        except:
            return url

    def _categorize_news(self, item: Dict[str, Any]) -> str:
        """根据来源和内容分类新闻"""
        url = item.get('url', '')
        title = item.get('title', '').lower()

        # AI垂直
        ai_vertical_sources = [
            'zhidx.com', 'leiphone.com', 'cvmart.net',
            'syncedreview.com', 'infoq.cn'
        ]

        # 科技媒体
        tech_media_sources = [
            '36kr.com', 'huxiu.com', 'geekpark.net',
            'tmtpost.com', 'latepost.com'
        ]

        # 国际科技
        international_sources = [
            'techcrunch.com', 'venturebeat.com', 'theinformation.com'
        ]

        # AI研究
        research_sources = [
            'openai.com', 'deepmind.google.com', 'huggingface.co',
            'anthropic.com', 'deeplearning.ai'
        ]

        # Reddit社区
        reddit_sources = [
            'reddit.com/r/artificial', 'reddit.com/r/MachineLearning',
            'reddit.com/r/ChatGPT', 'reddit.com/r/openai',
            'reddit.com/r/technology', 'reddit.com/r/programming',
            'reddit.com/r/compsci'
        ]

        base_url = self._extract_base_url(url)

        # 根据URL分类
        if any(source in base_url for source in research_sources):
            return '🤖 AI前沿'
        elif any(source in base_url for source in daily_sources):
            return '📰 AI日报'
        elif any(source in base_url for source in reddit_sources):
            return '💬 Reddit热议'
        elif any(source in base_url for source in ai_vertical_sources):
            return '🤖 AI前沿'
        elif any(source in base_url for source in tech_media_sources):
            return '📱 科技媒体'
        elif any(source in base_url for source in international_sources):
            return '🌍 国际科技'
        elif 'ai' in title or '人工智能' in title:
            return '🤖 AI前沿'
        elif 'tech' in title or '科技' in title:
            return '📱 科技动态'
        else:
            return '🔬 科学研究'

    def _deduplicate_news(self, news_list: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """去重新闻（基于标题相似度）"""
        unique_news = []
        seen_titles = set()

        for item in news_list:
            title = item.get('title', '').lower().strip()
            # 简单的标题去重
            if title and title not in seen_titles:
                seen_titles.add(title)
                unique_news.append(item)

        return unique_news

    def fetch_from_google_news(self, query: str, max_results: int = 10) -> List[Dict[str, Any]]:
        """从 Google News 获取新闻"""
        try:
            encoded_query = quote(query)
            rss_url = f"https://news.google.com/rss/search?q={encoded_query}&hl=zh-CN&gl=CN&ceid=CN:zh-Hans"

            response = self.session.get(rss_url, timeout=10)
            response.raise_for_status()

            import xml.etree.ElementTree as ET
            root = ET.fromstring(response.content)

            news_items = []
            for item in root.findall('.//item')[:max_results]:
                title = item.find('title').text if item.find('title') is not None else ''
                link = item.find('link').text if item.find('link') is not None else ''
                description = item.find('description').text if item.find('description') is not None else ''
                pub_date = item.find('pubDate').text if item.find('pubDate') is not None else ''

                # 清理描述
                clean_description = re.sub('<[^<]+?>', '', description) if description else ''

                # 提取来源
                source = self._extract_source_from_link(link)

                news_item = {
                    'title': title,
                    'url': link,
                    'summary': clean_description[:300],
                    'source': source,
                    'source_type': 'google_news',
                    'published_at': pub_date,
                    'score': self._calculate_score(title, clean_description, query)
                }

                news_items.append(news_item)

            return news_items
        except Exception as e:
            print(f"❌ 获取 Google News 失败: {e}")
            return []

    def _extract_source_from_link(self, link: str) -> str:
        """从链接提取来源名称"""
        if not link:
            return 'Google News'

        try:
            domain = link.split('//')[1].split('/')[0]
            # 移除 www.
            if domain.startswith('www.'):
                domain = domain[4:]

            # 映射常见的域名
            domain_mapping = {
                '36kr.com': '36氪',
                'huxiu.com': '虎嗅',
                'techcrunch.com': 'TechCrunch',
                'venturebeat.com': 'VentureBeat',
                'zhidx.com': '机器之心',
                'leiphone.com': '雷锋网',
                'therundown.ai': 'The Rundown',
                'openai.com': 'OpenAI',
                'deepmind.google.com': 'DeepMind'
            }

            return domain_mapping.get(domain, domain)
        except:
            return 'Google News'

    def _calculate_score(self, title: str, summary: str, query: str) -> float:
        """计算新闻分数（基于查询词匹配和长度）"""
        score = 0.0

        # 标题匹配
        if query.lower() in title.lower():
            score += 10
        elif any(word in title.lower() for word in query.lower().split()):
            score += 5

        # 摘要长度
        if len(summary) > 100:
            score += 2

        # 时间权重（如果包含时间）
        if '小时' in summary or '分钟' in summary:
            score += 3

        return score

    def fetch_daily_news(self, max_news: int = 15) -> List[Dict[str, Any]]:
        """获取每日新闻（带权重）"""
        print("🔍 开始获取带权重的新闻...")

        # 获取权重新闻
        news_items = self.fetch_with_weighting(max_news)

        # 按分类整理
        categorized_news = {}
        for item in news_items:
            category = item.get('_category', '🔬 科学研究')
            if category not in categorized_news:
                categorized_news[category] = []
            categorized_news[category].append(item)

        print(f"✅ 获取到 {len(news_items)} 条新闻")
        print("📊 分类统计:")
        for category, items in categorized_news.items():
            print(f"   {category}: {len(items)} 条")

        return news_items

if __name__ == "__main__":
    fetcher = WeightedNewsFetcher()
    news = fetcher.fetch_daily_news()

    print(f"\n📋 前 5 条新闻（按权重排序）:")
    for i, item in enumerate(news[:5], 1):
        print(f"{i}. [{item.get('_category', '')}] {item['title']}")
        print(f"   来源: {item.get('source', '')} | 权重: {item.get('_weight', 1.0)}")
        print()