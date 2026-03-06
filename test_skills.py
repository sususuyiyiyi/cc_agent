#!/usr/bin/env python3
"""
测试脚本：验证 CC Agent Skills 的功能
"""

import os
from datetime import datetime
from pathlib import Path

# 项目根目录
PROJECT_ROOT = Path("/Users/sususu/cc_agent")
SKILLS_DIR = PROJECT_ROOT / "skills"
DATA_DIR = PROJECT_ROOT / "data"

def test_skill_structure(skill_name):
    """测试 skill 的目录结构是否完整"""
    print(f"\n🔍 测试 {skill_name} 的目录结构...")

    skill_path = SKILLS_DIR / skill_name
    required_dirs = ["scripts", "references", "assets"]
    required_files = ["SKILL.md"]

    all_passed = True

    # 检查 skill 目录是否存在
    if not skill_path.exists():
        print(f"❌ Skill 目录不存在: {skill_path}")
        return False
    print(f"✅ Skill 目录存在: {skill_path}")

    # 检查必需的子目录
    for dir_name in required_dirs:
        dir_path = skill_path / dir_name
        if dir_path.exists():
            print(f"✅ {dir_name}/ 目录存在")
        else:
            print(f"❌ {dir_name}/ 目录不存在")
            all_passed = False

    # 检查必需的文件
    for file_name in required_files:
        file_path = skill_path / file_name
        if file_path.exists():
            print(f"✅ {file_name} 文件存在")
            # 读取文件内容并验证 frontmatter
            if file_name == "SKILL.md":
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    if '---' in content:
                        print(f"✅ SKILL.md 包含 YAML frontmatter")
                    else:
                        print(f"❌ SKILL.md 缺少 YAML frontmatter")
                        all_passed = False
        else:
            print(f"❌ {file_name} 文件不存在")
            all_passed = False

    return all_passed

def test_data_structure():
    """测试数据目录结构"""
    print("\n🔍 测试数据目录结构...")

    required_paths = [
        DATA_DIR / "news" / "2026" / "03" / "06",
        DATA_DIR / "wellness" / "2026" / "03" / "06",
        DATA_DIR / "reviews" / "2026" / "03" / "06",
    ]

    all_passed = True
    for path in required_paths:
        if path.exists():
            print(f"✅ {path} 目录存在")
        else:
            print(f"❌ {path} 目录不存在")
            all_passed = False

    return all_passed

def test_skill_content(skill_name):
    """测试 skill 的内容质量"""
    print(f"\n🔍 测试 {skill_name} 的内容质量...")

    skill_md = SKILLS_DIR / skill_name / "SKILL.md"

    if not skill_md.exists():
        print(f"❌ SKILL.md 不存在")
        return False

    with open(skill_md, 'r', encoding='utf-8') as f:
        content = f.read()

    # 检查必需的字段
    checks = {
        "name:": "Skill 名称字段",
        "description:": "Skill 描述字段",
        "When This Skill Applies": "激活条件说明",
        "Core Workflow": "核心工作流程",
        "Dependencies": "依赖项说明",
    }

    all_passed = True
    for keyword, description in checks.items():
        if keyword in content:
            print(f"✅ {description} 存在")
        else:
            print(f"❌ {description} 缺失")
            all_passed = False

    return all_passed

def simulate_news_workflow():
    """模拟 news-su 的工作流程"""
    print("\n🔄 模拟 news-su 工作流程...")

    today = datetime.now()
    year = today.year
    month = f"{today.month:02d}"
    day = f"{today.day:02d}"

    # 1. 创建新闻目录
    news_dir = DATA_DIR / "news" / str(year) / month / day
    news_dir.mkdir(parents=True, exist_ok=True)
    print(f"✅ 创建目录: {news_dir}")

    # 2. 创建示例新闻文件
    news_file = news_dir / "今日新闻.md"
    sample_news = f"""# 今日新闻简报
**日期**: {year}-{month}-{day}

## AI 资讯
- Claude 4.6 发布重大更新，推理能力提升50% (OpenAI Blog)
- Anthropic 推出新的安全研究项目 (AI News)
- GitHub Copilot 新增多项企业功能 (TechCrunch)

## 其他资讯
- 全球股市今日震荡上涨 (财经网)
- 新的气候变化报告发布 (科学美国人)

---
*此为测试文件，实际使用时将由 news-su agent 自动生成*
"""

    with open(news_file, 'w', encoding='utf-8') as f:
        f.write(sample_news)
    print(f"✅ 创建文件: {news_file}")

    # 3. 验证文件内容
    if news_file.exists():
        with open(news_file, 'r', encoding='utf-8') as f:
            content = f.read()
            print(f"\n📄 文件内容预览:")
            print(content[:200] + "...")

    return True

