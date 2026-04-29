@echo off
chcp 65001 >nul
echo ====================================
echo 知识库系统开发环境启动
echo ====================================

echo.
echo [1/2] 启动后端服务 (端口 8001)...
cd /d %~dp0code\backend
start "Backend" cmd /c "python -m uvicorn app.main:app --host 0.0.0.0 --port 8001"

echo 等待后端启动...
timeout /t 3 /nobreak >nul

echo.
echo [2/2] 启动前端服务 (端口 3000)...
cd /d %~dp0code\frontend
start "Frontend" cmd /c "npm run dev"

echo.
echo ====================================
echo 启动完成！
echo 前端: http://localhost:3000
echo 后端: http://localhost:8001
echo API文档: http://localhost:8001/docs
echo ====================================
pause