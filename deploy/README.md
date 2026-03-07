# CC Agent 云服务器部署指南

本指南帮助你将 CC Agent 部署到阿里云服务器上，实现 24/7 自动化运行。

## 📋 目录

- [快速开始](#快速开始)
- [详细部署步骤](#详细部署步骤)
- [配置说明](#配置说明)
- [常用命令](#常用命令)
- [故障排除](#故障排除)
- [更新与维护](#更新与维护)

## 🚀 快速开始

### 前提条件

- 已购买阿里云轻量应用服务器
- 服务器系统：Ubuntu 20.04/22.04
- 有服务器的 root 密码或 SSH 密钥

### 一键部署

```bash
# 1. 连接到服务器
ssh root@你的服务器IP地址

# 2. 下载并运行部署脚本
cd /opt
git clone https://github.com/sususuyiyiyi/cc_agent.git
cd cc_agent/deploy
bash install.sh

# 3. 配置飞书 webhook
bash quick_config.sh

# 4. 测试功能
bash test.sh
```

完成！🎉

## 📖 详细部署步骤

### 第 1 步：连接到服务器

```bash
# 使用密码连接
ssh root@你的服务器IP地址

# 或使用 SSH 密钥
ssh -i 你的密钥文件.pem root@你的服务器IP地址
```

### 第 2 步：下载代码

```bash
# 克隆代码仓库
cd /opt
git clone https://github.com/sususuyiyiyi/cc_agent.git
cd cc_agent
```

### 第 3 步：运行安装脚本

```bash
# 进入部署目录
cd deploy

# 运行安装脚本
bash install.sh
```

安装脚本会自动完成以下操作：
- ✅ 更新系统
- ✅ 安装 Python 和依赖
- ✅ 设置时区
- ✅ 配置防火墙
- ✅ 创建虚拟环境
- ✅ 安装依赖包
- ✅ 配置 systemd 服务
- ✅ 创建环境变量模板
- ✅ 启动调度器服务

### 第 4 步：配置飞书 Webhook

```bash
# 运行快速配置脚本
bash quick_config.sh
```

按提示输入你的飞书 Webhook URL，脚本会自动更新配置文件并发送测试消息。

**获取飞书 Webhook URL：**
1. 打开飞书群组
2. 群设置 → 机器人 → 自定义机器人
3. 创建机器人并复制 Webhook URL

### 第 5 步：测试功能

```bash
# 运行测试脚本
bash test.sh
```

测试脚本会检查：
- 服务状态
- Python 环境
- 依赖包
- 配置文件
- 新闻功能
- 日志目录
- 定时任务

## ⚙️ 配置说明

### 主要配置文件

```bash
/opt/cc_agent/config/config.yaml    # 主配置文件
/opt/cc_agent/.env                  # 环境变量（API 密钥等）
```

### 关键配置项

#### 飞书配置
```yaml
feishu:
  webhook_url: "你的飞书webhook地址"
  enabled: true
  message:
    news_enabled: true
    review_enabled: true   # 保留回顾功能
    wellness_enabled: true
```

#### 定时任务配置
```yaml
scheduling:
  enabled: true
  timezone: Asia/Shanghai
  news_su:
    enabled: true
    time: "08:00"  # 每天 8 点发送新闻
  wellness_su:
    enabled: true
    time: "08:30"  # 每天 8:30 发送健康提醒
  review_su:
    enabled: true   # 保留回顾功能
    time: "20:00"
```

#### 环境变量配置
```bash
# 在 /opt/cc_agent/.env 文件中配置
ANTHROPIC_BASE_URL=https://open.bigmodel.cn/api/anthropic
ANTHROPIC_AUTH_TOKEN=your_api_key_here
ANTHROPIC_MODEL=glm-4.5-air
TZ=Asia/Shanghai
```

### 修改配置后

```bash
# 重启服务使配置生效
systemctl restart cc_agent
```

## 🛠️ 常用命令

### 服务管理

```bash
# 启动服务
systemctl start cc_agent

# 停止服务
systemctl stop cc_agent

# 重启服务
systemctl restart cc_agent

# 查看服务状态
systemctl status cc_agent

# 查看服务日志
journalctl -u cc_agent -f

# 设置开机自启
systemctl enable cc_agent

# 禁用开机自启
systemctl disable cc_agent
```

### 查看日志

```bash
# 调度器服务日志
tail -f /opt/cc_agent/logs/scheduler_service.log

# 调度器执行日志
tail -f /opt/cc_agent/logs/scheduler_execution.log

# 健康检查数据
cat /opt/cc_agent/logs/scheduler_health.json

# 查看所有日志
ls -la /opt/cc_agent/logs/
```

### 手动运行

```bash
# 进入项目目录
cd /opt/cc_agent

# 激活虚拟环境
source venv/bin/activate

# 手动发送新闻
python3 news_agent.py

# 手动发送健康提醒
python3 wellness_agent.py

# 手动运行回顾
python3 review_agent.py
```

### 查看调度器状态

```bash
# 查看健康检查数据
cat /opt/cc_agent/logs/scheduler_health.json

# 查看已配置的任务
cat /opt/cc_agent/logs/scheduler_execution.log | grep "已配置任务"

# 查看任务执行历史
cat /opt/cc_agent/logs/scheduler_health.json | grep "last_execution"
```

## 🔧 故障排除

### 服务无法启动

```bash
# 1. 查看服务状态
systemctl status cc_agent

# 2. 查看错误日志
journalctl -u cc_agent -n 50

# 3. 手动运行查看错误
cd /opt/cc_agent
source venv/bin/activate
python3 news_agent.py
```

### 飞书消息发送失败

1. 检查 webhook URL 是否正确
2. 检查飞书机器人是否被禁用
3. 查看服务日志中的错误信息

```bash
# 测试飞书连接
cd /opt/cc_agent
source venv/bin/activate
python3 -c "
from feishu_client import FeishuClient
client = FeishuClient('你的webhook地址')
client.send_card_message('测试', '测试消息')
"
```

### 定时任务不执行

```bash
# 检查调度器健康状态
cat /opt/cc_agent/logs/scheduler_health.json

# 检查调度器执行日志
tail -50 /opt/cc_agent/logs/scheduler_execution.log

# 检查服务日志
journalctl -u cc_agent -f

# 手动测试任务
cd /opt/cc_agent && /opt/cc_agent/venv/bin/python3 news_agent.py
```

### Python 依赖问题

```bash
# 重新安装依赖
cd /opt/cc_agent
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

### 磁盘空间不足

```bash
# 查看磁盘使用情况
df -h

# 清理旧日志
find /opt/cc_agent/logs -name "*.log.old" -mtime +7 -delete

# 清理旧备份
find /opt/cc_agent_backups -type d -mtime +30 -delete
```

## 🔄 更新与维护

### 更新到最新版本

```bash
# 进入项目目录
cd /opt/cc_agent/deploy

# 运行更新脚本
bash update.sh
```

更新脚本会：
- ✅ 自动备份当前版本
- ✅ 拉取最新代码
- ✅ 更新依赖
- ✅ 重启服务

### 卸载 CC Agent

```bash
# 进入项目目录
cd /opt/cc_agent/deploy

# 运行卸载脚本
bash uninstall.sh
```

**注意：** 卸载前会询问是否备份数据。

### 定期维护

```bash
# 1. 检查服务状态
systemctl status cc_agent

# 2. 查看日志
tail -20 /opt/cc_agent/logs/cc_agent_service.log

# 3. 检查磁盘空间
df -h

# 4. 更新系统
apt update && apt upgrade -y

# 5. 运行测试
cd /opt/cc_agent/deploy && bash test.sh
```

## 📊 监控和告警

### 查看系统资源

```bash
# 查看实时资源使用
htop

# 查看内存使用
free -h

# 查看磁盘使用
df -h

# 查看 CPU 使用
top
```

### 设置监控告警

CC Agent 调度器已内置健康检查功能：
- **自动健康检查**：每小时检查调度器状态
- **任务执行监控**：记录每个任务的执行历史
- **异常通知**：任务失败或异常时发送飞书通知
- **任务丢失检测**：自动检测是否有任务丢失

监控数据位于：`/opt/cc_agent/logs/scheduler_health.json`

## 💰 成本估算

### 阿里云轻量应用服务器

| 配置 | 价格 | 年成本 |
|------|------|--------|
| 1核1GB | ¥9/月 | ¥108/年 |
| 1核2GB | ¥15/月 | ¥180/年 |
| 2核2GB | ¥24/月 | ¥288/年 |

**推荐配置：** 1核1GB 足够使用

### 其他成本

- 流量费：通常已包含
- 域名（可选）：¥50/年起
- SSL 证书（可选）：免费使用 Let's Encrypt

## 🔐 安全建议

1. **使用 SSH 密钥而非密码**
2. **定期更新系统**
3. **配置防火墙**
4. **备份重要数据**
5. **监控服务状态**

## 📞 获取帮助

遇到问题？

1. 查看日志文件
2. 运行测试脚本
3. 检查配置文件
4. 查看 GitHub Issues

## 🎉 部署完成

恭喜！你现在拥有了 24/7 自动运行的 CC Agent！

**预期效果：**
- ✅ 每天 08:00 自动发送新闻简报到飞书
- ✅ 每天 08:30 自动发送健康提醒到飞书
- ✅ 每天 20:00 自动发送晚间回顾任务到飞书（交互式，需要用户响应）
- ✅ 即使个人电脑关机，也能正常接收消息
- ✅ 服务崩溃时自动重启
- ✅ 每小时执行健康检查，异常时发送飞书通知

享受自动化带来的便利！🚀
