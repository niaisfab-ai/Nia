param([string]$Mode = "sutrin")
# Пуска агента без прозорец. sutrin: брифингът (при влизане в Windows и в 8:00). poshta: когато в inbox\novi има нов файл.
$Agent = Join-Path $HOME "moy-agent"
Set-Location $Agent
New-Item -ItemType Directory -Force -Path logs | Out-Null
if ($Mode -eq "poshta") {
  $new = Get-ChildItem inbox\novi -Filter *.md | Where-Object { $_.Name -ne "LEGNI-MI.md" }
  if (-not $new) { exit 0 }
  $Prompt = "В inbox/novi има нова поща. Обработи я по умението sutreshen-brif, стъпка 2, и добави един ред в logs/poshta.log."
} else {
  if (Test-Path ("logs\brif-" + (Get-Date -Format "yyyy-MM-dd") + ".md")) { exit 0 }
  $Prompt = "Направи сутрешния брифинг по умението sutreshen-brif."
}
Add-Content logs\run.log ("=== " + (Get-Date -Format "yyyy-MM-dd HH:mm:ss") + " " + $Mode)
claude -p $Prompt --permission-mode acceptEdits *>> logs\run.log
