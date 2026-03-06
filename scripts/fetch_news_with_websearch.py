#!/usr/bin/env python3
"""
使用 WebSearch 的真实新闻获取脚本
"""

import sys
import yaml
import json
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Dict, Any

# 添加项目根目录到 Python 路径
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

class RealNewsFetcher:
    """真实新闻获取器"""

    def __init__(self):
        self.config = self.load_config()
        self.websearch_enabled = self.config.get('websearch', {}).get('enabled', False)
        self.api_key = self._get_brave_api_key()

    def load_config(self) -> Dict[str, Any]:
        """加载配置"""
        config_path = PROJECT_ROOT / "config" / "config.yaml"
        if not config_path.exists():
            return {}

        with open(config_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)

    def _get_brave_api_key(self) -> str:
        """获取 Brave Search API Key"""
        # 从环境变量读取
        import os
        api_key = os.getenv('BRAVE_API_KEY', '')

        # 如果环境变量没有，尝试从 MCP 配置读取
        if not api_key:
            mcp_config_path = PROJECT_ROOT / "config" / "mcp_config.json"
            if mcp_config_path.exists():
                with open(mcp_config_path, 'r', encoding='utf-8') as f:
                    mcp_config = json.load(f)
                    websearch_config = mcp_config.get('mcpServers', {}).get('websearch', {})
                    api_key = websearch_config.get('env', {}).get('BRAVE_API_KEY', '')

        return api_key

    def search_with_brave(self, query: str, count: int = 5) -> List[Dict[str, Any]]:
        """使用 Brave Search API 搜索"""
        if not self.api_key:
            print(f"⚠️ Brave API Key 未配置")
            return []

        import requests

        url = "https://api.search.brave.com/res/v1/web/search"
        headers = {
            "Accept": "application/json",
            "Accept-Encoding": "gzip",
            "X-Subscription-Token": self.api_key
        }
        params = {
            "q": query,
            "count": count,
            "text_decorations": False,
            "search_lang": "zh-CN,en"
        }

        try:
            response = requests.get(url, headers=headers, params=params, timeout=10)
            response.raise_for_status()

            data = response.json()

            # 提取搜索结果
            results = []
            web_results = data.get('web', {}).get('results', [])

            for result in web_results:
                results.append({
                    'title': result.get('title', ''),
                    'url': result.get('url', ''),
                    'snippet': result.get('description', ''),
                    'publishedDate': result.get('publishedDate', ''),
                    'source': self._extract_source(result.get('url', ''))
                })

            return results

        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 401:
                print(f"❌ API Key 无效: {e}")
            elif e.response.status_code == 429:
                print(f"❌ API 调用次数超限: {e}")
            else:
                print(f"❌ HTTP 错误: {e}")
        except Exception as e:
            print(f"❌ 搜索失败: {e}")

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

    def search_news(self, queries: List[str], max_results: int = 10) -> List[Dict[str, Any]]:
        """搜索新闻"""
        all_results = []
        results_per_query = max(2, max_results // len(queries))

        print(f"\n🔍 搜索 {len(queries)} 个查询，每个查询最多 {results_per_query} 条结果")

        for query in queries:
            print(f"   搜索: {query}")
            results = self.search_with_brave(query, count=results_per_query)
            all_results.extend(results)

        return all_results

    def deduplicate_news(self, news_items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """去重新闻"""
        seen = set()
        unique_news = []

        for item in news_items:
            # 使用标题进行去重
            title_key = item.get('title', '').strip().lower()
            if title_key and title_key not in seen:
                seen.add(title_key)
                unique_news.append(item)

        return unique_news

    def filter_by_relevance(self, news_items: List[Dict[str, Any]], keywords: List[str]) -> List[Dict[str, Any]]:
        """过滤相关性"""
        filtered = []

        for item in news_items:
            title = item.get('title', '').lower()
            snippet = item.get('snippet', '').lower()

            # 检查是否包含关键词
            relevant = any(
                keyword.lower() in title or keyword.lower() in snippet
                for keyword in keywords
            )

            if relevant or not keywords:
                filtered.append(item)

        return filtered

    def rank_news(self, news_items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """排序新闻"""
        # 按日期排序（最新的在前）
        def sort_key(item):
            date_str = item.get('publishedDate', '')
            try:
                # 处理 ISO 格式日期
                return datetime.fromisoformat(date_str.replace('Z', '+00:00'))
            except:
                # 如果没有日期，使用当前时间
                return datetime.max

        return sorted(news_items, key=sort_key, reverse=True)

    def format_news_briefing(self, news_items: List[Dict[str, Any]]) -> str:
        """格式化新闻简报"""
        today = datetime.now().strftime('%Y-%m-%d')

        briefing = f"""# 今日新闻简报
**日期**: {today}

## AI 资讯
"""

        for i, item in enumerate(news_items, 1):
            title = item.get('title', '')
            snippet = item.get('snippet', '')
            source = item.get('source', '')
            url = item.get('url', '')

            briefing += f"\n### {i}. {title}\n"

            if snippet:
                briefing += f"{snippet}\n"

            if source:
                briefing += f"📍 {source}"

            if url:
                briefing += f"  |  🔗 {url}"

            briefing += "\n\n"

        briefing += f"""
---
*生成时间: {datetime.now().strftime('%H:%M:%S')}*
*共 {len(news_items)} 条新闻*
"""

        return briefing

    def save_briefing(self, briefing: str):
        """保存新闻简报"""
        today = datetime.now()
        news_dir = PROJECT_ROOT / "data" / "news" / str(today.year) / f"{today.month:02d}" / f"{today.day:02d}"
        news_dir.mkdir(parents=True, exist_ok=True)

        news_file = news_dir / "今日新闻.md"
        with open(news_file, 'w', encoding='utf-8') as f:
            f.write(briefing)

        print(f"✅ 新闻简报已保存到: {news_file}")
        return news_file

    def get_search_queries(self) -> List[str]:
        """获取搜索查询"""
        today = datetime.now().strftime('%Y-%m-%d')

        queries = [
            f"AI新闻 {today}",
            f"人工智能 最新消息",
            f"LLM 大模型进展",
            f"GPT Claude 更新",
            f"AI技术突破 {today}",
            f"机器学习 最新",
            f"深度学习 动态",
            f"ChatGPT 新闻",
            f"Anthropic Claude",
            f"OpenAI 新闻"
        ]

        return queries

    def fetch_daily_news(self, max_news: int = 10) -> List[Dict[str, Any]]:
        """获取每日新闻"""
        print("\n" + "=" * 60)
        print("📰 开始获取今日新闻（真实搜索）")
        print("=" * 60)

        if not self.websearch_enabled:
            print("\n⚠️ WebSearch 未启用")
            print("请先配置 WebSearch API:")
            print("  python3 configure.py --websearch YOUR_API_KEY")
            return []

        if not self.api_key:
            print("\n❌ Brave API Key 未配置")
            print("请配置 Brave API Key:")
            print("  1. 访问 https://brave.com/search/api/")
            print("  2. 注册并获取 API Key")
            print("  3. 运行: python3 configure.py --websearch YOUR_API_KEY")
            return []

        # 获取搜索查询
        queries = self.get_search_queries()

        # 搜索新闻
        search_results = self.search_news(queries, max_news * 2)

        print(f"\n📋 搜索到 {len(search_results)} 条结果")

        if not search_results:
            print("\n⚠️ 没有搜索到结果")
            return []

        # 去重
        unique_news = self.deduplicate_news(search_results)

        # 过滤相关性
        keywords = ['AI', '人工智能', 'GPT', 'Claude', 'LLM', '大模型', '机器学习', '深度学习']
        relevant_news = self.filter_by_relevance(unique_news, keywords)

        # 排序
        ranked_news = self.rank_news(relevant_news)

        # 限制数量
        final_news = ranked_news[:max_news]

        print(f"✅ 最终获取 {len(final_news)} 条新闻")

        return final_news

def main():
    """主函数"""
    import argparse

    parser = argparse.ArgumentParser(description='真实新闻获取脚本（使用 WebSearch）')
    parser.add_argument('--max', type=int, default=10, help='最大新闻数量')
    parser.add_argument('--save', action='store_true', help='保存到文件')

    args = parser.parse_args()

    # 创建新闻获取器
    fetcher = RealNewsFetcher()

    # 获取新闻
    news_items = fetcher.fetch_daily_news(max_news=args.max)

    if not news_items:
        print("\n❌ 没有获取到新闻")
        sys.exit(1)

    # 格式化简报
    briefing = fetcher.format_news_briefing(news_items)

    # 输出简报
    print("\n" + "=" * 60)
    print("📋 今日新闻简报")
    print("=" * 60)
    print(briefing)

    # 保存到文件
    if args.save:
        fetcher.save_briefing(briefing)

    print("\n" + "=" * 60)
    print("✅ 新闻获取完成")
    print("=" * 60)

if __name__ == "__main__":
    main()
