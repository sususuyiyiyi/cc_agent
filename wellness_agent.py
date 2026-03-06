#!/usr/bin/env python3
"""
营养师su - 健康建议 Agent
"""

import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, Any

# 添加项目根目录到 Python 路径
PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))

from feishu_client import FeishuClient

class WellnessAgent:
    """健康建议 Agent"""

    def __init__(self):
        self.config = self._load_config()
        self.data_dir = PROJECT_ROOT / "data" / "wellness"

    def _load_config(self) -> Dict[str, Any]:
        """加载配置"""
        import yaml

        config_path = PROJECT_ROOT / "config" / "config.yaml"
        if config_path.exists():
            with open(config_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        return {}

    def fetch_weather(self) -> Dict[str, Any]:
        """获取天气信息"""
        # TODO: 实际实现中，这里会调用天气 API
        print("\n⏳ 正在获取天气信息...")

        # 模拟天气数据
        weather = {
            "temperature": 18,
            "humidity": 65,
            "condition": "多云",
            "wind_speed": 12,
            "uv_index": 3
        }

        print(f"🌤️ 今日天气: {weather['temperature']}°C, 湿度 {weather['humidity']}%, {weather['condition']}")
        return weather

    def generate_diet_advice(self, weather: Dict[str, Any]) -> list:
        """生成饮食建议"""
        temp = weather['temperature']
        condition = weather['condition']

        advice = []

        if temp < 10:
            advice.append("建议吃些温热的食物，如热汤、粥")
            advice.append("可以多加些姜、葱等香料驱寒")
            advice.append("多喝热水或热茶，保持身体温暖")
        elif temp < 20:
            advice.append("适合吃些均衡的饮食，营养全面")
            advice.append("可以吃些温热的食物，避免生冷")
            advice.append("注意补充水分，保持体内平衡")
        else:
            advice.append("适合吃些清淡的食物，避免油腻")
            advice.append("多吃新鲜水果和蔬菜，补充维生素")
            advice.append("避免过于辛辣的食物")

        if "雨" in condition:
            advice.append("雨天建议补充维生素C，增强免疫力")
        elif "热" in condition or temp > 30:
            advice.append("高温天气建议多喝水，避免中暑")
            advice.append("可以吃些清凉解暑的食物，如绿豆汤")

        return advice

    def generate_outfit_advice(self, weather: Dict[str, Any]) -> list:
        """生成穿搭建议"""
        temp = weather['temperature']
        condition = weather['condition']
        wind = weather.get('wind_speed', 0)

        advice = []

        if temp < 5:
            advice.append("建议穿羽绒服或厚外套")
            advice.append("注意保暖，特别是手和脚")
            advice.append("可以考虑戴帽子和手套")
        elif temp < 10:
            advice.append("建议穿厚重的外套或大衣")
            advice.append("穿保暖内衣或毛衣")
            advice.append("围巾和帽子可以帮助保暖")
        elif temp < 15:
            advice.append("建议穿轻薄的外套或夹克")
            advice.append("可以穿长袖毛衣或卫衣")
            advice.append("注意防风")
        elif temp < 20:
            advice.append("建议穿轻薄的外套或风衣")
            advice.append("可以穿长袖衣服或薄毛衣")
            advice.append("可以准备一件薄外套备用")
        elif temp < 25:
            advice.append("建议穿长袖衬衫或薄毛衣")
            advice.append("可以穿舒适的裤装")
            advice.append("根据个人体感适当增减衣物")
        else:
            advice.append("建议穿轻薄、透气的衣服")
            advice.append("可以选择短袖或薄款衣物")
            advice.append("注意防晒，涂防晒霜")

        if "雨" in condition:
            advice.insert(0, "⚠️ 记得带雨具（雨伞或雨衣）")
            advice.append("建议穿防水鞋或准备防水鞋套")
        elif wind > 15:
            advice.insert(0, "⚠️ 今天风比较大，注意防风")
            advice.append("建议穿防风外套")

        return advice

    def create_advice(self, weather: Dict[str, Any], diet_advice: list, outfit_advice: list) -> str:
        """创建建议文档"""
        today = datetime.now()
        date_str = today.strftime('%Y-%m-%d')

        advice = f"""# 今日健康建议
**日期**: {date_str}

## 天气情况
- 温度: {weather['temperature']}°C
- 湿度: {weather['humidity']}%
- 天气: {weather['condition']}
- 风速: {weather.get('wind_speed', 0)} km/h

## 饮食建议
"""

        for i, item in enumerate(diet_advice, 1):
            advice += f"{i}. {item}\n"

        advice += "\n## 穿搭建议\n"
        for i, item in enumerate(outfit_advice, 1):
            advice += f"{i}. {item}\n"

        advice += f"""
---
*生成时间: {datetime.now().strftime('%H:%M:%S')}*
"""

        return advice

    def save_advice(self, advice: str):
        """保存建议文档"""
        today = datetime.now()
        advice_dir = self.data_dir / str(today.year) / f"{today.month:02d}" / f"{today.day:02d}"
        advice_dir.mkdir(parents=True, exist_ok=True)

        advice_file = advice_dir / "建议.md"
        with open(advice_file, 'w', encoding='utf-8') as f:
            f.write(advice)

        print(f"✅ 健康建议已保存到: {advice_file}")
        return advice_file

    def send_to_feishu(self, advice: str, weather: Dict[str, Any]):
        """发送到飞书"""
        if not self.config.get('feishu', {}).get('enabled'):
            print("⚠️ 飞书未配置，跳过发送")
            return

        if not self.config.get('feishu', {}).get('message', {}).get('wellness_enabled'):
            print("⚠️ 健康建议消息发送未启用，跳过发送")
            return

        webhook_url = self.config.get('feishu', {}).get('webhook_url')
        if not webhook_url:
            print("⚠️ 飞书 Webhook URL 未配置")
            return

        print("\n📤 发送到飞书...")
        client = FeishuClient(webhook_url)

        today = datetime.now()
        date_str = today.strftime('%Y-%m-%d')

        # 发送富文本消息
        title = f"🥗 今日健康建议 - {date_str}"

        content = [
            [
                {
                    "tag": "text",
                    "text": f"🌤️ 天气: {weather['temperature']}°C, {weather['condition']}"
                }
            ],
            [
                {
                    "tag": "text",
                    "text": advice
                }
            ]
        ]

        success = client.send_post(title, content)
        if success:
            print("✅ 已发送到飞书")
        else:
            print("❌ 发送到飞书失败")

    def run(self):
        """运行完整的健康建议流程"""
        print("\n" + "=" * 60)
        print("🥗 营养师su - 开始工作")
        print("=" * 60)

        # 1. 获取天气
        weather = self.fetch_weather()

        # 2. 生成建议
        diet_advice = self.generate_diet_advice(weather)
        outfit_advice = self.generate_outfit_advice(weather)

        print("\n🍽️ 饮食建议:")
        for i, advice in enumerate(diet_advice, 1):
            print(f"  {i}. {advice}")

        print("\n👕 穿搭建议:")
        for i, advice in enumerate(outfit_advice, 1):
            print(f"  {i}. {advice}")

        # 3. 创建建议文档
        advice_doc = self.create_advice(weather, diet_advice, outfit_advice)

        # 4. 保存建议
        self.save_advice(advice_doc)

        # 5. 发送到飞书
        self.send_to_feishu(advice_doc, weather)

        print("\n" + "=" * 60)
        print("✅ 营养师su - 工作完成")
        print("=" * 60)

if __name__ == "__main__":
    agent = WellnessAgent()
    agent.run()
