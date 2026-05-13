@echo off
chcp 65001 >nul
echo ====================================
echo Knowledge Base System Dev Launcher
echo ====================================

echo.
echo [1/2] Starting backend (port 8000)...
cd /d C:\AICODE3\code\backend
start "Backend" cmd /k "python -m uvicorn app.main:app --host 0.0.0.0 --port 8000"

echo Waiting for backend to initialize...
timeout /t 4 /nobreak >nul

echo.
echo [2/2] Starting frontend (port 3000)...
cd /d C:\AICODE3\code\frontend
start "Frontend" cmd /k "npm run dev"

echo.
echo ====================================
echo Startup complete!
echo Frontend: http://localhost:3000
echo Backend:  http://localhost:8000
echo API Docs:  http://localhost:8000/docs
echo ====================================
echo.
echo NOTE: Close the Backend and Frontend windows to stop services
echo Press any key to exit this launcher...
pause >nul