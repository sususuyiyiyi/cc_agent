# CC Agent - 个人生活助理团队

> 🤖 基于 Claude Skills 的个人生活助理系统，包含资讯、健康建议和日报三个智能代理。

## 📖 项目说明

CC Agent 是一个个人生活助理团队，包含三个 AI 助手：

- **资讯su** (news-su) - 每日早上获取 AI 资讯和新闻，生成简报并发送到飞书
- **营养师su** (wellness-su) - 根据天气提供饮食和穿搭建议
- **复盘su** (review-su) - 每日晚上进行复盘，生成日报

### 本项目与 Claude Code

本仓库也用于配合 Claude Code 测试与开发。你可以在终端进入本项目目录后运行：

```bash
cd /Users/sususu/cc_agent
claude
```

即可在当前项目中使用 Claude Code 进行编码辅助。

---

## 🚀 快速开始

### 1. 安装依赖

```bash
# 使用安装脚本（推荐）
chmod +x install.sh
./install.sh

# 或手动安装
pip3 install -r requirements.txt
```

### 2. 配置系统

```bash
# 交互式配置
python3 configure.py

# 或命令行配置
python3 configure.py --websearch YOUR_API_KEY
python3 configure.py --weather openweathermap YOUR_API_KEY
python3 configure.py --feishu YOUR_WEBHOOK_URL
python3 configure.py --enable-scheduling
```

### 3. 运行 Agents

```bash
# 交互式运行
python3 run_agents.py

# 或命令行运行
python3 run_agents.py --news      # 运行资讯su
python3 run_agents.py --wellness  # 运行营养师su
python3 run_agents.py --review    # 运行复盘su
python3 run_agents.py --all       # 运行所有agents
```

### 4. 查看状态

```bash
python3 run_agents.py --status
```

---

## 🔧 配置说明

### 必需配置

#### 1. WebSearch 配置（用于新闻获取）

注册 Brave Search API: https://brave.com/search/api/

```bash
python3 configure.py --websearch YOUR_API_KEY
```

#### 2. 天气 API 配置

**选项 A - OpenWeatherMap（推荐）**
```bash
python3 configure.py --weather openweathermap YOUR_API_KEY
```

**选项 B - 和风天气**
```bash
python3 configure.py --weather qweather YOUR_API_KEY
```

### 可选配置

#### 3. 飞书集成

1. 在飞书群聊中添加群机器人
2. 复制 Webhook URL
3. 运行配置

```bash
python3 configure.py --feishu YOUR_WEBHOOK_URL
```

#### 4. 启用定时任务

```bash
python3 configure.py --enable-scheduling
```

或手动编辑 `config/config.yaml` 中的 `scheduling.enabled = true`

---

## 📁 项目结构

```
cc_agent/
├── skills/                  # Skills 定义
│   ├── news-su/            # 资讯su
│   ├── wellness-su/        # 营养师su
│   └── review-su/          # 复盘su
├── data/                   # 数据存储
│   ├── news/              # 新闻存档
│   ├── wellness/          # 健康建议存档
│   └── reviews/           # 日报存档
├── config/                # 配置文件
│   ├── config.yaml        # 主配置
│   └── mcp_config.json    # MCP 配置
├── agents/                # Agent 实现
│   ├── news_agent.py
│   ├── wellness_agent.py
│   └── review_agent.py
├── run_agents.py          # 主程序
├── scheduler.py           # 任务调度器
├── configure.py           # 配置工具
├── feishu_client.py       # 飞书客户端
├── mcp_tools.py           # MCP 工具管理
├── test_skills.py         # 测试脚本
├── install.sh             # 安装脚本
├── requirements.txt       # 依赖列表
├── 信息输入.md             # 设计文档
├── 测试报告.md             # 测试报告
├── 使用指南.md             # 使用说明
└── README.md              # 本文档
```

---

## 🧪 测试

```bash
# 运行完整测试
python3 test_skills.py

# 测试飞书连接
python3 feishu_client.py --test

# 查看配置状态
python3 mcp_tools.py --status
```

---

## 📊 系统状态

当前配置状态：

- ✅ Skills 设计完成（3个）
- ✅ 目录结构建立
- ✅ 工作流程验证
- ⏳ MCP 工具配置（需要配置）
- ⏳ 天气 API 配置（需要配置）
- ⏳ 飞书集成（可选）
- ⏳ 定时任务（可选）

运行 `python3 configure.py --status` 查看详细状态。

---

## 📚 更多文档

- **设计文档**: `信息输入.md` - 包含 Skills 创建指南
- **使用指南**: `使用指南.md` - 详细使用说明
- **测试报告**: `测试报告.md` - 测试结果总结

---

## 🤝 Claude Code 命令说明

以下命令在 Claude Code 的终端界面中使用（以 `/` 开头）：

- **/add-dir**：添加新的工作目录
- **/agents**：查看和管理代理配置
- **/clear**：清空当前对话历史
- **/config**：打开配置面板
- **/help**：显示帮助信息
- **/mcp**：管理 MCP 服务器
- **/memory**：编辑 Claude 的记忆文件
- **/status**：显示 Claude Code 的整体状态

> 更多关于 Claude Code 的介绍和使用方式，可参考官方概览文档：`https://code.claude.com/docs/en/overview`

---

## 📞 支持

如有问题或建议，请参考相关文档或查看 GitHub Issues。

---

**祝您使用愉快！** 🎉


