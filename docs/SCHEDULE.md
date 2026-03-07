# CC Agent 定时任务说明

## 为什么一关电脑 / 关终端，定时就失效？

常见有两种情况：

1. **你是用「终端里运行」或 `./start_scheduler.sh` 启动的**  
   调度器是当前终端里的一个进程，关掉终端或关掉电脑，进程就没了，定时自然不会再跑。

2. **即使用 launchd，合盖/休眠时也不会跑**  
   Mac 合盖或休眠后，系统不会执行任何用户程序，所以 8:00 的新闻如果在合盖/休眠期间，就不会触发。只有**电脑处于开机、未休眠**时，定时任务才会在设定时间执行。

**正确做法**：用 **launchd** 把调度器当成「后台服务」跑，这样：
- 关掉终端不会停（服务在后台）
- 开机/登录后可以自动拉起（配合 `RunAtLoad`）
- 合盖/休眠时仍不会跑——若希望合盖时也能准时收新闻，需要机器在到点时不休眠（插电 + 系统设置里不自动休眠），或把任务放到「一直开着的机器/云上」跑。

---

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

### 方法一：用 launchd 后台跑（推荐，关终端也不停）
```bash
# 1）首次使用：安装 launchd 配置（把 plist 装到 ~/Library/LaunchAgents）
./manage_launchd.sh install

# 2）在项目根目录建 .env，写上模型 API 等（供定时任务用）
#    例如：ANTHROPIC_BASE_URL=... ANTHROPIC_AUTH_TOKEN=... ANTHROPIC_MODEL=glm-4.5-air

# 3）启动服务（之后关掉终端也会在后台跑）
./manage_launchd.sh start

# 查看状态
./manage_launchd.sh status

# 查看日志
./manage_launchd.sh logs
# 或 tail -f logs/scheduler.stderr.log
```

### 方法二：只使用 cron（已配置）
cron 任务已经设置好，即使电脑关闭后开机也会自动运行。

### 方法三：开机自启（可选）
用 `./manage_launchd.sh install` 装好的 plist 里已设置 `RunAtLoad`，**登录后 launchd 会自动加载**；若你希望每次开机再显式拉起一次，可再做一个 bootstrap plist（一般不需要）。

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