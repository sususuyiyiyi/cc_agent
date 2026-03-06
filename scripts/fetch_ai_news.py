#!/usr/bin/env python3
"""
专门的AI新闻获取器
专注于获取以下类型的AI新闻：
- 最新AI技术突破
- 大语言模型发展
- AI应用和产品发布
- AI研究和论文
- AI行业动态和投资
- AI伦理和监管新闻
"""
import sys
import json
import requests
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Dict, Any
import re
from urllib.parse import urljoin

# 添加项目根目录到 Python 路径
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

class AIKeywords:
    """AI相关关键词分类"""

    # 技术突破关键词
    TECH_BREAKTHROUGH = [
        'breakthrough', 'breakthroughs', 'break', 'breakthrough',
        'breakthrough', 'milestone', 'milestones', 'discovery',
        'breakthrough', 'breakthrough', 'breakthrough', 'breakthrough',
        '突破', '里程碑', '重大突破', '新发现', '进展'
    ]

    # 大语言模型关键词
    LLM = [
        'LLM', 'Large Language Model', 'language model', 'transformer',
        'GPT', 'Claude', 'Gemini', 'Llama', 'Mistral', 'BERT', 'T5',
        '大语言模型', '语言模型', 'Transformer', 'GPT', 'Claude',
        'Gemini', 'Llama', '大模型', '预训练模型'
    ]

    # AI应用和产品关键词
    APPLICATIONS = [
        'application', 'applications', 'product launch', 'released',
        'launch', 'released', 'new product', 'update', 'feature',
        '应用', '产品发布', '发布', '新产品', '更新', '功能',
        '落地', '应用场景', '商业化'
    ]

    # 研究和论文关键词
    RESEARCH = [
        'research', 'paper', 'study', 'arxiv', '论文', '研究',
        'study', 'publication', 'scientific', 'academic',
        'preprint', 'conference', 'Nature', 'Science', 'ICML',
        'NeurIPS', 'CVPR', 'ACL', 'ICLR'
    ]

    # 行业动态和投资关键词
    INDUSTRY = [
        'investment', 'funding', 'startup', 'venture capital',
        'round', 'Series', 'funding', 'acquisition', 'M&A',
        '投资', '融资', '创业', '风投', '轮次', '收购',
        '并购', 'IPO', '估值', '市场', '产业', '竞争'
    ]

    # 伦理和监管关键词
    ETHICS = [
        'ethics', 'regulation', 'policy', 'law', 'government',
        'AI ethics', 'AI safety', 'AI alignment', '监管',
        '伦理', '法规', '政策', '法律', '政府', '安全',
        '对齐', '风险', '治理', '准则', '规范'
    ]

class AIWebScraper:
    """AI新闻网页爬虫"""

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        })

    def fetch_arxiv_papers(self, limit: int = 5) -> List[Dict[str, Any]]:
        """获取ArXiv最新AI论文"""
        papers = []

        try:
            # 搜索AI相关论文
            url = "http://export.arxiv.org/api/query"
            params = {
                'search_query': 'cat:cs.AI OR cat:cs.LG OR cat:cs.CL OR cat:cs.CV',
                'start': 0,
                'max_results': limit,
                'sortBy': 'submittedDate',
                'sortOrder': 'descending'
            }

            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()

            # 解析XML响应
            from xml.etree import ElementTree as ET

            root = ET.fromstring(response.content)

            for entry in root.findall('{http://www.w3.org/2005/Atom}entry'):
                title = entry.find('{http://www.w3.org/2005/Atom}title').text
                authors = [author.find('{http://www.w3.org/2005/Atom}name').text
                          for author in entry.findall('{http://www.w3.org/2005/Atom}author')]
                summary = entry.find('{http://www.w3.org/2005/Atom}summary').text
                published = entry.find('{http://www.w3.org/2005/Atom}published').text
                link = entry.find('{http://www.w3.org/2005/Atom}id').text

                papers.append({
                    'title': title,
                    'authors': authors,
                    'summary': summary[:200],
                    'published': published[:10],
                    'link': link,
                    'category': 'research',
                    'source': 'ArXiv'
                })

        except Exception as e:
            print(f"⚠️ ArXiv获取失败: {e}")

        return papers

    def fetch_ai_news_sites(self) -> List[Dict[str, Any]]:
        """从AI新闻网站获取新闻"""
        all_news = []

        # AI新闻RSS源
        rss_feeds = [
            {
                'name': 'MIT Technology Review AI',
                'url': 'https://www.technologyreview.com/topic/artificial-intelligence/feed/',
                'category': 'tech'
            },
            {
                'name': 'VentureBeat AI',
                'url': 'https://venturebeat.com/category/ai/feed/',
                'category': 'industry'
            },
            {
                'name': 'AI News',
                'url': 'https://artificialintelligence-news.com/feed/',
                'category': 'general'
            }
        ]

        for feed in rss_feeds:
            try:
                print(f"🔍 获取 {feed['name']}...")
                response = self.session.get(feed['url'], timeout=10)
                response.raise_for_status()

                # 简单解析RSS（实际项目中应使用feedparser）
                content = response.text

                # 提取标题和链接（简化版）
                title_pattern = r'<title>(.*?)</title>'
                link_pattern = r'<link>(.*?)</link>'

                titles = re.findall(title_pattern, content)
                links = re.findall(link_pattern, content)

                # 过滤出AI相关内容
                for i, title in enumerate(titles):
                    if i < len(links) and self._is_ai_related(title):
                        all_news.append({
                            'title': title,
                            'url': links[i],
                            'snippet': f"来自 {feed['name']}",
                            'published': datetime.now().strftime('%Y-%m-%d'),
                            'category': feed['category'],
                            'source': feed['name']
                        })

            except Exception as e:
                print(f"⚠️ {feed['name']}获取失败: {e}")

        return all_news

    def _is_ai_related(self, text: str) -> bool:
        """判断文本是否与AI相关"""
        ai_keywords = AIKeywords.LLM + AIKeywords.TECH_BREAKTHROUGH + AIKeywords.APPLICATIONS
        text_lower = text.lower()
        return any(keyword.lower() in text_lower for keyword in ai_keywords)

