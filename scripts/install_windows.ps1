$ErrorActionPreference='Stop'
Set-Location (Split-Path $PSScriptRoot -Parent)
if (!(Test-Path .venv)) { py -3.12 -m venv .venv }
& .\.venv\Scripts\python.exe -m pip install --upgrade pip
& .\.venv\Scripts\pip.exe install -r requirements.txt
if (!(Test-Path .env)) { Copy-Item .env.example .env }
Write-Host 'Kurulum tamam. Baslatmak icin: .\.venv\Scripts\python.exe run_all.py'
