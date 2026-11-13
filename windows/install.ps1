# Включва будилките на агента (Windows). Пуснете PowerShell като администратор, после: powershell -ExecutionPolicy Bypass -File $HOME\moy-agent\windows\install.ps1
$ps = Join-Path $HOME "moy-agent\windows\start-agent.ps1"
if (-not (Test-Path $ps)) { Write-Host "Сложете папката moy-agent в $HOME"; exit 1 }
$run = "powershell -NoProfile -ExecutionPolicy Bypass -WindowStyle Hidden -File `"$ps`""
schtasks /create /tn "Moy agent pri vlizane" /sc onlogon /tr "$run sutrin" /f
schtasks /create /tn "Moy agent 8-00" /sc daily /st 08:00 /tr "$run sutrin" /f
schtasks /create /tn "Moy agent poshta" /sc minute /mo 15 /tr "$run poshta" /f
Write-Host "Готово. Проверка: schtasks /query /tn ""Moy agent poshta"". Логът: $HOME\moy-agent\logs\run.log"
