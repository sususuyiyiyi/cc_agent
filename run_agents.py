#!/usr/bin/env python3
"""
CC Agent 主程序
提供命令行界面来手动触发和测试各个 agents
"""

import sys
import argparse
from pathlib import Path
from datetime import datetime

# 添加项目根目录到 Python 路径
PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))

def show_menu():
    """显示主菜单"""
    print("\n" + "=" * 60)
    print("🤖 CC Agent - 个人生活助理团队")
    print("=" * 60)
    print("\n可用功能:")
    print("  1. 资讯su - 获取今日新闻简报")
    print("  2. 营养师su - 获取健康建议")
    print("  3. 复盘su - 创建今日日报")
    print("  4. 运行所有 agents")
    print("  5. 测试 Skills")
    print("  6. 查看状态")
    print("  7. 退出")
    print("=" * 60)

def show_status():
    """显示系统状态"""
    print("\n" + "=" * 60)
    print("📊 系统状态")
    print("=" * 60)

    # 检查 skills
    skills_dir = PROJECT_ROOT / "skills"
    if skills_dir.exists():
        skills = [d.name for d in skills_dir.iterdir() if d.is_dir()]
        print(f"\n📦 已安装的 Skills ({len(skills)} 个):")
        for skill in sorted(skills):
            skill_md = skills_dir / skill / "SKILL.md"
            status = "✅" if skill_md.exists() else "❌"
            print(f"  {status} {skill}")
    else:
        print("\n❌ Skills 目录不存在")

    # 检查数据目录
    data_dir = PROJECT_ROOT / "data"
    if data_dir.exists():
        print(f"\n💾 数据目录:")
        for subdir in ["news", "wellness", "reviews"]:
            path = data_dir / subdir
            if path.exists():
                count = sum(1 for _ in path.rglob("*.md"))
                print(f"  ✅ {subdir}/ ({count} 个文件)")
            else:
                print(f"  ❌ {subdir}/ (不存在)")

    # 今日数据
    today = datetime.now()
    today_dir = data_dir / "news" / str(today.year) / f"{today.month:02d}" / f"{today.day:02d}"
    if today_dir.exists():
        print(f"\n📅 今日数据 ({today.strftime('%Y-%m-%d')}):")
        for subdir in ["news", "wellness", "reviews"]:
            path = data_dir / subdir / str(today.year) / f"{today.month:02d}" / f"{today.day:02d}"
            if path.exists():
                files = list(path.glob("*.md"))
                for file in files:
                    print(f"  📄 {subdir}/{file.name}")
    else:
        print(f"\n📅 今日数据: 尚未生成")

    print("\n" + "=" * 60)

def run_news_agent():
    """运行资讯su"""
    print("\n📰 启动资讯su...")

    print("\n早上好！让我为您获取今天的新闻...")

    # TODO: 实际实现中，这里会调用 WebSearch 和 WebFetch
    print("\n⏳ 正在搜索最新 AI 资讯...")

    # 模拟数据（实际使用时替换为真实的新闻获取逻辑）
    news_items = [
        ("Claude 4.6 发布重大更新，推理能力提升50%", "OpenAI Blog"),
        ("Anthropic 推出新的安全研究项目", "AI News"),
        ("GitHub Copilot 新增多项企业功能", "TechCrunch"),
    ]

    print("\n📋 今日新闻简报:")
    print(f"**日期**: {datetime.now().strftime('%Y-%m-%d')}")
    print("\n## AI 资讯")
    for title, source in news_items:
        print(f"- {title} ({source})")

    # 保存到文件
    today = datetime.now()
    news_dir = PROJECT_ROOT / "data" / "news" / str(today.year) / f"{today.month:02d}" / f"{today.day:02d}"
    news_dir.mkdir(parents=True, exist_ok=True)

    news_file = news_dir / "今日新闻.md"
    with open(news_file, 'w', encoding='utf-8') as f:
        f.write(f"""# 今日新闻简报
**日期**: {today.strftime('%Y-%m-%d')}

## AI 资讯
""")
        for title, source in news_items:
            f.write(f"- {title} ({source})\n")

        f.write("\n\n---\n")
        f.write(f"*生成时间: {datetime.now().strftime('%H:%M:%S')}*\n")

    print(f"\n✅ 新闻简报已保存到: {news_file}")

    # TODO: 发送到飞书（如果配置了）
    print("\n💡 提示: 配置飞书后可以自动发送到您的群聊")

