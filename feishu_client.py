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

    def send_card(self, title: str, elements: list) -> bool:
        """发送卡片消息（支持超链接）"""
        if not self.webhook_url:
            print("⚠️ 飞书 Webhook URL 未配置")
            return False

        data = {
            "msg_type": "interactive",
            "card": {
                "header": {
                    "title": {
                        "tag": "plain_text",
                        "content": title
                    }
                },
                "elements": elements
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
                print("✅ 卡片消息发送成功")
                return True
            else:
                print(f"❌ 卡片消息发送失败: {result.get('msg')}")
                return False

        except Exception as e:
            print(f"❌ 发送消息时出错: {e}")
            return False

    def send_news_briefing(self, news_items: list, date: str) -> bool:
        """发送新闻简报（简洁格式，支持超链接）"""
        title = f"📰 今日新闻简报 - {date}"

        # 创建卡片元素列表
        elements = []

        # 添加分类标题
        categories = {}
        for item in news_items:
            category = item.get('_category', '🔬 科学研究')
            if category not in categories:
                categories[category] = []
            categories[category].append(item)

        # 为每个分类添加卡片元素
        for category, items in categories.items():
            if items:  # 只添加有内容的分类
                # 分类标题
                elements.append({
                    "tag": "div",
                    "text": {
                        "tag": "lark_md",
                        "content": f"**{category}**\n"
                    }
                })

                # 该分类下的新闻（简洁格式）
                for item in items[:5]:  # 每个分类最多5条
                    title = item.get('title', '')
                    url = item.get('url', '')
                    source = item.get('source', '')
                    source_type = item.get('source_type', '')
                    subreddit = item.get('subreddit', '')

                    # 新闻标题
                    if url and url.startswith('http'):
                        title_element = f"• [{title}]({url})"
                    else:
                        title_element = f"• {title}"

                    elements.append({
                        "tag": "div",
                        "text": {
                            "tag": "lark_md",
                            "content": f"{title_element}\n"
                        }
                    })

                    # 添加信息源
                    source_text = ""
                    if source_type == 'reddit':
                        source_text = f"  📍 r/{subreddit}"
                    else:
                        if source and 'news.google.com' not in source:
                            source_text = f"  📍 {source}"

                    if source_text:
                        elements.append({
                            "tag": "div",
                            "text": {
                                "tag": "lark_md",
                                "content": f"{source_text}\n"
                            }
                        })

                # 分类间添加空行
                elements.append({
                    "tag": "div",
                    "text": {
                        "tag": "lark_md",
                        "content": ""
                    }
                })

        # 统计信息
        elements.append({
            "tag": "div",
            "text": {
                "tag": "lark_md",
                "content": f"---\n*共 {len(news_items)} 条新闻*"
            }
        })

        return self.send_card(title, elements)

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
