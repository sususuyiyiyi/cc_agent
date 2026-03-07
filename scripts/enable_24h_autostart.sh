#!/bin/bash
# 一键开启「24 小时自动执行」：安装 launchd 并启动调度器，关终端也会在后台按点跑

set -e
PROJECT_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$PROJECT_ROOT"

echo "============================================================"
echo "⏰ CC Agent 24 小时自动执行 - 一键设置"
echo "============================================================"
echo ""
echo "当前每日定时（config/config.yaml）："
echo "  📰 资讯su  08:00"
echo "  🥗 营养师su 08:30"
echo "  📝 复盘su  20:00"
echo ""

# 1. 检查 .env（提醒，不强制）
if [ ! -f "$PROJECT_ROOT/.env" ]; then
  echo "⚠️ 未发现 .env，定时任务里的模型调用可能失败。"
  echo "   建议在项目根目录创建 .env，内容示例："
  echo "   ANTHROPIC_BASE_URL=https://open.bigmodel.cn/api/anthropic"
  echo "   ANTHROPIC_AUTH_TOKEN=你的key"
  echo "   ANTHROPIC_MODEL=glm-4.5-air"
  echo ""
  read -p "是否继续安装？(y/N) " -n 1 r; echo
  if [ "$r" != "y" ] && [ "$r" != "Y" ]; then
    echo "已取消。配置好 .env 后再运行: ./scripts/enable_24h_autostart.sh"
    exit 0
  fi
fi

# 2. 安装 launchd
echo "📦 安装 launchd 配置..."
./manage_launchd.sh install

# 3. 若已在跑则先停
if launchctl list 2>/dev/null | grep -q "com.susu.ccaagent.scheduler"; then
  echo "🛑 停止旧服务..."
  ./manage_launchd.sh stop
  sleep 2
fi

# 4. 启动
echo ""
echo "🚀 启动调度器（后台常驻）..."
./manage_launchd.sh start

echo ""
echo "============================================================"
echo "✅ 已设置 24 小时自动执行"
echo "============================================================"
echo ""
echo "说明："
echo "  - 调度器已在后台运行，关掉终端也会按点执行。"
echo "  - 每天 08:00 新闻、08:30 健康建议、20:00 复盘（可在 config/config.yaml 改时间）。"
echo "  - 合盖/休眠时不会执行，需电脑处于开机且未休眠。"
echo ""
echo "常用命令："
echo "  查看状态: ./manage_launchd.sh status"
echo "  查看日志: ./manage_launchd.sh logs"
echo "  停止:     ./manage_launchd.sh stop"
echo "  重启:     ./manage_launchd.sh restart"
echo ""
