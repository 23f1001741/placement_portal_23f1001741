@echo off
echo ===================================================
echo   Starting Placement Portal (MAD2 Project)
echo ===================================================

echo [1/6] Starting Redis Server...
start "Redis Server" cmd /k "wsl redis-server"

echo [2/6] Starting MailHog...
:: This looks for the file in the root directory where run.bat is located.
if exist "MailHog.exe" (
    start "MailHog" cmd /k "MailHog.exe"
) else (
    echo WARNING: MailHog_windows_amd64.exe not found in root. 
    echo Please download it as per README instructions.
    pause
)

echo [3/6] Starting Flask Backend API...
start "Flask API" cmd /k "cd backend && venv\Scripts\activate && python app.py"

echo [4/6] Starting Celery Worker...
start "Celery Worker" cmd /k "cd backend && venv\Scripts\activate && celery -A app.celery worker --pool=solo --loglevel=info"

echo [5/6] Starting Celery Beat Scheduler...
start "Celery Beat" cmd /k "cd backend && venv\Scripts\activate && celery -A app.celery beat --loglevel=info"

echo [6/6] Starting Vue.js Frontend...
start "Vue Frontend" cmd /k "cd frontend && npm run dev"

echo.
echo ===================================================
echo All services have been launched!
echo.
echo Web UI: http://localhost:5173
echo MailHog UI: http://localhost:8025
echo ===================================================
pause