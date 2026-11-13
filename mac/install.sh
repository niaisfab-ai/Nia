#!/bin/bash
# Включва двете будилки на агента (Mac). Папката трябва да е в ~/moy-agent: macOS не пуска фонови задачи в Desktop, Documents и Downloads.
set -e
[ -d "$HOME/moy-agent" ] || { echo "Сложете папката moy-agent в $HOME (не в Desktop или Documents)."; exit 1; }
command -v claude >/dev/null || [ -x "$HOME/.local/bin/claude" ] || { echo "Първо инсталирайте Claude Code."; exit 1; }
mkdir -p "$HOME/Library/LaunchAgents"
for f in com.moy-agent.sutrin com.moy-agent.poshta; do
  sed "s|__HOME__|$HOME|g" "$HOME/moy-agent/mac/$f.plist" > "$HOME/Library/LaunchAgents/$f.plist"
  launchctl bootout "gui/$(id -u)/$f" 2>/dev/null || true
  launchctl bootstrap "gui/$(id -u)" "$HOME/Library/LaunchAgents/$f.plist"
done
echo "Готово. Проверка: launchctl list | grep moy-agent. Логът: ~/moy-agent/logs/run.log"
