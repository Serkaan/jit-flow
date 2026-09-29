# Yönetici PowerShell ile çalıştırın. NSSM kurulu olmalıdır.
$Root=(Split-Path $PSScriptRoot -Parent)
$Py="$Root\.venv\Scripts\python.exe"
$nssm=(Get-Command nssm -ErrorAction Stop).Source
& $nssm install JITFlow-API $Py '-m uvicorn app.main:app --host 0.0.0.0 --port 8080'
& $nssm set JITFlow-API AppDirectory $Root
& $nssm set JITFlow-API Start SERVICE_AUTO_START
& $nssm install JITFlow-UI $Py '-m streamlit run app/ui.py --server.address 0.0.0.0 --server.port 8501 --server.headless true'
& $nssm set JITFlow-UI AppDirectory $Root
& $nssm set JITFlow-UI Start SERVICE_AUTO_START
Start-Service JITFlow-API; Start-Service JITFlow-UI
Write-Host 'Servisler kuruldu: API 8080, UI 8501'
