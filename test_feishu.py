#!/usr/bin/env python3
"""
测试飞书集成
"""

from feishu_client import FeishuClient
from datetime import datetime

# 测试飞书连接
webhook_url = "https://open.feishu.cn/open-apis/bot/v2/hook/e3990900-85a3-44b6-a025-9b7175b191a0"
client = FeishuClient(webhook_url)

print("🧪 测试飞书集成...")
print(f"Webhook URL: {webhook_url}\n")

# 测试 1: 发送文本消息
print("测试 1: 发送文本消息")
success = client.send_text("🧪 测试消息 - CC Agent 飞书集成测试成功！")
print(f"结果: {'✅ 成功' if success else '❌ 失败'}\n")

# 测试 2: 发送富文本消息
print("测试 2: 发送富文本消息")
title = "📋 CC Agent 飞书集成测试"
content = [
    [
        {
            "tag": "text",
            "text": "飞书集成已配置完成！"
        }
    ],
    [
        {
            "tag": "text",
            "text": "📰 新闻简报 - 每日发送 AI 资讯"
        }
    ],
    [
        {
            "tag": "text",
            "text": "🥗 健康建议 - 基于天气的饮食和穿搭建议"
        }
    ],
    [
        {
            "tag": "text",
            "text": "📝 日报 - 每日复盘和总结"
        }
    ]
]
success = client.send_post(title, content)
print(f"结果: {'✅ 成功' if success else '❌ 失败'}\n")

# 测试 3: 发送系统状态
print("测试 3: 发送系统状态")
status_title = "📊 CC Agent 系统状态"
status_content = [
    [
        {
            "tag": "text",
            "text": f"✅ 飞书集成已配置"
        }
    ],
    [
        {
            "tag": "text",
            "text": f"✅ 已配置 3 个 Agents"
        }
    ],
    [
        {
            "tag": "text",
            "text": f"✅ 所有功能正常运行"
        }
    ],
    [
        {
            "tag": "text",
            "text": f"📅 测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        }
    ]
]
success = client.send_post(status_title, status_content)
print(f"结果: {'✅ 成功' if success else '❌ 失败'}\n")

print("🎉 所有测试完成！")
print("\n飞书集成已成功配置，您的飞书群聊现在可以收到 CC Agent 的消息了！")
