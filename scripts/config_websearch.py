#!/usr/bin/env python3
"""
WebSearch 配置工具
"""

import sys
import yaml
from pathlib import Path

# 添加项目根目录到 Python 路径
PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))

def config_websearch_api(api_key: str):
    """配置 WebSearch API"""
    config_path = PROJECT_ROOT / "config" / "config.yaml"

    # 读取现有配置
    if config_path.exists():
        with open(config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
    else:
        config = {}

    # 确保相关结构存在
    if 'websearch' not in config:
        config['websearch'] = {}
    if 'mcpServers' not in config:
        config['mcpServers'] = {}

    # 更新主配置
    config['websearch']['enabled'] = True
    config['websearch']['search_engine'] = 'brave'
    config['websearch']['max_results'] = 10
    config['websearch']['timeout'] = 30

    # 更新 MCP 配置
    if 'websearch' not in config['mcpServers']:
        config['mcpServers']['websearch'] = {
            'command': 'npx',
            'args': ['-y', '@modelcontextprotocol/server-brave-search'],
            'env': {}
        }

    config['mcpServers']['websearch']['env']['BRAVE_API_KEY'] = api_key

    # 保存配置
    with open(config_path, 'w', encoding='utf-8') as f:
        yaml.dump(config, default_flow_style=False, allow_unicode=True)

    print("✅ WebSearch API 已配置")
    print(f"   API Key: {api_key[:10]}...{api_key[-4:]}")
    print("   已启用: true")
    print("   搜索引擎: brave")

def test_websearch_config():
    """测试 WebSearch 配置"""
    config_path = PROJECT_ROOT / "config" / "config.yaml"

    if not config_path.exists():
        print("❌ 配置文件不存在")
        return False

    with open(config_path, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)

    websearch_config = config.get('websearch', {})
    mcp_config = config.get('mcpServers', {}).get('websearch', {})

    print("\n" + "=" * 60)
    print("🔍 WebSearch 配置状态")
    print("=" * 60)

    print(f"\n主配置:")
    print(f"  启用状态: {websearch_config.get('enabled', False)}")
    print(f"  搜索引擎: {websearch_config.get('search_engine', 'default')}")
    print(f"  最大结果: {websearch_config.get('max_results', 10)}")

    print(f"\nMCP 配置:")
    print(f"  命令: {mcp_config.get('command', 'N/A')}")
    print(f"  参数: {' '.join(mcp_config.get('args', []))}")

    api_key = mcp_config.get('env', {}).get('BRAVE_API_KEY', '')
    if api_key:
        print(f"  API Key: {api_key[:10]}...{api_key[-4:]}")
    else:
        print(f"  API Key: ❌ 未配置")

    print("\n" + "=" * 60)

    return bool(api_key)

def main():
    """主函数"""
    import argparse

    parser = argparse.ArgumentParser(description='WebSearch 配置工具')
    parser.add_argument('--config', type=str, help='配置 API Key')
    parser.add_argument('--test', action='store_true', help='测试配置')

    args = parser.parse_args()

    if args.config:
        config_websearch_api(args.config)
    elif args.test:
        test_websearch_config()
    else:
        print("请使用 --config 配置 API Key 或 --test 测试配置")
        print("\n示例:")
        print("  python3 config_websearch.py --config YOUR_API_KEY")
        print("  python3 config_websearch.py --test")

if __name__ == "__main__":
    main()
