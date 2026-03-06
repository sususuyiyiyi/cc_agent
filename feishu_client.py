#!/usr/bin/env python3
"""
飞书客户端
用于发送消息到飞书
"""

import requests
import json
from pathlib import Path
from typing import Dict, Any, Optional

class FeishuClient:
    """飞书消息客户端"""

    def __init__(self, webhook_url: Optional[str] = None):
        self.webhook_url = webhook_url

    def send_text(self, text: str) -> bool:
        """发送文本消息"""
        if not self.webhook_url:
            print("⚠️ 飞书 Webhook URL 未配置")
            return False

        data = {
            "msg_type": "text",
            "content": {
                "text": text
            }
        }

        try:
            response = requests.post(
                self.webhook_url,
                json=data,
                headers={"Content-Type": "application/json"}
            )
            result = response.json()

            if result.get("code") == 0:
                print("✅ 消息发送成功")
                return True
            else:
                print(f"❌ 消息发送失败: {result.get('msg')}")
                return False

        except Exception as e:
            print(f"❌ 发送消息时出错: {e}")
            return False

    def send_post(self, title: str, content: list) -> bool:
        """发送富文本消息"""
        if not self.webhook_url:
            print("⚠️ 飞书 Webhook URL 未配置")
            return False

        data = {
            "msg_type": "post",
            "content": {
                "post": {
                    "zh_cn": {
                        "title": title,
                        "content": content
                    }
                }
            }
        }

        try:
            response = requests.post(
                self.webhook_url,
                json=data,
                headers={"Content-Type": "application/json"}
            )
            result = response.json()

            if result.get("code") == 0:
                print("✅ 富文本消息发送成功")
                return True
            else:
                print(f"❌ 富文本消息发送失败: {result.get('msg')}")
                return False

        except Exception as e:
            print(f"❌ 发送消息时出错: {e}")
            return False

    def send_news_briefing(self, news_items: list, date: str) -> bool:
        """发送新闻简报"""
        title = f"📰 今日新闻简报 - {date}"

        content = [
            [
                {
                    "tag": "text",
                    "text": "AI 资讯"
                }
            ]
        ]

        for item in news_items:
            content.append([
                {
                    "tag": "text",
                    "text": f"• {item['title']} ({item['source']})"
                }
            ])

        return self.send_post(title, content)

    def send_wellness_advice(self, advice: str, weather: dict, date: str) -> bool:
        """发送健康建议"""
        title = f"🥗 今日健康建议 - {date}"

        content = [
            [
                {
                    "tag": "text",
                    "text": f"天气: {weather.get('temperature')}°C, {weather.get('condition')}"
                }
            ],
            [
                {
                    "tag": "text",
                    "text": advice
                }
            ]
        ]

        return self.send_post(title, content)

    def send_daily_review(self, review: str, date: str) -> bool:
        """发送日报"""
        title = f"📝 今日日报 - {date}"

        content = [
            [
                {
                    "tag": "text",
                    "text": review
                }
            ]
        ]

        return self.send_post(title, content)

def test_webhook(webhook_url: str):
    """测试 Webhook 连接"""
    client = FeishuClient(webhook_url)
    success = client.send_text("🧪 测试消息 - CC Agent 飞书集成测试成功！")
    return success

def load_config():
    """加载飞书配置"""
    import yaml

    config_path = Path(__file__).parent / "config" / "config.yaml"
    if not config_path.exists():
        return None

    with open(config_path, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)

    if not config.get('feishu', {}).get('enabled'):
        return None

    return config['feishu'].get('webhook_url')

if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        webhook_url = load_config()
        if webhook_url:
            print(f"测试 Webhook: {webhook_url}")
            test_webhook(webhook_url)
        else:
            print("❌ 飞书未配置")
    else:
        webhook_url = load_config()
        if webhook_url:
            print(f"✅ 飞书已配置")
            print(f"   Webhook URL: {webhook_url}")
        else:
            print("⚠️ 飞书未配置")
            print("   请运行: python3 configure.py --feishu YOUR_WEBHOOK_URL")
