#!/bin/bash

# 自动推送脚本
# 用途: 自动检测更改并推送到 GitHub

echo "============================================================"
echo "🔄 Git 自动推送脚本"
echo "============================================================"

# 检查是否有更改
if [ -z "$(git status --porcelain)" ]; then
    echo "✅ 没有需要提交的更改"
    echo "============================================================"
    exit 0
fi

echo ""
echo "📋 检测到以下更改:"
git status --short

echo ""
echo "📝 提交信息 (留空使用默认):"
read -r commit_message

# 如果用户没有输入，使用默认提交信息
if [ -z "$commit_message" ]; then
    commit_message="chore: 自动更新 - $(date '+%Y-%m-%d %H:%M:%S')"
fi

echo ""
echo "🔄 添加更改..."
git add .

echo ""
echo "📝 提交更改: $commit_message"
git commit -m "$commit_message"

echo ""
echo "📤 推送到 GitHub..."
if git push; then
    echo "✅ 推送成功！"
else
    echo "❌ 推送失败，请检查网络连接或凭据"
    exit 1
fi

echo ""
echo "============================================================"
echo "✅ 自动推送完成"
echo "============================================================"