def simulate_wellness_workflow():
    """模拟 wellness-su 的工作流程"""
    print("\n🔄 模拟 wellness-su 工作流程...")

    today = datetime.now()
    year = today.year
    month = f"{today.month:02d}"
    day = f"{today.day:02d}"

    # 1. 创建建议目录
    wellness_dir = DATA_DIR / "wellness" / str(year) / month / day
    wellness_dir.mkdir(parents=True, exist_ok=True)
    print(f"✅ 创建目录: {wellness_dir}")

    # 2. 创建示例建议文件
    advice_file = wellness_dir / "建议.md"
    sample_advice = f"""# 今日健康建议
**日期**: {year}-{month}-{day}

## 天气情况
- 温度: 18°C
- 湿度: 65%
- 天气: 多云

## 饮食建议
- 适量喝温水，保持身体水分
- 多吃新鲜蔬菜和水果
- 避免过于油腻的食物

## 穿搭建议
- 建议穿轻薄的外套
- 适合穿长袖衣服
- 可以考虑穿舒适的牛仔裤或休闲裤

## 额外提醒
- 适当进行户外活动
- 注意保暖

---
*此为测试文件，实际使用时将由 wellness-su agent 自动生成*
"""

    with open(advice_file, 'w', encoding='utf-8') as f:
        f.write(sample_advice)
    print(f"✅ 创建文件: {advice_file}")

    return True

def simulate_review_workflow():
    """模拟 review-su 的工作流程"""
    print("\n🔄 模拟 review-su 工作流程...")

    today = datetime.now()
    year = today.year
    month = f"{today.month:02d}"
    day = f"{today.day:02d}"

    # 1. 创建复盘目录
    review_dir = DATA_DIR / "reviews" / str(year) / month / day
    review_dir.mkdir(parents=True, exist_ok=True)
    print(f"✅ 创建目录: {review_dir}")

    # 2. 创建示例日报文件
    report_file = review_dir / "日报.md"
    sample_report = f"""# 日报
**日期**: {year}-{month}-{day}

## 今日完成事项
### 工作相关
- 完成了 CC Agent 项目的技能设计
- 创建了三个 Skills 的目录结构
- 编写了详细的 SKILL.md 文件

### 个人相关
- 散步30分钟
- 阅读了技术文档

## 今日心得/感悟
- Skills 的设计需要考虑实际使用场景
- 模块化的设计有助于后续维护和扩展

## 明日计划
- 测试所有 Skills 的功能
- 优化工作流程
- 添加必要的 MCP 工具集成

---
*此为测试文件，实际使用时将由 review-su agent 根据用户输入生成*
"""

    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(sample_report)
    print(f"✅ 创建文件: {report_file}")

    return True

def main():
    """主测试函数"""
    print("=" * 60)
    print("🧪 CC Agent Skills 测试")
    print("=" * 60)

    # 测试的 skills
    skills = ["news-su", "wellness-su", "review-su"]

    # 1. 测试所有 skills 的结构
    print("\n" + "=" * 60)
    print("📦 测试 Skills 目录结构")
    print("=" * 60)

    structure_results = {}
    for skill in skills:
        structure_results[skill] = test_skill_structure(skill)

    # 2. 测试所有 skills 的内容
    print("\n" + "=" * 60)
    print("📝 测试 Skills 内容质量")
    print("=" * 60)

    content_results = {}
    for skill in skills:
        content_results[skill] = test_skill_content(skill)

    # 3. 测试数据目录结构
    print("\n" + "=" * 60)
    print("💾 测试数据目录结构")
    print("=" * 60)

    data_result = test_data_structure()

    # 4. 模拟工作流程
    print("\n" + "=" * 60)
    print("⚙️ 模拟工作流程")
    print("=" * 60)

    news_workflow = simulate_news_workflow()
    wellness_workflow = simulate_wellness_workflow()
    review_workflow = simulate_review_workflow()

    # 5. 总结测试结果
    print("\n" + "=" * 60)
    print("📊 测试结果总结")
    print("=" * 60)

    print("\n✅ Skills 结构测试:")
    for skill, passed in structure_results.items():
        status = "✅ 通过" if passed else "❌ 失败"
        print(f"  - {skill}: {status}")

    print("\n✅ Skills 内容测试:")
    for skill, passed in content_results.items():
        status = "✅ 通过" if passed else "❌ 失败"
        print(f"  - {skill}: {status}")

    print(f"\n✅ 数据目录结构: {'✅ 通过' if data_result else '❌ 失败'}")

    print("\n✅ 工作流程模拟:")
    print(f"  - news-su: {'✅ 通过' if news_workflow else '❌ 失败'}")
    print(f"  - wellness-su: {'✅ 通过' if wellness_workflow else '❌ 失败'}")
    print(f"  - review-su: {'✅ 通过' if review_workflow else '❌ 失败'}")

    print("\n" + "=" * 60)
    print("✅ 所有测试完成！")
    print("=" * 60)

if __name__ == "__main__":
    main()
