#!/usr/bin/env python3
"""
新闻获取脚本
从配置的新闻源获取最新新闻
"""

import sys
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any

# 添加项目根目录到 Python 路径
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

def load_config() -> Dict[str, Any]:
    """加载配置"""
    import yaml

    config_path = PROJECT_ROOT / "config" / "config.yaml"
    if not config_path.exists():
        return {}

    with open(config_path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)

def fetch_news_from_source(source_url: str) -> List[Dict[str, str]]:
    """从单个新闻源获取新闻"""
    # TODO: 实现真实的新闻抓取逻辑
    # 这里需要根据不同网站的特点实现抓取逻辑

    news_items = []

    # 模拟数据（实际使用时替换为真实抓取）
    return news_items

def fetch_news_from_priority_sources() -> List[Dict[str, str]]:
    """从优先新闻源获取新闻"""
    config = load_config()
    sources = config.get('preferences', {}).get('news', {}).get('priority_sources', [])

    all_news = []
    for source in sources:
        news_items = fetch_news_from_source(source)
        all_news.extend(news_items)

    return all_news

def fetch_news_from_all_sources() -> List[Dict[str, str]]:
    """从所有新闻源获取新闻"""
    config = load_config()
    sources = config.get('preferences', {}).get('news', {}).get('sources', [])

    all_news = []
    for source in sources:
        news_items = fetch_news_from_source(source)
        all_news.extend(news_items)

    return all_news

def deduplicate_news(news_items: List[Dict[str, str]]) -> List[Dict[str, str]]:
    """去重新闻"""
    seen = set()
    unique_news = []

    for item in news_items:
        # 使用标题作为去重依据
        key = item.get('title', '').strip().lower()
        if key and key not in seen:
            seen.add(key)
            unique_news.append(item)

    return unique_news

def rank_news(news_items: List[Dict[str, str]]) -> List[Dict[str, str]]:
    """对新闻进行排序"""
    # TODO: 实现新闻排序逻辑
    # 可以基于以下因素排序：
    # - 时间（越新越好）
    # - 来源（优先源优先）
    # - 内容质量
    # - 相关性（AI相关度）

    return news_items

def format_news_item(item: Dict[str, str]) -> str:
    """格式化单个新闻项"""
    title = item.get('title', '')
    summary = item.get('summary', '')
    source = item.get('source', '')
    url = item.get('url', '')

    formatted = f"- {title}"
    if summary:
        formatted += f"\n  {summary}"
    if source:
        formatted += f" ({source})"
    if url:
        formatted += f"\n  🔗 {url}"

    return formatted

def save_news_to_file(news_items: List[Dict[str, str]], date: str):
    """保存新闻到文件"""
    news_dir = PROJECT_ROOT / "data" / "news" / date
    news_dir.mkdir(parents=True, exist_ok=True)

    news_file = news_dir / "今日新闻.md"

    with open(news_file, 'w', encoding='utf-8') as f:
        f.write(f"# 今日新闻简报\n")
        f.write(f"**日期**: {date}\n\n")

        f.write("## AI 资讯\n")
        for item in news_items:
            f.write(format_news_item(item) + "\n\n")

        f.write(f"---\n")
        f.write(f"*生成时间: {datetime.now().strftime('%H:%M:%S')}*\n")
        f.write(f"*共 {len(news_items)} 条新闻*\n")

    print(f"✅ 新闻已保存到: {news_file}")

def main():
    """主函数"""
    import argparse

    parser = argparse.ArgumentParser(description='新闻获取脚本')
    parser.add_argument('--all', action='store_true', help='从所有源获取新闻')
    parser.add_argument('--priority', action='store_true', help='仅从优先源获取新闻')
    parser.add_argument('--limit', type=int, default=10, help='限制新闻数量')

    args = parser.parse_args()

    print("\n" + "=" * 60)
    print("📰 新闻获取脚本")
    print("=" * 60)

    today = datetime.now().strftime('%Y-%m-%d')

    # 获取新闻
    if args.priority:
        print("\n🎯 从优先新闻源获取...")
        news_items = fetch_news_from_priority_sources()
    elif args.all:
        print("\n🌐 从所有新闻源获取...")
        news_items = fetch_news_from_all_sources()
    else:
        print("\n🎯 从优先新闻源获取...")
        news_items = fetch_news_from_priority_sources()

    # 去重
    news_items = deduplicate_news(news_items)

    # 排序
    news_items = rank_news(news_items)

    # 限制数量
    if args.limit and len(news_items) > args.limit:
        news_items = news_items[:args.limit]

    print(f"\n📋 获取到 {len(news_items)} 条新闻")

    # 保存到文件
    save_news_to_file(news_items, today)

    print("\n" + "=" * 60)
    print("✅ 新闻获取完成")
    print("=" * 60)

if __name__ == "__main__":
    main()
