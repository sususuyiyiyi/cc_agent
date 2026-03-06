#!/usr/bin/env python3
"""
配置脚本 - 快速配置 CC Agent
"""

import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))

from mcp_tools import (
    show_mcp_status,
    configure_websearch,
    configure_weather,
    configure_feishu,
    enable_scheduling,
    show_configuration_guide
)

def main():
    """主函数"""
    print("\n" + "=" * 60)
    print("🔧 CC Agent 配置工具")
    print("=" * 60)

    if len(sys.argv) < 2:
        show_menu()
        choice = input("\n请选择配置项 (1-6): ").strip()

        if choice == '1':
            configure_websearch_interactive()
        elif choice == '2':
            configure_weather_interactive()
        elif choice == '3':
            configure_feishu_interactive()
        elif choice == '4':
            enable_scheduling()
        elif choice == '5':
            show_mcp_status()
        elif choice == '6':
            show_configuration_guide()
        else:
            print("❌ 无效的选择")
    else:
        # 命令行模式
        if sys.argv[1] == "--status":
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

def show_menu():
    """显示配置菜单"""
    print("\n可用配置项:")
    print("  1. 配置 WebSearch (Brave Search API)")
    print("  2. 配置天气 API (OpenWeatherMap / 和风天气)")
    print("  3. 配置飞书集成 (Webhook URL)")
    print("  4. 启用定时任务")
    print("  5. 查看当前配置状态")
    print("  6. 显示配置指南")

def configure_websearch_interactive():
    """交互式配置 WebSearch"""
    print("\n🔍 配置 WebSearch")
    print("\n需要 Brave Search API Key")
    print("注册地址: https://brave.com/search/api/")

    api_key = input("\n请输入您的 API Key: ").strip()
    if api_key:
        configure_websearch(api_key)
    else:
        print("❌ API Key 不能为空")

def configure_weather_interactive():
    """交互式配置天气 API"""
    print("\n🌤️ 配置天气 API")
    print("\n选择天气服务:")
    print("  1. OpenWeatherMap (推荐，免费额度较大)")
    print("  2. 和风天气 (国内服务)")

    choice = input("\n请选择 (1-2): ").strip()

    if choice == '1':
        print("\nOpenWeatherMap")
        print("注册地址: https://openweathermap.org/api")
        api_key = input("\n请输入您的 API Key: ").strip()
        if api_key:
            configure_weather(api_key, "openweathermap")
        else:
            print("❌ API Key 不能为空")
    elif choice == '2':
        print("\n和风天气")
        print("注册地址: https://dev.qweather.com/")
        api_key = input("\n请输入您的 API Key: ").strip()
        if api_key:
            configure_weather(api_key, "qweather")
        else:
            print("❌ API Key 不能为空")
    else:
        print("❌ 无效的选择")

def configure_feishu_interactive():
    """交互式配置飞书"""
    print("\n📱 配置飞书集成")
    print("\n创建飞书群机器人的步骤:")
    print("  1. 在飞书群聊中点击右上角 '...'")
    print("  2. 选择 '设置'")
    print("  3. 点击 '群机器人'")
    print("  4. 点击 '添加机器人'")
    print("  5. 创建机器人后复制 Webhook URL")

    webhook_url = input("\n请输入您的飞书 Webhook URL: ").strip()
    if webhook_url:
        if webhook_url.startswith("https://open.feishu.cn/open-apis/bot/v2/hook/"):
            configure_feishu(webhook_url)

            # 询问是否测试
            test = input("\n是否测试连接？(y/n): ").strip().lower()
            if test == 'y':
                test_feishu_connection(webhook_url)
        else:
            print("❌ 无效的飞书 Webhook URL")
    else:
        print("❌ Webhook URL 不能为空")

def test_feishu_connection(webhook_url: str):
    """测试飞书连接"""
    print("\n🧪 测试飞书连接...")
    from feishu_client import FeishuClient

    client = FeishuClient(webhook_url)
    success = client.send_text("🧪 测试消息 - CC Agent 飞书集成测试成功！")

    if success:
        print("✅ 飞书连接测试成功")
    else:
        print("❌ 飞书连接测试失败")

if __name__ == "__main__":
    main()
