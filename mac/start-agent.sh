#!/bin/bash
# Пуска агента без прозорец. sutrin: брифингът (при включване и в 8:00). poshta: когато в inbox/novi има нов файл.
set -u
AGENT="$HOME/moy-agent"
export PATH="$HOME/.local/bin:/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin"
cd "$AGENT" || exit 1
mkdir -p logs
MODE="${1:-sutrin}"
if [ "$MODE" = "poshta" ]; then
  N=$(find inbox/novi -type f -name '*.md' ! -name 'LEGNI-MI.md' | wc -l | tr -d ' ')
  [ "$N" -gt 0 ] || exit 0
  PROMPT="В inbox/novi има нова поща. Обработи я по умението sutreshen-brif, стъпка 2, и добави един ред в logs/poshta.log."
else
  [ -f "logs/brif-$(date +%F).md" ] && exit 0
  PROMPT="Направи сутрешния брифинг по умението sutreshen-brif."
fi
echo "=== $(date '+%F %T') $MODE" >> logs/run.log
claude -p "$PROMPT" --permission-mode acceptEdits >> logs/run.log 2>&1