def run_wellness_agent():
    """运行营养师su"""
    print("\n🥗 启动营养师su...")

    # TODO: 实际实现中，这里会调用天气 API
    print("\n⏳ 正在获取天气信息...")

    # 模拟天气数据（实际使用时替换为真实的天气获取逻辑）
    weather = {
        "temperature": 18,
        "humidity": 65,
        "condition": "多云"
    }

    print(f"\n🌤️ 今日天气: {weather['temperature']}°C, 湿度 {weather['humidity']}%, {weather['condition']}")

    # 生成建议
    if weather['temperature'] < 10:
        diet_advice = [
            "建议吃些温热的食物，如热汤、粥",
            "可以多加些姜、葱等香料",
            "多喝热水或热茶"
        ]
        outfit_advice = [
            "建议穿羽绒服或厚外套",
            "注意保暖，特别是手和脚",
            "可以考虑戴帽子和手套"
        ]
    elif weather['temperature'] < 20:
        diet_advice = [
            "适合吃些均衡的饮食",
            "可以吃些温热的食物",
            "注意补充水分"
        ]
        outfit_advice = [
            "建议穿轻薄的外套",
            "可以穿毛衣或卫衣",
            "注意防风"
        ]
    else:
        diet_advice = [
            "适合吃些清淡的食物",
            "多吃新鲜水果和蔬菜",
            "避免过于油腻"
        ]
        outfit_advice = [
            "建议穿轻薄的衣服",
            "注意防晒",
            "可以选择透气的面料"
        ]

    print("\n🍽️ 饮食建议:")
    for advice in diet_advice:
        print(f"  • {advice}")

    print("\n👕 穿搭建议:")
    for advice in outfit_advice:
        print(f"  • {advice}")

    # 保存到文件
    today = datetime.now()
    wellness_dir = PROJECT_ROOT / "data" / "wellness" / str(today.year) / f"{today.month:02d}" / f"{today.day:02d}"
    wellness_dir.mkdir(parents=True, exist_ok=True)

    advice_file = wellness_dir / "建议.md"
    with open(advice_file, 'w', encoding='utf-8') as f:
        f.write(f"""# 今日健康建议
**日期**: {today.strftime('%Y-%m-%d')}

## 天气情况
- 温度: {weather['temperature']}°C
- 湿度: {weather['humidity']}%
- 天气: {weather['condition']}

## 饮食建议
""")
        for advice in diet_advice:
            f.write(f"- {advice}\n")

        f.write("\n## 穿搭建议\n")
        for advice in outfit_advice:
            f.write(f"- {advice}\n")

        f.write("\n\n---\n")
        f.write(f"*生成时间: {datetime.now().strftime('%H:%M:%S')}*\n")

    print(f"\n✅ 健康建议已保存到: {advice_file}")

def run_review_agent():
    """运行复盘su"""
    print("\n📝 启动复盘su...")

    print("\n🌙 晚上好！让我们来回顾今天...")
    print("\n今天都做了什么呢？")
    print("(请输入您今天做的事情，完成后输入 '完成' 继续)")

    # 收集用户输入
    activities = []
    while True:
        try:
            user_input = input("\n> ").strip()
            if user_input.lower() in ['完成', 'done', 'exit']:
                break
            if user_input:
                activities.append(user_input)
        except KeyboardInterrupt:
            print("\n\n已取消输入")
            return

    if not activities:
        print("\n⚠️ 您没有输入任何活动，将创建一个空白的日报")
        activities = ["暂无活动记录"]

    # 生成日报
    print("\n📊 正在生成日报...")

    today = datetime.now()
    review_dir = PROJECT_ROOT / "data" / "reviews" / str(today.year) / f"{today.month:02d}" / f"{today.day:02d}"
    review_dir.mkdir(parents=True, exist_ok=True)

    report_file = review_dir / "日报.md"

    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(f"""# 日报
**日期**: {today.strftime('%Y-%m-%d')}

## 今日完成事项
""")

        for i, activity in enumerate(activities, 1):
            f.write(f"{i}. {activity}\n")

        f.write(f"""

## 心得/感悟
(在此处添加您的心得和感悟)

## 明日计划
(在此处添加明天的计划)

---
*生成时间: {datetime.now().strftime('%H:%M:%S')}*
""")

    print(f"\n✅ 日报已生成并保存到: {report_file}")
    print("\n💡 提示: 您可以编辑该文件添加更多详细信息")

def run_all_agents():
    """运行所有 agents"""
    print("\n🚀 运行所有 agents...")

    print("\n" + "=" * 60)
    run_news_agent()

    print("\n" + "=" * 60)
    run_wellness_agent()

    print("\n" + "=" * 60)
    run_review_agent()

    print("\n" + "=" * 60)
    print("✅ 所有 agents 运行完成！")

def run_tests():
    """运行测试"""
    print("\n🧪 运行测试...")

    import subprocess
    test_script = PROJECT_ROOT / "test_skills.py"

    if test_script.exists():
        try:
            result = subprocess.run(
                [sys.executable, str(test_script)],
                cwd=str(PROJECT_ROOT),
                capture_output=True,
                text=True
            )
            print(result.stdout)
            if result.stderr:
                print("错误:", result.stderr)
        except Exception as e:
            print(f"❌ 测试执行失败: {e}")
    else:
        print(f"❌ 测试脚本不存在: {test_script}")

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='CC Agent - 个人生活助理团队')
    parser.add_argument('--news', action='store_true', help='运行资讯su')
    parser.add_argument('--wellness', action='store_true', help='运行营养师su')
    parser.add_argument('--review', action='store_true', help='运行复盘su')
    parser.add_argument('--all', action='store_true', help='运行所有agents')
    parser.add_argument('--test', action='store_true', help='运行测试')
    parser.add_argument('--status', action='store_true', help='查看状态')

    args = parser.parse_args()

    # 命令行模式
    if args.news:
        run_news_agent()
        return
    elif args.wellness:
        run_wellness_agent()
        return
    elif args.review:
        run_review_agent()
        return
    elif args.all:
        run_all_agents()
        return
    elif args.test:
        run_tests()
        return
    elif args.status:
        show_status()
        return

    # 交互式模式
    while True:
        show_menu()

        try:
            choice = input("\n请选择功能 (1-7): ").strip()

            if choice == '1':
                run_news_agent()
            elif choice == '2':
                run_wellness_agent()
            elif choice == '3':
                run_review_agent()
            elif choice == '4':
                run_all_agents()
            elif choice == '5':
                run_tests()
            elif choice == '6':
                show_status()
            elif choice == '7':
                print("\n👋 再见！")
                break
            else:
                print("\n❌ 无效的选择，请重新输入")

            input("\n按 Enter 继续...")

        except KeyboardInterrupt:
            print("\n\n👋 再见！")
            break
        except Exception as e:
            print(f"\n❌ 发生错误: {e}")
            input("\n按 Enter 继续...")

if __name__ == "__main__":
    main()
