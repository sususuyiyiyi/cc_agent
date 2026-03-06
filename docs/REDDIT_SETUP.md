# Reddit API 配置指南

## 为什么需要 Reddit？

Reddit 是一个热门的讨论社区，有很多优质的科技和 AI 相关子版块（subreddits），包括：
- r/artificial - 人工智能讨论
- r/MachineLearning - 机器学习
- r/ArtificialIntelligence - AI 资讯
- r/ChatGPT - ChatGPT 讨论
- r/openai - OpenAI 相关
- r/localLLaMA - 本地大模型
- r/technology - 科技新闻
- r/programming - 编程

## 如何配置 Reddit API

### 步骤 1: 创建 Reddit App

1. 访问 https://www.reddit.com/prefs/apps
2. 点击 "create app" 或 "create another app"
3. 填写表单：
   - **name**: 你的应用名称（例如：CC-Agent News）
   - **app type**: 选择 **script**
   - **description**: 可选，填写应用描述
   - **about url**: 可选，可以填 https://github.com/your-repo
   - **redirect uri**: 必须填 `http://localhost:8080`
4. 点击 "create app"

### 步骤 2: 获取 API 凭据

创建应用后，你会看到以下信息：
- **client ID**: 在 app information 下方的 14 字符字符串
- **client secret**: 在 client ID 下方的密码字符串

### 步骤 3: 配置到你的系统

编辑 `config/news_apis.yaml` 文件：

```yaml
reddit:
  enabled: true  # 改为 true
  client_id: "你的_client_id"  # 替换为你的 client ID
  client_secret: "你的_client_secret"  # 替换为你的 client secret
  user_agent: "CC-Agent:v1.0:by /u/你的Reddit用户名"
  rate_limit: 60
```

**注意**: 将 user_agent 中的 `你的Reddit用户名` 替换为你的 Reddit 用户名。

### 步骤 4: 启用新闻聚合器

编辑 `config/config.yaml` 文件：

```yaml
preferences:
  news:
    use_aggregator: true  # 启用新闻聚合器
```

### 步骤 5: 测试

运行测试脚本：

```bash
python3 scripts/fetch_news_reddit_api.py --category ai --max 5
```

或使用聚合器：

```bash
python3 scripts/news_aggregator.py
```

## API 限制

Reddit API 有以下限制：
- **认证后**: 每分钟 60 次请求
- **未认证**: 请求会被限制或拒绝
- **建议**: 每天获取一次新闻即可，不会超过限制

## 注意事项

1. **不要共享凭据**: client_id 和 client_secret 是敏感信息，不要分享给他人
2. **不要滥用**: 遵守 Reddit API 使用条款
3. **User-Agent 格式**: 必须使用正确的格式 `<platform>:<appID>:<version> (by /u/<username>)`
4. **尊重社区**: 获取新闻是只读操作，不会发布或评论

## 故障排除

### 问题 1: 认证失败
- 检查 client_id 和 client_secret 是否正确
- 确保应用类型是 "script"
- 检查 user_agent 格式是否正确

### 问题 2: 请求被限制
- Reddit 可能有临时限制，稍后重试
- 确保已正确认证

### 问题 3: 获取不到数据
- 检查 subreddit 名称是否正确
- 某些 subreddit 可能是私有的

## 示例配置

```yaml
# config/news_apis.yaml
reddit:
  enabled: true
  client_id: "aBcDeFgHiJkLmN"
  client_secret: "xYz1234567890"
  user_agent: "CC-Agent:v1.0:by /u/myusername"
  rate_limit: 60
  subreddits:
    ai:
      - artificial
      - MachineLearning
      - ChatGPT
      - openai
    tech:
      - technology
      - programming
```

## 更多信息

- Reddit API 文档: https://www.reddit.com/dev/api/
- Reddit App 创建: https://www.reddit.com/prefs/apps
- OAuth 2.0 说明: https://github.com/reddit-archive/reddit/wiki/OAuth2
