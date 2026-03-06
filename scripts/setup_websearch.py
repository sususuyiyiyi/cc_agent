#!/usr/bin/env python3
"""
快速配置 WebSearch API
"""

import sys
import os
from pathlib import Path

# 添加项目根目录到 Python 路径
PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))

def main():
    print("\n" + "=" * 60)
    print("🔍 WebSearch API 快速配置")
    print("=" * 60)

    print("\n📋 步骤 1: 获取 API Key")
    print("1. 访问: https://brave.com/search/api/")
    print("2. 注册账号并登录")
    print("3. 创建 API Key（选择 Web Search API）")
    print("4. 复制 API Key\n")

    api_key = input("🔑 请输入您的 API Key: ").strip()

    if not api_key:
        print("\n❌ API Key 不能为空")
        return

    print(f"\n✅ API Key 已输入: {api_key[:10]}...{api_key[-4:]}")

    # 配置 MCP
    mcp_config_path = PROJECT_ROOT / "config" / "mcp_config.json"

    import json

    if mcp_config_path.exists():
        with open(mcp_config_path, 'r', encoding='utf-8') as f:
            mcp_config = json.load(f)
    else:
        mcp_config = {"mcpServers": {}}

    # 配置 websearch
    if "websearch" not in mcp_config["mcpServers"]:
        mcp_config["mcpServers"]["websearch"] = {
            "command": "npx",
            "args": ["-y", "@modelcontextprotocol/server-brave-search"],
            "env": {}
        }

    mcp_config["mcpServers"]["websearch"]["env"]["BRAVE_API_KEY"] = api_key

    with open(mcp_config_path, 'w', encoding='utf-8') as f:
        json.dump(mcp_config, indent=2, ensure_ascii=False)

    print("✅ MCP 配置已更新")

    # 配置主配置
    import yaml

    config_path = PROJECT_ROOT / "config" / "config.yaml"

    if config_path.exists():
        with open(config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
    else:
        config = {}

    # 更新 websearch 配置
    if "websearch" not in config:
        config["websearch"] = {}

    config["websearch"]["enabled"] = True
    config["websearch"]["search_engine"] = "brave"
    config["websearch"]["max_results"] = 10
    config["websearch"]["timeout"] = 30

    with open(config_path, 'w', encoding='utf-8') as f:
        yaml.dump(config, default_flow_style=False, allow_unicode=True)

    print("✅ 主配置已更新")

    # 设置环境变量（可选）
    os.environ['BRAVE_API_KEY'] = api_key
    print("✅ 环境变量已设置")

    print("\n" + "=" * 60)
    print("✅ WebSearch API 配置完成！")
    print("=" * 60)

    print("\n🧪 测试配置:")
    print("   python3 scripts/test_websearch.py")

    print("\n🚀 测试新闻获取:")
    print("   python3 scripts/fetch_news_with_websearch.py --max 3 --save")

    print("\n📖 查看详细文档:")
    print("   cat WebSearch配置完成.md")

if __name__ == "__main__":
    main()
