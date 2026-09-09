# SMMS Client PowerShell Launcher (Microsoft Edge)
Write-Host "=========================================================================" -ForegroundColor Cyan
Write-Host " Launching SMMS Civil Engineering Client on Microsoft Edge" -ForegroundColor Green
Write-Host " Target: flutter run -d edge" -ForegroundColor Yellow
Write-Host "=========================================================================" -ForegroundColor Cyan

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location "$ScriptDir\client"
flutter run -d edge
