#!/bin/bash
# 停止现有进程
pkill -f embedding_service || true
sleep 2
cd /home/mm/embedding
export PATH=/home/mm/.local/bin:$PATH
nohup python3 embedding_service.py > /tmp/embedding.log 2>&1 &
sleep 30
cat /tmp/embedding.log
echo "---检查端口---"
ss -tlnp | grep 8001 || netstat -tlnp | grep 8001 || echo "端口8001未监听"
