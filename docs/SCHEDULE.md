# CC Agent 定时任务说明

## 当前状态

系统已配置两种定时任务方式：

### 1. launchd 调度器（备用）
- **启动方式**: 开机自动启动
- **检查间隔**: 每60秒
- **优势**: 在系统运行时更可靠
- **缺点**: 电脑关闭后不会运行

### 2. cron 定时任务（主用）
- **配置文件**: `crontab -l`
- **运行时间**:
  - 📰 新闻: 每天 08:00
  - 🧘 健康: 每天 08:30
  - 📝 回顾: 每天 20:00
- **优势**: 系统级定时任务，电脑开机后会自动执行
- **日志位置**: `logs/cron_*.log`

## 确保任务运行的方法

### 方法一：保持 launchd 运行（推荐）
```bash
# 启动调度器
./manage_launchd.sh start

# 查看状态
./manage_launchd.sh status

# 查看日志
tail -f logs/scheduler.stderr.log
```

### 方法二：只使用 cron（已配置）
cron 任务已经设置好，即使电脑关闭后开机也会自动运行。

### 方法三：创建开机自启动脚本
创建一个开机脚本确保 launchd 服务运行：

```bash
# 创建开机脚本
cat > ~/Library/LaunchAgents/com.susu.ccaagent.bootstrap.plist << 'EOF'
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.susu.ccaagent.bootstrap</string>
    <key>ProgramArguments</key>
    <array>
        <string>/bin/sh</string>
        <string>-c</string>
        <string>sleep 30; launchctl load ~/Library/LaunchAgents/com.susu.ccaagent.scheduler.plist; launchctl start com.susu.ccaagent.scheduler</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
    <key>StartInterval</key>
    <integer>300</integer>
</dict>
</plist>
EOF

# 加载脚本
launchctl load ~/Library/LaunchAgents/com.susu.ccaagent.bootstrap.plist
```

## 验证任务运行

### 查看最近的运行日志
```bash
# 新闻任务日志
tail -f logs/cron_news.log

# 健康任务日志
tail -f logs/cron_wellness.log

# 回顾任务日志
tail -f logs/cron_review.log
```

### 检查 cron 任务状态
```bash
# 列出所有 cron 任务
crontab -l

# 查看 cron 运行日志
cat /var/log/cron
```

### 检查 launchd 状态
```bash
# 查看 launchd 服务状态
launchctl list | grep com.susu.ccaagent.scheduler

# 查看服务日志
log show --predicate 'senderImagePath contains "scheduler"' --debug
```

## 常见问题

### Q: 电脑休眠时任务会运行吗？
A: 不会。电脑休眠时不会执行任何任务。建议将电脑设置为不自动休眠。

### Q: 如何确保任务在指定时间运行？
A: 使用 cron 是最可靠的方式，它在系统时间到达时会自动执行。

### Q: 如何修改运行时间？
A: 编辑 crontab：
```bash
crontab -e
```

### Q: 任务运行失败怎么办？
A: 检查日志文件：
- `logs/cron_news.log` - 新闻任务日志
- `logs/cron_wellness.log` - 健康任务日志
- `logs/cron_review.log` - 回顾任务日志

## 推荐配置

**最佳实践**：同时使用 launchd 和 cron
- launchd 作为主调度器（实时监控）
- cron 作为备用方案（确保电脑开机后执行）

这样可以确保：
1. 电脑运行时，任务每60秒检查一次
2. 即使电脑关闭后开机，cron 也会在指定时间执行任务