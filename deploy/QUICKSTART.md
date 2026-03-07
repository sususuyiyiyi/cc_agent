# 阿里云服务器快速部署指南

## 📌 前提条件
- ✅ 已购买阿里云轻量应用服务器
- ✅ 服务器系统：Ubuntu 20.04/22.04
- ✅ 有服务器的 root 密码

## 🚀 5 分钟快速部署

### 1️⃣ 连接到服务器

```bash
# 使用密码连接
ssh root@你的服务器IP地址

# 输入密码后进入服务器
```

### 2️⃣ 下载并安装

```bash
# 克隆代码
cd /opt
git clone https://github.com/sususuyiyiyi/cc_agent.git

# 进入部署目录
cd cc_agent/deploy

# 运行安装脚本（需要 5-10 分钟）
bash install.sh
```

### 3️⃣ 配置飞书

```bash
# 运行配置脚本
bash quick_config.sh

# 输入你的飞书 Webhook URL
```

**获取飞书 Webhook URL：**
1. 打开飞书群组
2. 群设置 → 机器人 → 自定义机器人
3. 创建机器人并复制 Webhook URL

### 4️⃣ 测试功能

```bash
# 运行测试脚本
bash test.sh
```

### 5️⃣ 完成！🎉

现在每天早上 8 点会自动收到新闻播报，8:30 收到健康提醒，20:00 收到晚间回顾任务！即使你的电脑关机也没关系！

---

## 📋 常用命令

```bash
# 查看服务状态
systemctl status cc_agent

# 重启服务
systemctl restart cc_agent

# 查看调度器日志
tail -f /opt/cc_agent/logs/scheduler_execution.log

# 查看服务日志
tail -f /opt/cc_agent/logs/scheduler_service.log

# 查看健康检查数据
cat /opt/cc_agent/logs/scheduler_health.json

# 手动测试功能
cd /opt/cc_agent && source venv/bin/activate
python3 news_agent.py     # 测试新闻
python3 wellness_agent.py  # 测试健康提醒
python3 review_agent.py    # 测试回顾
```

---

## 🔧 遇到问题？

### 服务无法启动
```bash
# 查看错误日志
journalctl -u cc_agent -n 50

# 查看调度器执行日志
tail -f /opt/cc_agent/logs/scheduler_execution.log

# 查看服务日志
tail -f /opt/cc_agent/logs/scheduler_service.log
```

### 飞书消息发送失败
```bash
# 重新配置 webhook
bash quick_config.sh
```

### 更新到最新版本
```bash
cd /opt/cc_agent/deploy
bash update.sh
```

---

## 💰 成本参考

- 阿里云轻量应用服务器（1核1GB）：约 ¥9/月
- 年成本：约 ¥108/年

---

## 📖 完整文档

详细文档请查看：`deploy/README.md`

---

## ✅ 部署检查清单

- [ ] 连接到服务器
- [ ] 运行安装脚本
- [ ] 配置飞书 webhook
- [ ] 配置 API 密钥（编辑 /opt/cc_agent/.env）
- [ ] 测试功能正常
- [ ] 确认服务开机自启
- [ ] 查看健康检查数据

---

**需要帮助？** 查看完整文档或检查日志文件
