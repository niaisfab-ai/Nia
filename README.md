# Моят агент · стартова папка

Агент с памет, умения, проверител, пощенска кутия за други агенти и будилки. Ръководството е в PDF-а „Вашият агент с Claude Code“.

1. Сложете папката moy-agent в домашната папка: ~/moy-agent на Mac, C:\Users\<вие>\moy-agent на Windows. Не в Desktop или Documents.
2. Попълнете CLAUDE.md, раздел „Кой съм аз“, и първата задача в zadachi.md.
3. Пуснете claude в папката и напишете: „Направи сутрешния брифинг.“ Проверете logs.
4. Будилките: Mac: bash ~/moy-agent/mac/install.sh. Windows: install.ps1 (PowerShell като администратор).
5. Изключване: mac/uninstall.sh или windows/uninstall.ps1.

Какво има вътре:
- CLAUDE.md: правилата и паметта, агентът ги чете при всеки старт.
- pamet: паметта, един файл за един факт, и INDEX.md.
- .claude/skills: zapomni, sutreshen-brif, pishi-na-agent.
- .claude/agents/proveritel.md: проверител с чужди очи.
- .claude/settings.json: разрешенията и куката при старт, която показва паметта и новата поща.
- inbox/novi и inbox/gotovi: пощенската кутия.
- mac и windows: будилките.
