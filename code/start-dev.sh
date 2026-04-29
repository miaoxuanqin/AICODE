#!/bin/bash
echo "===================================="
echo "知识库系统开发环境启动"
echo "===================================="

echo ""
echo "[1/2] 启动后端服务 (端口 8001)..."
cd "$(dirname "$0")/code/backend"
python -m uvicorn app.main:app --host 0.0.0.0 --port 8001 &
BACKEND_PID=$!

echo "等待后端启动..."
sleep 3

echo ""
echo "[2/2] 启动前端服务 (端口 3000)..."
cd "$(dirname "$0")/code/frontend"
npm run dev &
FRONTEND_PID=$!

echo ""
echo "===================================="
echo "启动完成！"
echo "前端: http://localhost:3000"
echo "后端: http://localhost:8001"
echo "API文档: http://localhost:8001/docs"
echo "===================================="
echo ""
echo "按 Ctrl+C 停止所有服务"
trap "kill $BACKEND_PID $FRONTEND_PID 2>/dev/null" EXIT
wait