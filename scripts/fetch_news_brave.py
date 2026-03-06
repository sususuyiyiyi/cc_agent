#!/usr/bin/env python3
"""
使用 Brave MCP 获取真实新闻
"""
import sys
import json
import subprocess
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any

# 添加项目根目录到 Python 路径
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

class BraveNewsFetcher:
    """使用 Brave MCP 获取新闻"""

    def __init__(self):
        self.config = self._load_config()

    def _load_config(self) -> Dict[str, Any]:
        """加载配置"""
        import yaml
        config_path = PROJECT_ROOT / "config" / "news_apis.yaml"
        if not config_path.exists():
            return {}
        with open(config_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)

    def search_brave(self, query: str, count: int = 10) -> List[Dict[str, Any]]:
        """使用 Brave 搜索新闻"""
        try:
            # 检查是否安装了 MCP 客户端
            result = subprocess.run(
                ['which', 'mcp-client'],
                capture_output=True,
                text=True
            )

            if result.returncode != 0:
                print("⚠️ MCP 客户端未安装")
                print("请先安装 MCP 客户端: npm install -g @smithery/mcp-client")
                return []

            # 构建搜索请求
            search_request = {
                "jsonrpc": "2.0",
                "method": "tools/call",
                "params": {
                    "name": "search",
                    "arguments": {
                        "query": query
                    }
                },
                "id": 1
            }

            # 调用 MCP 客户端
            process = subprocess.Popen(
                ['mcp-client', 'call'],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )

            stdout, stderr = process.communicate(
                input=json.dumps(search_request),
                timeout=30
            )

            if process.returncode != 0:
                print(f"⚠️ 搜索失败: {stderr}")
                return []

            # 解析结果
            response = json.loads(stdout)

            if 'result' in response:
                results = response['result'].get('content', [])
                return self._parse_search_results(results)

            return []

        except subprocess.TimeoutExpired:
            print("⚠️ 搜索超时")
            return []
        except Exception as e:
            print(f"⚠️ 搜索错误: {e}")
            return []

    def _parse_search_results(self, results: List[Any]) -> List[Dict[str, Any]]:
        """解析搜索结果"""
        news_items = []

        for result in results:
            if isinstance(result, str):
                # 尝试解析文本结果
                continue
            elif isinstance(result, dict):
                news_items.append({
                    'title': result.get('title', ''),
                    'url': result.get('url', ''),
                    'snippet': result.get('snippet', result.get('description', '')),
                    'source': self._extract_source(result.get('url', '')),
                    'date': datetime.now().strftime('%Y-%m-%d')
                })

        return news_items

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
        print("📰 使用 Brave 获取今日新闻")
        print("=" * 60)

        today = datetime.now().strftime('%Y-%m-%d')

        # 搜索查询
        queries = [
            f"AI新闻 {today}",
            "人工智能 最新消息",
            "OpenAI ChatGPT",
            "Anthropic Claude",
            "大模型 LLM",
            "机器学习 深度学习",
            "科技新闻 AI"
        ]

        all_news = []

        for query in queries:
            print(f"🔍 搜索: {query}")
            results = self.search_brave(query, count=3)
            all_news.extend(results)

        # 去重
        seen_titles = set()
        unique_news = []

        for news in all_news:
            title = news.get('title', '').strip().lower()
            if title and title not in seen_titles:
                seen_titles.add(title)
                unique_news.append(news)

        # 限制数量
        final_news = unique_news[:max_news]

        print(f"✅ 获取到 {len(final_news)} 条新闻")
        return final_news

def main():
    """主函数"""
    fetcher = BraveNewsFetcher()
    news_items = fetcher.fetch_daily_news()

    # 输出新闻
    print("\n📋 今日新闻简报:")
    for i, item in enumerate(news_items, 1):
        print(f"\n{i}. {item.get('title', '')}")
        print(f"   {item.get('snippet', '')}")
        print(f"   📍 {item.get('source', '')}")

if __name__ == "__main__":
    main()
