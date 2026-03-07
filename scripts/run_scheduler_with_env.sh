#!/bin/bash
# 供 launchd 调用：加载项目 .env 后再运行调度器（保证 ANTHROPIC_* 等环境变量生效）

PROJECT_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$PROJECT_ROOT"

# 加载 .env（若存在），避免把密钥写进 plist
if [ -f "$PROJECT_ROOT/.env" ]; then
  set -a
  source "$PROJECT_ROOT/.env"
  set +a
fi

mkdir -p "$PROJECT_ROOT/logs"
exec python3 "$PROJECT_ROOT/scheduler.py"
