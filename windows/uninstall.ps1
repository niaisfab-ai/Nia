foreach ($t in "Moy agent pri vlizane", "Moy agent 8-00", "Moy agent poshta") { schtasks /delete /tn $t /f }
Write-Host "Будилките са изключени."
