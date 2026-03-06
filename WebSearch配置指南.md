# WebSearch API 配置指南

## 🎯 配置 Brave Search API

Brave Search 提供免费的搜索 API，每月有 2000 次免费调用额度。

---

## 📝 步骤 1: 注册 Brave Search API

### 1. 访问注册页面
打开浏览器，访问：https://brave.com/search/api/

### 2. 创建账号
- 点击 "Get Started" 或 "Sign Up"
- 填写邮箱和密码
- 验证邮箱

### 3. 创建 API Key
- 登录后进入 Dashboard
- 点击 "Create API Key" 或类似按钮
- 选择 "Web Search API"
- 设置 API Key 名称（如：CC Agent）
- 复制生成的 API Key

**API Key 格式示例**：
```
BSAxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

---

## 🔧 步骤 2: 配置 CC Agent

### 方法一：使用配置工具（推荐）

```bash
cd /Users/sususu/cc_agent
python3 configure.py --websearch YOUR_API_KEY
```

### 方法二：直接编辑配置文件

编辑 `config/config.yaml`：

```yaml
websearch:
  enabled: true
  search_engine: default
  max_results: 10
  timeout: 30
```

---

## 🧪 步骤 3: 测试配置

### 测试 WebSearch

```bash
python3 scripts/test_websearch.py
```

### 测试新闻获取

```bash
python3 scripts/fetch_news_real.py --max 5 --save
```

### 测试完整流程

```bash
python3 run_agents.py --news
```

---

## 📊 API 配额

Brave Search 免费计划：
- **每月免费调用**: 2,000 次
- **每秒查询数**: 1 QPS
- **适用场景**: 个人项目、测试

**估算**：
- 如果每天获取 10 条新闻
- 使用 10 个搜索查询
- 每天 10 次调用
- 每月约 300 次（远低于 2000 次限额）

---

## ⚠️ 注意事项

### API 安全
- 不要将 API Key 提交到公共仓库
- 不要在客户端代码中硬编码 API Key
- 定期更换 API Key

### 使用限制
- 遵守 API 调用限制
- 实现错误重试机制
- 监控 API 使用情况

---

## 🔍 API 文档

详细文档：https://brave.com/search/api/

---

## 📞 需要帮助？

配置完成后，运行以下命令验证：

```bash
# 查看配置状态
python3 configure.py --status

# 测试搜索
python3 scripts/test_websearch.py
```

---

**准备好您的 API Key 后，告诉我，我会帮您完成配置！**
