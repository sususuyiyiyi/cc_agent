#!/usr/bin/env python3
"""
MCP 工具包装器
用于配置和访问 MCP 工具
"""

import json
import os
from pathlib import Path
from typing import Dict, Any, Optional

# MCP 工具配置路径
MCP_CONFIG_PATH = Path(__file__).parent / "config" / "mcp_config.json"

class MCPTools:
    """MCP 工具管理器"""

    def __init__(self, config_path: Optional[Path] = None):
        self.config_path = config_path or MCP_CONFIG_PATH
        self.config = self._load_config()

    def _load_config(self) -> Dict[str, Any]:
        """加载 MCP 配置"""
        if not self.config_path.exists():
            return {"mcpServers": {}}

        with open(self.config_path, 'r', encoding='utf-8') as f:
            return json.load(f)

    def _save_config(self):
        """保存 MCP 配置"""
        with open(self.config_path, 'w', encoding='utf-8') as f:
            json.dump(self.config, f, indent=2, ensure_ascii=False)

    def get_server_config(self, server_name: str) -> Optional[Dict[str, Any]]:
        """获取指定 MCP 服务器配置"""
        return self.config.get("mcpServers", {}).get(server_name)

    def list_servers(self) -> list:
        """列出所有配置的 MCP 服务器"""
        return list(self.config.get("mcpServers", {}).keys())

    def update_server_env(self, server_name: str, env_vars: Dict[str, str]):
        """更新服务器的环境变量"""
        servers = self.config.get("mcpServers", {})
        if server_name in servers:
            servers[server_name]["env"].update(env_vars)
            self._save_config()
            return True
        return False

    def enable_server(self, server_name: str):
        """启用服务器"""
        # 在实际实现中，这会连接到 MCP 服务器
        print(f"✅ MCP 服务器已启用: {server_name}")

    def disable_server(self, server_name: str):
        """禁用服务器"""
        # 在实际实现中，这会断开与 MCP 服务器的连接
        print(f"❌ MCP 服务器已禁用: {server_name}")

    def check_server_status(self, server_name: str) -> str:
        """检查服务器状态"""
        config = self.get_server_config(server_name)
        if not config:
            return "未配置"

        # 检查必需的环境变量
        required_keys = self._get_required_env_keys(server_name)
        env = config.get("env", {})

        for key in required_keys:
            if not env.get(key):
                return "配置不完整"

        return "已配置"

    def _get_required_env_keys(self, server_name: str) -> list:
        """获取服务器必需的环境变量"""
        required_keys = {
            "websearch": ["BRAVE_API_KEY"],
            "postgres": [],  # 连接字符串在 args 中
        }
        return required_keys.get(server_name, [])

def show_mcp_status():
    """显示 MCP 工具状态"""
    print("\n" + "=" * 60)
    print("🔧 MCP 工具状态")
    print("=" * 60)

    mcp_tools = MCPTools()
    servers = mcp_tools.list_servers()

    if not servers:
        print("\n❌ 未配置任何 MCP 服务器")
        return

    print(f"\n已配置的 MCP 服务器 ({len(servers)} 个):")
    for server in servers:
        status = mcp_tools.check_server_status(server)
        config = mcp_tools.get_server_config(server)

        print(f"\n📦 {server}")
        print(f"   状态: {status}")
        print(f"   命令: {config.get('command', 'N/A')}")
        print(f"   参数: {' '.join(config.get('args', []))}")

    print("\n" + "=" * 60)

def configure_websearch(api_key: str):
    """配置 WebSearch 工具"""
    mcp_tools = MCPTools()
    mcp_tools.update_server_env("websearch", {"BRAVE_API_KEY": api_key})
    print("✅ WebSearch 配置已更新")

def configure_weather(api_key: str, provider: str = "openweathermap"):
    """配置天气 API"""
    # 这个配置会保存到 config.yaml
    config_path = Path(__file__).parent / "config" / "config.yaml"

    # 读取现有配置
    import yaml
    with open(config_path, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)

    # 更新配置
    if provider == "openweathermap":
        config['weather']['openweathermap']['api_key'] = api_key
    elif provider == "qweather":
        config['weather']['qweather']['api_key'] = api_key

    config['weather']['enabled'] = True

    # 保存配置
    with open(config_path, 'w', encoding='utf-8') as f:
        yaml.dump(config, f, default_flow_style=False, allow_unicode=True)

    print(f"✅ 天气 API 配置已更新 ({provider})")

def configure_feishu(webhook_url: str):
    """配置飞书集成"""
    config_path = Path(__file__).parent / "config" / "config.yaml"

    # 读取现有配置
    import yaml
    with open(config_path, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)

    # 更新配置
    config['feishu']['enabled'] = True
    config['feishu']['webhook_url'] = webhook_url

    # 保存配置
    with open(config_path, 'w', encoding='utf-8') as f:
        yaml.dump(config, f, default_flow_style=False, allow_unicode=True)

    print("✅ 飞书集成配置已更新")

def enable_scheduling():
    """启用定时任务"""
    config_path = Path(__file__).parent / "config" / "config.yaml"

    # 读取现有配置
    import yaml
    with open(config_path, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)

    # 更新配置
    config['scheduling']['enabled'] = True

    # 保存配置
    with open(config_path, 'w', encoding='utf-8') as f:
        yaml.dump(config, f, default_flow_style=False, allow_unicode=True)

    print("✅ 定时任务已启用")

def show_configuration_guide():
    """显示配置指南"""
    print("\n" + "=" * 60)
    print("📖 配置指南")
    print("=" * 60)

    print("""
1. WebSearch 配置
   - 注册 Brave Search API: https://brave.com/search/api/
   - 获取 API Key
   - 运行: python3 configure.py --websearch YOUR_API_KEY

2. 天气 API 配置
   选项 A - OpenWeatherMap:
   - 注册: https://openweathermap.org/api
   - 获取 API Key
   - 运行: python3 configure.py --weather openweathermap YOUR_API_KEY

   选项 B - 和风天气:
   - 注册: https://dev.qweather.com/
   - 获取 API Key
   - 运行: python3 configure.py --weather qweather YOUR_API_KEY

3. 飞书集成配置
   - 创建飞书群聊
   - 添加群机器人，获取 Webhook URL
   - 运行: python3 configure.py --feishu YOUR_WEBHOOK_URL

4. 启用定时任务
   - 运行: python3 configure.py --enable-scheduling

5. 查看状态
   - 运行: python3 configure.py --status
""")

    print("=" * 60)

if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        show_configuration_guide()
    elif sys.argv[1] == "--status":
        show_mcp_status()
    elif sys.argv[1] == "--websearch" and len(sys.argv) > 2:
        configure_websearch(sys.argv[2])
    elif sys.argv[1] == "--weather" and len(sys.argv) > 3:
        configure_weather(sys.argv[3], sys.argv[2])
    elif sys.argv[1] == "--feishu" and len(sys.argv) > 2:
        configure_feishu(sys.argv[2])
    elif sys.argv[1] == "--enable-scheduling":
        enable_scheduling()
    else:
        show_configuration_guide()
