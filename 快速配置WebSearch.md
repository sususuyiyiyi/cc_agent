# 🚀 WebSearch API 快速配置指南

## 📝 3 步快速配置

### 步骤 1: 获取 API Key

访问：https://brave.com/search/api/

1. 注册账号
2. 登录 Dashboard
3. 创建 API Key
4. 复制 API Key

**免费额度**: 每月 2,000 次调用

---

### 步骤 2: 配置 CC Agent

运行快速配置脚本：

```bash
cd /Users/sususu/cc_agent
python3 scripts/setup_websearch.py
```

输入您的 API Key 即可自动配置。

---

### 步骤 3: 测试

```bash
# 测试配置
python3 scripts/test_websearch.py

# 测试新闻获取
python3 scripts/fetch_news_with_websearch.py --max 3 --save
```

---

## ✅ 配置完成后

系统将能够：

- ✅ 搜索真实的 AI 新闻
- ✅ 从多个来源获取内容
- ✅ 生成高质量新闻简报
- ✅ 自动发送到飞书

---

## 📞 需要帮助？

查看详细文档：

```bash
cat WebSearch配置完成.md
```

---

**现在就可以配置了！准备好您的 API Key 后，运行：**

```bash
python3 scripts/setup_websearch.py
```
