#!/usr/bin/env python3
"""
真实新闻获取脚本
使用公开的 API 和爬虫获取新闻
"""
import sys
import requests
import json
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Dict, Any
from urllib.parse import urljoin, quote
import re

# 添加项目根目录到 Python 路径
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

class RealNewsFetcher:
    """真实新闻获取器"""

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        })

    def fetch_from_google_news(self, query: str, max_results: int = 10) -> List[Dict[str, Any]]:
        """从 Google News 获取新闻（通过 RSS）"""
        try:
            # Google News RSS URL
            encoded_query = quote(query)
            rss_url = f"https://news.google.com/rss/search?q={encoded_query}&hl=zh-CN&gl=CN&ceid=CN:zh-Hans"

            response = self.session.get(rss_url, timeout=10)
            response.raise_for_status()

            # 解析 XML
            import xml.etree.ElementTree as ET
            root = ET.fromstring(response.content)

            news_items = []
            for item in root.findall('.//item')[:max_results]:
                title = item.find('title').text if item.find('title') is not None else ''
                link = item.find('link').text if item.find('link') is not None else ''
                description = item.find('description').text if item.find('description') is not None else ''

                # 清理 HTML 标签
                clean_description = re.sub('<[^<]+?>', '', description) if description else ''

                news_items.append({
                    'title': title,
                    'url': link,
                    'snippet': clean_description[:200] if clean_description else '',
                    'source': self._extract_source(link),
                    'date': datetime.now().strftime('%Y-%m-%d')
                })

            return news_items

        except Exception as e:
            print(f"⚠️ Google News 获取失败: {e}")
            return []

    def fetch_from_bing_news(self, query: str, max_results: int = 10) -> List[Dict[str, Any]]:
        """从 Bing News 获取新闻（需要 API Key，这里使用备用方案）"""
        # 暂时返回空，需要 API Key
        return []

    def fetch_from_36kr(self) -> List[Dict[str, Any]]:
        """从 36氪获取科技新闻"""
        try:
            url = "https://36kr.com/api/mobilerecommend/aweme/posts"
            response = self.session.get(url, timeout=10)
            response.raise_for_status()

            data = response.json()

            news_items = []
            if data.get('code') == 0:
                for item in data.get('data', {}).get('item_list', [])[:5]:
                    news_items.append({
                        'title': item.get('title', ''),
                        'url': f"https://36kr.com/p/{item.get('id', '')}",
                        'snippet': item.get('summary', ''),
                        'source': '36氪',
                        'date': datetime.now().strftime('%Y-%m-%d')
                    })

            return news_items

        except Exception as e:
            print(f"⚠️ 36氪获取失败: {e}")
            return []

    def fetch_from_it之家(self) -> List[Dict[str, Any]]:
        """从 IT之家获取科技新闻"""
        try:
            url = "https://www.ithome.com/rss/"
            response = self.session.get(url, timeout=10)
            response.raise_for_status()

            import xml.etree.ElementTree as ET
            root = ET.fromstring(response.content)

            news_items = []
            for item in root.findall('.//item')[:5]:
                title = item.find('title').text if item.find('title') is not None else ''
                link = item.find('link').text if item.find('link') is not None else ''
                description = item.find('description').text if item.find('description') is not None else ''

                clean_description = re.sub('<[^<]+?>', '', description) if description else ''

                news_items.append({
                    'title': title,
                    'url': link,
                    'snippet': clean_description[:200] if clean_description else '',
                    'source': 'IT之家',
                    'date': datetime.now().strftime('%Y-%m-%d')
                })

            return news_items

        except Exception as e:
            print(f"⚠️ IT之家获取失败: {e}")
            return []

    def _extract_source(self, url: str) -> str:
        """从URL提取来源"""
        try:
            from urllib.parse import urlparse
            domain = urlparse(url).netloc
            if domain.startswith('www.'):
                domain = domain[4:]
            return domain
        except:
            return '未知来源'

    def fetch_daily_news(self, max_news: int = 10) -> List[Dict[str, Any]]:
        """获取每日新闻"""
        print("\n" + "=" * 60)
        print("📰 获取今日新闻")
        print("=" * 60)

        all_news = []

        # 从多个来源获取
        print("🔍 从 36氪 获取科技新闻...")
        all_news.extend(self.fetch_from_36kr())

        print("🔍 从 IT之家 获取科技新闻...")
        all_news.extend(self.fetch_from_it之家())

        print("🔍 从 Google News 搜索 AI 新闻...")
        all_news.extend(self.fetch_from_google_news("AI 人工智能"))

        # 去重
        seen_titles = set()
        unique_news = []

        for news in all_news:
            title = news.get('title', '').strip().lower()
            if title and title not in seen_titles and len(title) > 5:
                seen_titles.add(title)
                unique_news.append(news)

        # 限制数量
        final_news = unique_news[:max_news]

        print(f"✅ 获取到 {len(final_news)} 条新闻")
        return final_news

    def format_news_briefing(self, news_items: List[Dict[str, Any]]) -> str:
        """格式化新闻简报"""
        today = datetime.now().strftime('%Y-%m-%d')

        briefing = f"""# 今日新闻简报
**日期**: {today}

## 科技资讯
"""

        for i, item in enumerate(news_items, 1):
            title = item.get('title', '')
            summary = item.get('snippet', '')
            source = item.get('source', '')
            url = item.get('url', '')

            briefing += f"\n### {i}. {title}\n"
            if summary:
                briefing += f"{summary}\n"
            briefing += f"📍 来源: {source}\n\n"

        briefing += f"""
---
*生成时间: {datetime.now().strftime('%H:%M:%S')}*
*共 {len(news_items)} 条新闻*
"""

        return briefing

def main():
    """主函数"""
    fetcher = RealNewsFetcher()
    news_items = fetcher.fetch_daily_news()

    if news_items:
        briefing = fetcher.format_news_briefing(news_items)
        print("\n" + briefing)
    else:
        print("❌ 未能获取到新闻")

if __name__ == "__main__":
    main()
