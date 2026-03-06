#!/usr/bin/env python3
"""
真实新闻获取脚本
使用 WebSearch + WebFetch 获取新闻
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

class NewsFetcher:
    """新闻获取器"""

    def __init__(self):
        self.config = self.load_config()
        self.websearch_enabled = self.config.get('websearch', {}).get('enabled', False)

    def load_config(self) -> Dict[str, Any]:
        """加载配置"""
        config_path = PROJECT_ROOT / "config" / "config.yaml"
        if not config_path.exists():
            return {}

        with open(config_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)

    def search_news(self, queries: List[str], max_results: int = 10) -> List[Dict[str, Any]]:
        """搜索新闻"""
        all_results = []

        for query in queries:
            print(f"🔍 搜索: {query}")
            results = self.web_search(query, max_results)
            all_results.extend(results)

        return all_results

    def web_search(self, query: str, max_results: int = 10) -> List[Dict[str, Any]]:
        """执行 Web 搜索"""
        # 使用 WebSearch 工具进行真实搜索
        try:
            from websearch import WebSearch

            searcher = WebSearch()

            # 执行搜索
            results = searcher.search(
                query=query,
                max_results=max_results
            )

            # 转换搜索结果
            search_results = []
            for result in results:
                search_results.append({
                    'title': result.get('title', ''),
                    'url': result.get('url', ''),
                    'snippet': result.get('snippet', ''),
                    'source': self.extract_source(result.get('url', '')),
                    'date': datetime.now().strftime('%Y-%m-%d')
                })

            return search_results

        except Exception as e:
            print(f"⚠️ 搜索失败: {e}")
            # 返回空结果
            return []

    def fetch_article_content(self, url: str) -> str:
        """获取文章内容"""
        # TODO: 使用 WebFetch 工具
        # 目前返回模拟内容

        return f"这是从 {url} 获取的文章内容..."

    def parse_article(self, url: str, content: str) -> Dict[str, Any]:
        """解析文章"""
        # TODO: 实现文章解析逻辑
        # 提取标题、摘要、关键词等

        return {
            'title': '模拟标题',
            'summary': '模拟摘要',
            'content': content,
            'url': url,
            'source': self.extract_source(url),
            'date': datetime.now().strftime('%Y-%m-%d'),
            'keywords': []
        }

    def extract_source(self, url: str) -> str:
        """从URL提取来源"""
        try:
            from urllib.parse import urlparse
            domain = urlparse(url).netloc
            # 移除 www. 前缀
            if domain.startswith('www.'):
                domain = domain[4:]
            return domain
        except:
            return '未知来源'

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

    def rank_news(self, news_items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """排序新闻"""
        # 按日期排序（最新的在前）
        def sort_key(item):
            date_str = item.get('date', '')
            try:
                return datetime.strptime(date_str, '%Y-%m-%d')
            except:
                return datetime.min

        return sorted(news_items, key=sort_key, reverse=True)

    def filter_by_relevance(self, news_items: List[Dict[str, Any]], keywords: List[str]) -> List[Dict[str, Any]]:
        """过滤相关性"""
        filtered = []

        for item in news_items:
            title = item.get('title', '').lower()
            summary = item.get('summary', '').lower()

            # 检查是否包含关键词
            relevant = any(
                keyword.lower() in title or keyword.lower() in summary
                for keyword in keywords
            )

            if relevant or not keywords:
                filtered.append(item)

        return filtered

    def format_news_briefing(self, news_items: List[Dict[str, Any]]) -> str:
        """格式化新闻简报"""
        today = datetime.now().strftime('%Y-%m-%d')

        briefing = f"""# 今日新闻简报
**日期**: {today}

## AI 资讯
"""

        for i, item in enumerate(news_items, 1):
            title = item.get('title', '')
            summary = item.get('summary', '')
            source = item.get('source', '')
            url = item.get('url', '')

            briefing += f"\n### {i}. {title}\n"

            if summary:
                briefing += f"{summary}\n"

            briefing += f"\n📍 来源: {source}"
            if url:
                briefing += f"\n🔗 链接: {url}"

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
        # 基于配置的新闻源生成搜索查询
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
        print("📰 开始获取今日新闻")
        print("=" * 60)

        if not self.websearch_enabled:
            print("⚠️ WebSearch 未启用，使用模拟数据")
            return self._get_mock_news()

        # 获取搜索查询
        queries = self.get_search_queries()

        # 搜索新闻
        search_results = self.search_news(queries, max_news * 2)

        print(f"\n📋 搜索到 {len(search_results)} 条结果")

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

    def _get_mock_news(self) -> List[Dict[str, Any]]:
        """获取模拟新闻（用于测试）"""
        today = datetime.now().strftime('%Y-%m-%d')

        mock_news = [
            {
                'title': f'Claude 4.6 发布重大更新，推理能力提升50% ({today})',
                'summary': 'Anthropic 发布了 Claude 4.6 模型，在推理能力和多模态理解方面有显著提升，特别是在代码生成和数学推理方面表现出色。',
                'content': '详细内容...',
                'url': 'https://openai.com/blog/claude-4-6',
                'source': 'OpenAI Blog',
                'date': today,
                'keywords': ['Claude', 'Anthropic', 'AI', 'LLM']
            },
            {
                'title': f'新智元：大模型在医疗领域取得突破性进展 ({today})',
                'summary': '最新的研究显示，大语言模型在医疗诊断和治疗方案制定方面已经达到专家水平，准确率超过90%。',
                'content': '详细内容...',
                'url': 'https://www.zhidx.com/article/12345',
                'source': '新智元',
                'date': today,
                'keywords': ['大模型', '医疗', 'AI']
            },
            {
                'title': f'AI科技评论：Agent 架构成为新热点 ({today})',
                'summary': 'AI Agent 正在成为新的技术热点，多家公司发布相关产品和解决方案，预计将重塑人机交互方式。',
                'content': '详细内容...',
                'url': 'https://www.leiphone.com/article/67890',
                'source': 'AI科技评论',
                'date': today,
                'keywords': ['Agent', '架构', 'AI']
            },
            {
                'title': f'IT之家：国内多家公司发布AI新品 ({today})',
                'summary': '国内多家科技公司发布基于大模型的AI产品，涵盖办公、教育、金融等多个领域。',
                'content': '详细内容...',
                'url': 'https://www.ithome.com/0/678/901.htm',
                'source': 'IT之家',
                'date': today,
                'keywords': ['AI', '产品', '公司']
            }
        ]

        return mock_news

def main():
    """主函数"""
    import argparse

    parser = argparse.ArgumentParser(description='真实新闻获取脚本')
    parser.add_argument('--max', type=int, default=10, help='最大新闻数量')
    parser.add_argument('--mock', action='store_true', help='使用模拟数据')
    parser.add_argument('--save', action='store_true', help='保存到文件')

    args = parser.parse_args()

    # 创建新闻获取器
    fetcher = NewsFetcher()

    # 获取新闻
    if args.mock:
        print("\n🔧 使用模拟数据模式")
        news_items = fetcher._get_mock_news()
    else:
        news_items = fetcher.fetch_daily_news(max_news=args.max)

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
