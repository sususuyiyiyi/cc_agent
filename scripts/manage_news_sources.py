#!/usr/bin/env python3
"""
新闻源管理工具
添加、删除、测试新闻源
"""

import sys
import yaml
from pathlib import Path

# 添加项目根目录到 Python 路径
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

def load_config():
    """加载配置"""
    config_path = PROJECT_ROOT / "config" / "config.yaml"
    if not config_path.exists():
        return None

    with open(config_path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)

def save_config(config):
    """保存配置"""
    config_path = PROJECT_ROOT / "config" / "config.yaml"
    with open(config_path, 'w', encoding='utf-8') as f:
        yaml.dump(config, default_flow_style=False, allow_unicode=True)

def list_sources():
    """列出所有新闻源"""
    config = load_config()
    if not config:
        print("❌ 配置文件不存在")
        return

    sources = config.get('preferences', {}).get('news', {}).get('sources', [])
    priority_sources = config.get('preferences', {}).get('news', {}).get('priority_sources', [])

    print("\n" + "=" * 60)
    print("📰 新闻源列表")
    print("=" * 60)

    print(f"\n总计: {len(sources)} 个新闻源")
    print(f"优先源: {len(priority_sources)} 个\n")

    print("🎯 优先新闻源:")
    for i, source in enumerate(priority_sources, 1):
        print(f"  {i}. {source}")

    print(f"\n📋 所有新闻源:")
    for i, source in enumerate(sources, 1):
        marker = "⭐" if source in priority_sources else "  "
        print(f"  {marker} {i}. {source}")

    print("\n" + "=" * 60)

def add_source(url, priority=False):
    """添加新闻源"""
    config = load_config()
    if not config:
        print("❌ 配置文件不存在")
        return

    sources = config.get('preferences', {}).get('news', {}).get('sources', [])

    if url in sources:
        print("⚠️ 该新闻源已存在")
        return

    sources.append(url)

    if priority:
        priority_sources = config.get('preferences', {}).get('news', {}).get('priority_sources', [])
        if url not in priority_sources:
            priority_sources.append(url)

    save_config(config)

    marker = "（优先）" if priority else ""
    print(f"✅ 新闻源已添加: {url} {marker}")

def remove_source(url):
    """删除新闻源"""
    config = load_config()
    if not config:
        print("❌ 配置文件不存在")
        return

    sources = config.get('preferences', {}).get('news', {}).get('sources', [])
    priority_sources = config.get('preferences', {}).get('news', {}).get('priority_sources', [])

    if url not in sources:
        print("⚠️ 该新闻源不存在")
        return

    sources.remove(url)

    if url in priority_sources:
        priority_sources.remove(url)

    save_config(config)

    print(f"❌ 新闻源已删除: {url}")

def set_priority(url):
    """设置优先新闻源"""
    config = load_config()
    if not config:
        print("❌ 配置文件不存在")
        return

    sources = config.get('preferences', {}).get('news', {}).get('sources', [])
    priority_sources = config.get('preferences', {}).get('news', {}).get('priority_sources', [])

    if url not in sources:
        print("⚠️ 该新闻源不存在，请先添加")
        return

    if url not in priority_sources:
        priority_sources.append(url)
        save_config(config)
        print(f"⭐ 已设为优先源: {url}")
    else:
        print("⚠️ 该新闻源已经是优先源")

def unset_priority(url):
    """取消优先新闻源"""
    config = load_config()
    if not config:
        print("❌ 配置文件不存在")
        return

    priority_sources = config.get('preferences', {}).get('news', {}).get('priority_sources', [])

    if url in priority_sources:
        priority_sources.remove(url)
        save_config(config)
        print(f"⚪ 已取消优先源: {url}")
    else:
        print("⚠️ 该新闻源不是优先源")

def test_source(url):
    """测试新闻源"""
    import requests

    print(f"\n🔍 测试新闻源: {url}")

    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            print(f"✅ 可访问 (状态码: {response.status_code})")
            print(f"   内容长度: {len(response.text)} 字符")
            print(f"   Content-Type: {response.headers.get('Content-Type')}")
        else:
            print(f"⚠️ 可访问但状态异常 (状态码: {response.status_code})")
    except requests.exceptions.Timeout:
        print("❌ 访问超时")
    except requests.exceptions.ConnectionError:
        print("❌ 连接失败")
    except Exception as e:
        print(f"❌ 访问失败: {e}")

def main():
    """主函数"""
    import argparse

    parser = argparse.ArgumentParser(description='新闻源管理工具')
    parser.add_argument('--list', action='store_true', help='列出所有新闻源')
    parser.add_argument('--add', type=str, help='添加新闻源')
    parser.add_argument('--remove', type=str, help='删除新闻源')
    parser.add_argument('--priority', action='store_true', help='添加/设置为优先源')
    parser.add_argument('--unset-priority', action='store_true', help='取消优先源')
    parser.add_argument('--test', type=str, help='测试新闻源')

    args = parser.parse_args()

    if args.list:
        list_sources()
    elif args.add:
        add_source(args.add, args.priority)
    elif args.remove:
        remove_source(args.remove)
    elif args.priority and args.add:
        # 已在 add 中处理
        pass
    elif args.test:
        test_source(args.test)
    else:
        print("请使用 --help 查看帮助")

if __name__ == "__main__":
    main()