class AIKeywordSearcher:
    """AI关键词搜索器"""

    def __init__(self):
        self.api_key = None
        self._load_config()

    def _load_config(self):
        """加载配置"""
        try:
            import yaml

            config_path = PROJECT_ROOT / "config" / "news_apis.yaml"
            if config_path.exists():
                with open(config_path, 'r', encoding='utf-8') as f:
                    config = yaml.safe_load(f)
                    newsapi_config = config.get('newsapi', {})
                    if newsapi_config.get('enabled'):
                        self.api_key = newsapi_config.get('api_key')
        except:
            pass

    def search_news_with_keywords(self, keywords: List[str], limit: int = 5) -> List[Dict[str, Any]]:
        """使用关键词搜索新闻"""
        all_news = []

        if not self.api_key:
            print("⚠️ 未配置NewsAPI，跳过关键词搜索")
            return all_news

        try:
            base_url = "https://newsapi.org/v2/everything"

            # 搜索中文AI新闻
            for keyword in keywords:
                params = {
                    'q': keyword,
                    'apiKey': self.api_key,
                    'language': 'zh',
                    'sortBy': 'publishedAt',
                    'pageSize': limit,
                    'domains': 'zhuanlan.zhihu.com,juejin.cn,36kr.com,ithome.com'
                }

                response = requests.get(base_url, params=params, timeout=10)
                response.raise_for_status()

                data = response.json()

                if data.get('articles'):
                    for article in data['articles'][:limit]:
                        all_news.append({
                            'title': article.get('title', ''),
                            'snippet': article.get('description', '')[:200],
                            'url': article.get('url', ''),
                            'published': article.get('publishedAt', '')[:10],
                            'source': article.get('source', {}).get('name', 'Unknown'),
                            'category': self._classify_news(article.get('title', '')),
                            'search_keyword': keyword
                        })

        except Exception as e:
            print(f"⚠️ 新闻搜索失败: {e}")

        return all_news

    def _classify_news(self, title: str) -> str:
        """根据标题分类新闻"""
        title_lower = title.lower()

        for category, keywords in {
            'tech': AIKeywords.TECH_BREAKTHROUGH,
            'llm': AIKeywords.LLM,
            'applications': AIKeywords.APPLICATIONS,
            'research': AIKeywords.RESEARCH,
            'industry': AIKeywords.INDUSTRY,
            'ethics': AIKeywords.ETHICS
        }.items():
            if any(keyword.lower() in title_lower for keyword in keywords):
                return category

        return 'general'

