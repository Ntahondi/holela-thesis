@echo off
echo =========================================================================
echo  Starting SMMS Analytical & Decision Support Microservice (FastAPI)
echo =========================================================================
cd /d "%~dp0"
call venv\Scripts\activate.bat
python -m uvicorn main:app --app-dir backend/app --host 0.0.0.0 --port 8000 --reload
pause
