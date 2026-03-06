#!/bin/bash

# CC Agent 安装脚本

echo "============================================================"
echo "🚀 CC Agent 安装程序"
echo "============================================================"

# 检查 Python 版本
echo ""
echo "📋 检查 Python 版本..."
python3 --version
if [ $? -ne 0 ]; then
    echo "❌ Python 3 未安装，请先安装 Python 3"
    exit 1
fi

# 创建虚拟环境（可选）
read -p "是否创建虚拟环境？(推荐) (y/n): " create_venv
if [ "$create_venv" = "y" ] || [ "$create_venv" = "Y" ]; then
    echo ""
    echo "🔧 创建虚拟环境..."
    python3 -m venv venv

    echo "🔧 激活虚拟环境..."
    source venv/bin/activate

    echo "✅ 虚拟环境已创建并激活"
else
    echo "⚠️ 跳过虚拟环境创建"
fi

# 安装依赖
echo ""
echo "📦 安装 Python 依赖..."

# 基础依赖
pip3 install -q pyyaml requests
echo "✅ 基础依赖已安装"

# 调度器依赖
pip3 install -q apscheduler
echo "✅ APScheduler 已安装"

# MCP 相关依赖
pip3 install -q httpx mcp
echo "✅ MCP 相关依赖已安装"

# 创建日志目录
echo ""
echo "📁 创建必要的目录..."
mkdir -p logs
mkdir -p backups
echo "✅ 目录创建完成"

# 设置执行权限
echo ""
echo "🔧 设置执行权限..."
chmod +x run_agents.py
chmod +x configure.py
chmod +x mcp_tools.py
chmod +x scheduler.py
chmod +x news_agent.py
chmod +x wellness_agent.py
chmod +x review_agent.py
chmod +x feishu_client.py
echo "✅ 执行权限设置完成"

# 运行测试
echo ""
echo "🧪 运行测试..."
python3 test_skills.py

if [ $? -eq 0 ]; then
    echo ""
    echo "============================================================"
    echo "✅ 安装完成！"
    echo "============================================================"
    echo ""
    echo "下一步:"
    echo "  1. 运行配置工具: python3 configure.py"
    echo "  2. 查看使用指南: cat 使用指南.md"
    echo "  3. 运行 agents: python3 run_agents.py"
    echo ""

    # 询问是否立即配置
    read -p "是否立即开始配置？(y/n): " start_config
    if [ "$start_config" = "y" ] || [ "$start_config" = "Y" ]; then
        python3 configure.py
    fi
else
    echo ""
    echo "⚠️ 测试失败，请检查错误信息"
    exit 1
fi
