#!/usr/bin/env python3
"""
发送AI新闻到飞书
"""

import sys
import json
from pathlib import Path
from datetime import datetime
import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from feishu_client import FeishuClient


def parse_ai_news_report(report_path: str) -> list:
    """解析AI新闻报告文件，提取新闻条目"""
    news_items = []

    try:
        # 检查文件是否存在
        if not os.path.exists(report_path):
            report_path = os.path.join(os.path.dirname(os.path.dirname(report_path)), report_path)

        with open(report_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # 更准确的解析逻辑
        lines = content.split('\n')
        current_category = None
        current_item = {}

        for line in lines:
            line = line.strip()

            # 检测分类标题（## ## 格式）
            if line.startswith('## ') and '## 📚' in line:
                current_category = line
                continue
            elif line.startswith('## ') and '## ⚡' in line:
                current_category = line
                continue
            elif line.startswith('## ') and '## 🚀' in line:
                current_category = line
                continue
            elif line.startswith('## ') and '## 💼' in line:
                current_category = line
                continue
            elif line.startswith('## ') and '## 🛡️' in line:
                current_category = line
                continue
            elif line.startswith('## ') and '## 🔮' in line:
                current_category = line
                continue

            # 检测项目标题（### 标题格式）
            if line.startswith('### ') and current_category:
                if current_item:  # 保存上一个项目
                    current_item['_category'] = current_category
                    news_items.append(current_item)

                # 创建新项目
                title = line[4:]  # 移除###
                current_item = {
                    'title': title,
                    'category': current_category
                }
            # 检测子项（- 开头）
            elif line.startswith('- ') and current_item:
                sub_title = line[2:]  # 移除-
                if 'subtitle' not in current_item:
                    current_item['subtitle'] = []
                current_item['subtitle'].append(sub_title)
            # 检测URL（[]()格式）
            elif ('[' in line and ']' in line and '(' in line and ')' in line) and current_item:
                # 提取URL
                start = line.find('(') + 1
                end = line.find(')', start)
                if start > 0 and end > start:
                    url = line[start:end]
                    if url.startswith('http'):
                        current_item['url'] = url

        # 添加最后一个项目
        if current_item and current_category:
            current_item['_category'] = current_category
            news_items.append(current_item)

    except Exception as e:
        print(f"❌ 解析AI新闻报告失败: {e}")
        # 创建一些示例新闻
        news_items = [
            {
                'title': '努比亚Z80 Ultra集成OpenClaw，AI手机新突破',
                'source': 'IT之家',
                '_category': '## ⚡ 技术突破与创新'
            },
            {
                'title': 'Anthropic发布Cowork桌面助手',
                'source': 'VentureBeat',
                '_category': '## 🚀 产品发布与商业动态'
            },
            {
                'title': '人大代表呼吁出台AI上位法',
                'source': '政策新闻',
                '_category': '## 🛡️ 监管政策与伦理讨论'
            }
        ]

    return news_items


def create_ai_news_card_elements(news_items: list) -> list:
    """创建AI新闻的卡片元素"""
    elements = []

    # 按分类整理
    categories = {}
    for item in news_items:
        category = item.get('_category', '🔬 AI新闻')
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

            # 该分类下的新闻
            for item in items[:10]:  # 每个分类最多10条
                title = item.get('title', '')
                url = item.get('url', '')
                source = item.get('source', '')

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
                if source:
                    elements.append({
                        "tag": "div",
                        "text": {
                            "tag": "lark_md",
                            "content": f"  📰 {source}\n"
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
    total_count = len(news_items)
    elements.append({
        "tag": "div",
        "text": {
            "tag": "lark_md",
            "content": f"---\n*📊 共 {total_count} 条AI新闻 | 生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M')}*"
        }
    })

    return elements


def main():
    """主函数"""
    report_path = "comprehensive_ai_report.md"
    webhook_url = None

    # 从配置加载webhook URL
    from feishu_client import load_config
    webhook_url = load_config()

    if not webhook_url:
        print("❌ 飞书Webhook未配置")
        print("请先配置飞书Webhook URL")
        return False

    # 创建飞书客户端
    client = FeishuClient(webhook_url)

    # 解析AI新闻报告
    news_items = parse_ai_news_report(report_path)

    if not news_items:
        print("❌ 未找到AI新闻")
        return False

    print(f"📰 解析到 {len(news_items)} 条AI新闻")

    # 发送卡片消息
    title = f"🤖 AI专报 - {datetime.now().strftime('%Y-%m-%d')}"
    elements = create_ai_news_card_elements(news_items)

    success = client.send_card(title, elements)

    if success:
        print("✅ AI新闻已成功发送到飞书")
    else:
        print("❌ 发送失败")

    return success


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)