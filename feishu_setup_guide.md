# 飞书配置指南

## 📱 创建飞书群机器人

### 第一步：打开群聊设置

1. 在飞书中打开目标群聊
2. 点击群聊右上角的 **"..."** 菜单
3. 选择 **"设置"**

### 第二步：添加群机器人

1. 点击 **"群机器人"**
2. 点击 **"添加机器人"**
3. 选择 **"自定义机器人"**

### 第三步：配置机器人

1. 输入机器人名称（例如：CC Agent）
2. （可选）添加机器人描述
3. 点击 **"添加"**

### 第四步：获取 Webhook URL

创建成功后，您会看到一个 Webhook URL，格式类似：

```
https://open.feishu.cn/open-apis/bot/v2/hook/xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
```

**重要**：请妥善保管这个 URL，不要泄露给他人。

---

## 🔧 配置 CC Agent

### 方法一：交互式配置

```bash
cd /Users/sususu/cc_agent
python3 configure.py
```

选择菜单中的 **"3. 配置飞书集成"**，然后粘贴您的 Webhook URL。

### 方法二：命令行配置

```bash
cd /Users/sususu/cc_agent
python3 configure.py --feishu YOUR_WEBHOOK_URL
```

将 `YOUR_WEBHOOK_URL` 替换为您实际的 Webhook URL。

---

## 🧪 测试飞书连接

### 方法一：使用测试命令

```bash
python3 feishu_client.py --test
```

### 方法二：手动测试

```python
from feishu_client import FeishuClient

# 替换为您的 Webhook URL
webhook_url = "https://open.feishu.cn/open-apis/bot/v2/hook/your-webhook-url"

client = FeishuClient(webhook_url)
client.send_text("🧪 测试消息 - CC Agent 飞书集成测试成功！")
```

---

## ✅ 验证配置

```bash
# 查看配置状态
python3 configure.py --status

# 或
python3 feishu_client.py
```

---

## 📝 飞书机器人可以发送的内容

CC Agent 可以通过飞书机器人发送以下内容：

1. **新闻简报** - 每日 AI 资讯和新闻
2. **健康建议** - 根据天气的饮食和穿搭建议
3. **日报** - 每日复盘和总结

---

## 🔐 安全注意事项

1. **不要泄露 Webhook URL**
   - Webhook URL 相当于密码，任何拥有这个 URL 的人都可以向群聊发送消息

2. **定期更新**
   - 如果怀疑 URL 泄露，可以删除机器人并重新创建

3. **权限控制**
   - 确保只有信任的成员可以添加群机器人

---

## 🚀 开始使用

配置完成后，您可以通过以下方式发送消息到飞书：

### 1. 运行资讯su 并发送到飞书

```bash
python3 run_agents.py --news
```

### 2. 运行营养师su 并发送到飞书

```bash
python3 run_agents.py --wellness
```

### 3. 运行复盘su 并发送到飞书

```bash
python3 run_agents.py --review
```

### 4. 运行所有 agents 并发送到飞书

```bash
python3 run_agents.py --all
```

---

## ❓ 常见问题

### Q: 消息发送失败怎么办？

A: 检查以下几点：
1. Webhook URL 是否正确
2. 网络连接是否正常
3. 飞书群是否已解散或机器人是否被删除
4. 查看错误日志了解具体原因

### Q: 如何修改飞书 Webhook URL？

A: 运行配置命令重新设置：

```bash
python3 configure.py --feishu NEW_WEBHOOK_URL
```

或编辑 `config/config.yaml` 文件中的 `feishu.webhook_url` 字段。

### Q: 飞书机器人消息有限制吗？

A: 是的，飞书群机器人有以下限制：
- 消息频率：每分钟最多 20 条
- 消息类型：支持文本、富文本、卡片等

---

## 📚 更多信息

- **飞书机器人文档**: https://open.feishu.cn/document/ukTMukTMukTM/ucTM5YjL3ETO24yNkjAE
- **CC Agent 使用指南**: `使用指南.md`
- **CC Agent 快速配置**: `快速配置指南.md`

---

**配置完成后，您的飞书群聊就能收到 CC Agent 发送的消息了！** 🎉
