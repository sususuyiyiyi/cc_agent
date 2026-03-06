# WebSearch API 配置完成

## 📝 配置步骤

### 1. 获取 Brave Search API Key

**注册地址**: https://brave.com/search/api/

**步骤**:
1. 访问注册页面
2. 点击 "Get Started" 或 "Sign Up"
3. 使用邮箱注册账号
4. 登录后进入 Dashboard
5. 点击 "Create API Key"
6. 选择 "Web Search API"
7. 设置 API Key 名称（如：CC Agent）
8. 复制生成的 API Key

**API Key 格式**:
```
BSAxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

**免费额度**:
- 每月 2,000 次免费调用
- 每秒 1 次查询 (1 QPS)
- 适用于个人项目

---

## 🔧 配置 CC Agent

### 方法一：使用配置脚本

```bash
cd /Users/sususu/cc_agent

# 配置 API Key
python3 scripts/config_websearch.py --config YOUR_API_KEY

# 测试配置
python3 scripts/config_websearch.py --test
```

### 方法二：手动配置

编辑 `config/config.yaml`:

```yaml
websearch:
  enabled: true
  search_engine: brave
  max_results: 10
  timeout: 30
```

编辑 `config/mcp_config.json`:

```json
{
  "mcpServers": {
    "websearch": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-brave-search"],
      "env": {
        "BRAVE_API_KEY": "YOUR_API_KEY_HERE"
      }
    }
  }
}
```

---

## 🧪 测试配置

### 测试 1: 测试配置状态

```bash
python3 scripts/config_websearch.py --test
```

应该看到：
```
============================================================
🔍 WebSearch 配置状态
============================================================

主配置:
  启用状态: true
  搜索引擎: brave
  最大结果: 10

MCP 配置:
  命令: npx
  参数: -y @modelcontextprotocol/server-brave-search
  API Key: BSAxxxxxxxx...xxxx

============================================================
```

### 测试 2: 测试搜索功能

```bash
python3 scripts/fetch_news_with_websearch.py --max 3 --save
```

应该看到：
```
============================================================
📰 开始获取今日新闻（真实搜索）
============================================================

🔍 搜索 10 个查询，每个查询最多 3 条结果
   搜索: AI新闻 2026-03-06
   搜索: 人工智能 最新消息
   ...

📋 搜索到 X 条结果

✅ 最终获取 3 条新闻
```

### 测试 3: 测试完整流程

```bash
python3 run_agents.py --news
```

---

## 📊 API 使用估算

### 当前配置
- 每天搜索查询: 10 个
- 每个查询结果: 2 条
- 每天总调用: 10 次
- 每月总调用: 约 300 次

### 免费额度
- 每月免费: 2,000 次
- 实际使用: 300 次
- 剩余额度: 1,700 次

**结论**: 免费额度完全够用！

---

## ⚠️ 注意事项

### API 安全
- 不要将 API Key 提交到公共仓库
- 不要在客户端代码中硬编码
- 定期更换 API Key

### 使用限制
- 遵守 API 调用限制（1 QPS）
- 实现错误重试机制
- 监控 API 使用情况

### 错误处理
系统会自动处理以下错误：
- 401: API Key 无效
- 429: API 调用次数超限
- 超时: 网络请求超时

---

## 📞 故障排查

### 问题 1: API Key 无效

**错误信息**: `❌ API Key 无效`

**解决方案**:
1. 检查 API Key 是否正确
2. 确认 API Key 没有过期
3. 重新生成 API Key

### 问题 2: API 调用超限

**错误信息**: `❌ API 调用次数超限`

**解决方案**:
1. 等待下个月重置
2. 或升级到付费计划
3. 或减少搜索查询数量

### 问题 3: 没有搜索到结果

**可能原因**:
1. 搜索查询过于具体
2. API 服务暂时不可用
3. 网络连接问题

**解决方案**:
1. 检查网络连接
2. 尝试其他搜索查询
3. 查看错误日志

---

## 🎯 配置完成后

配置完成后，系统会：

1. ✅ 每天自动搜索新闻
2. ✅ 获取真实的新闻内容
3. ✅ 生成新闻简报
4. ✅ 发送到飞书

**启动调度器**:
```bash
./start_scheduler.sh
```

---

## 📁 相关文件

| 文件 | 说明 |
|------|------|
| `scripts/config_websearch.py` | WebSearch 配置工具 |
| `scripts/fetch_news_with_websearch.py` | 真实新闻获取脚本 |
| `scripts/test_websearch.py` | WebSearch 测试脚本 |
| `config/config.yaml` | 主配置文件 |
| `config/mcp_config.json` | MCP 配置文件 |

---

## 🎉 总结

**配置 Brave Search API 后，您的 CC Agent 将能够：**

- ✅ 获取真实的 AI 新闻
- ✅ 从多个来源整合内容
- ✅ 提供最新、最相关的资讯
- ✅ 自动发送到飞书

**准备好您的 API Key 后，运行以下命令配置：**

```bash
python3 scripts/config_websearch.py --config YOUR_API_KEY
```

---

**配置完成时间**: 2026-03-06
**状态**: ✅ 工具已创建，待配置 API Key
