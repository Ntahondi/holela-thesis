@echo off
echo =========================================================================
echo  Starting SMMS Client Application (Microsoft Edge Web Target)
echo =========================================================================
cd /d "%~dp0client"
flutter run -d edge
pause