class AINewsFetcher:
    """AI新闻获取器"""

    def __init__(self):
        self.web_scraper = AIWebScraper()
        self.keyword_searcher = AIKeywordSearcher()

    def fetch_all_ai_news(self, max_news: int = 15) -> List[Dict[str, Any]]:
        """获取所有AI新闻"""
        print("\n" + "=" * 60)
        print("🤖 AI 专用新闻获取器")
        print("=" * 60)

        all_news = []

        # 1. 获取ArXiv论文
        print("\n📚 获取最新AI研究论文...")
        papers = self.web_scraper.fetch_arxiv_papers(limit=3)
        all_news.extend(papers)
        print(f"✅ 获取到 {len(papers)} 篇论文")

        # 2. 从AI新闻网站获取
        print("\n📰 从AI新闻网站获取...")
        site_news = self.web_scraper.fetch_ai_news_sites()
        all_news.extend(site_news)
        print(f"✅ 获取到 {len(site_news)} 条新闻")

        # 3. 使用关键词搜索
        print("\n🔍 使用关键词搜索...")
        search_keywords = [
            '人工智能', 'AI', '机器学习', '深度学习',
            '大语言模型', 'GPT', 'ChatGPT', 'OpenAI'
        ]

        searched_news = []
        for keyword in search_keywords[:3]:  # 限制搜索次数
            print(f"   搜索: {keyword}")
            news = self.keyword_searcher.search_news_with_keywords([keyword], limit=2)
            searched_news.extend(news)

        all_news.extend(searched_news)
        print(f"✅ 搜索到 {len(searched_news)} 条新闻")

        # 4. 分类和去重
        classified_news = self._classify_and_deduplicate(all_news)

        # 5. 排序
        ranked_news = self._rank_news(classified_news)

        # 6. 限制数量
        final_news = ranked_news[:max_news]

        print(f"\n✅ 最终获取到 {len(final_news)} 条AI新闻")
        return final_news

    def _classify_and_deduplicate(self, news_items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """分类和去重新闻"""
        unique_news = []
        seen_titles = set()

        # 分类统计
        category_count = {
            'research': 0,
            'tech': 0,
            'applications': 0,
            'industry': 0,
            'ethics': 0,
            'general': 0
        }

        for item in news_items:
            # 去重
            title = item.get('title', '').strip()
            if title.lower() in seen_titles:
                continue

            seen_titles.add(title.lower())

            # 分类
            category = item.get('category', 'general')
            category_count[category] = category_count.get(category, 0) + 1

            # 确保有必要字段
            if 'source' not in item:
                item['source'] = 'Unknown'
            if 'published' not in item:
                item['published'] = datetime.now().strftime('%Y-%m-%d')

            unique_news.append(item)

        print(f"\n📊 分类统计: {category_count}")
        return unique_news

    def _rank_news(self, news_items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """按相关性排序新闻"""
        def get_score(item):
            # 研究论文权重最高
            if item.get('category') == 'research' and item.get('source') == 'ArXiv':
                return 1000

            # 新发布的新闻权重较高
            publish_date = item.get('published', '')
            if publish_date:
                try:
                    days_ago = (datetime.now() - datetime.strptime(publish_date, '%Y-%m-%d')).days
                    if days_ago <= 1:
                        return 500
                    elif days_ago <= 3:
                        return 300
                    else:
                        return 100
                except:
                    pass

            # 标题长度适中
            title_len = len(item.get('title', ''))
            if 20 <= title_len <= 100:
                return 50

            return 10

        return sorted(news_items, key=get_score, reverse=True)

    def format_ai_news_briefing(self, news_items: List[Dict[str, Any]]) -> str:
        """格式化AI新闻简报"""
        today = datetime.now().strftime('%Y-%m-%d')

        briefing = f"""# 🤖 AI 专报 - {today}

## 📋 今日概览
本报告专注于人工智能领域的最新动态，涵盖技术突破、大模型发展、应用产品、研究论文、行业动态和监管政策等。

"""

        # 按类别分组
        categories = {
            'research': ('📚 研究论文', []),
            'tech': ('⚡ 技术突破', []),
            'applications': ('🚀 应用产品', []),
            'industry': ('💼 行业动态', []),
            'ethics': ('🛡️ 监管政策', []),
            'general': ('📰 综合资讯', [])
        }

        for item in news_items:
            category = item.get('category', 'general')
            if category in categories:
                categories[category][1].append(item)

        # 输出每个类别的新闻
        for category_title, category_items in categories.values():
            if category_items:
                briefing += f"\n### {category_title}\n"
                for i, item in enumerate(category_items, 1):
                    title = item.get('title', '')
                    snippet = item.get('snippet', '')
                    source = item.get('source', 'Unknown')
                    published = item.get('published', '')
                    link = item.get('url', '')

                    briefing += f"\n{i}. **{title}**\n"
                    if snippet:
                        briefing += f"   {snippet}\n"
                    briefing += f"   📍 来源: {source} | 📅 {published}"
                    if link:
                        briefing += f" | 🔗 [阅读原文]({link})"
                    briefing += "\n"

        # 统计信息
        total_count = len(news_items)
        source_stats = {}
        for item in news_items:
            source = item.get('source', 'Unknown')
            source_stats[source] = source_stats.get(source, 0) + 1

        briefing += f"""
---

## 📊 统计信息
- **总条数**: {total_count}
- **主要来源**: {', '.join([f"{k}({v})" for k, v in source_stats.items() if v > 0])}

*生成时间: {datetime.now().strftime('%H:%M:%S')}*
"""

        return briefing

def main():
    """主函数"""
    fetcher = AINewsFetcher()
    news_items = fetcher.fetch_all_ai_news(max_news=15)

    if news_items:
        briefing = fetcher.format_ai_news_briefing(news_items)
        print("\n" + briefing)

        # 保存到文件
        output_file = PROJECT_ROOT / "ai_news_briefing.md"
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(briefing)
        print(f"\n💾 已保存到: {output_file}")
    else:
        print("❌ 未能获取到AI新闻")

if __name__ == "__main__":
    main()