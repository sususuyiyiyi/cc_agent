#!/usr/bin/env python3
"""
测试 WebSearch 功能
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

def test_websearch():
    """测试 WebSearch 功能"""
    print("\n" + "=" * 60)
    print("🔍 WebSearch 测试")
    print("=" * 60)

    # 加载配置
    config = load_config()
    if not config:
        print("❌ 配置文件不存在")
        return False

    # 检查 WebSearch 是否启用
    websearch_config = config.get('websearch', {})
    enabled = websearch_config.get('enabled', False)

    if not enabled:
        print("\n❌ WebSearch 未启用")
        print("请先配置 WebSearch API:")
        print("  python3 configure.py --websearch YOUR_API_KEY")
        return False

    print(f"\n✅ WebSearch 已启用")
    print(f"   搜索引擎: {websearch_config.get('search_engine', 'default')}")
    print(f"   最大结果: {websearch_config.get('max_results', 10)}")
    print(f"   超时: {websearch_config.get('timeout', 30)}s")

    # TODO: 这里会调用实际的 WebSearch 工具
    # 目前返回测试数据
    print("\n🔍 测试搜索: 'AI新闻 今日'")

    mock_results = [
        {
            'title': 'AI 最新进展 - 模拟结果',
            'url': 'https://example.com/news/1',
            'snippet': '这是一条模拟的搜索结果...'
        },
        {
            'title': 'GPT Claude 更新 - 模拟结果',
            'url': 'https://example.com/news/2',
            'snippet': '这是另一条模拟的搜索结果...'
        }
    ]

    print(f"\n📋 搜索结果 ({len(mock_results)} 条):")
    for i, result in enumerate(mock_results, 1):
        print(f"\n{i}. {result['title']}")
        print(f"   {result['url']}")
        print(f"   {result['snippet']}")

    print("\n" + "=" * 60)
    print("✅ WebSearch 测试完成")
    print("=" * 60)

    return True

def main():
    """主函数"""
    success = test_websearch()

    if not success:
        print("\n💡 配置 WebSearch API:")
        print("1. 访问 https://brave.com/search/api/")
        print("2. 注册并获取 API Key")
        print("3. 运行: python3 configure.py --websearch YOUR_API_KEY")

if __name__ == "__main__":
    main()
