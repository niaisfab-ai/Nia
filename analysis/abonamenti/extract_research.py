"""Извлича дословно финалния отговор на researcher агент от JSONL транскрипта му и го записва като файл-източник.
Употреба: python3 analysis/abonamenti/extract_research.py <transcript.output> <изходен.md> "<заглавие>"
Причина: правилото в CLAUDE.md забранява съкращаване на отговора при запис (грешката се повтори 4 пъти при ръчно преписване)."""
import json
import sys

src, dst, title = sys.argv[1], sys.argv[2], sys.argv[3]
msg = None
for ln in open(src, encoding="utf-8"):
    try:
        d = json.loads(ln)
    except ValueError:
        continue
    for part in (d.get("message") or {}).get("content") or []:
        if isinstance(part, dict) and part.get("type") == "tool_use" and part.get("name") == "SubagentHandback":
            msg = part["input"]["message"]
if msg is None:
    sys.exit("няма SubagentHandback в " + src)
with open(dst, "w", encoding="utf-8") as f:
    f.write(f"# Researcher: {title}\nДата на събиране: 2026-11-13. Дословен отговор на researcher-а (извлечен със скрипт, без редакция).\n\n")
    f.write(msg.strip() + "\n")
print(dst, len(msg), "знака")
