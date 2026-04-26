#!/bin/bash
# 检查服务是否在运行
ps aux | grep -v grep | grep "embedding_service" && echo "服务运行中"
# 检查health接口
curl -s http://localhost:8001/health 2>&1 || echo "服务未响应"
