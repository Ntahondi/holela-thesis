# SMMS Backend PowerShell Launcher
Write-Host "=========================================================================" -ForegroundColor Cyan
Write-Host " Starting SMMS Analytical & Decision Support Microservice (FastAPI)" -ForegroundColor Green
Write-Host " API Docs available at: http://localhost:8000/docs" -ForegroundColor Yellow
Write-Host " WebSocket Stream at: ws://localhost:8000/api/v1/telemetry/ws/{asset_id}" -ForegroundColor Yellow
Write-Host "=========================================================================" -ForegroundColor Cyan

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $ScriptDir
& "$ScriptDir\venv\Scripts\python.exe" -m uvicorn main:app --app-dir backend/app --host 0.0.0.0 --port 8000 --reload
