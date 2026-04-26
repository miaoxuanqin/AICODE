#!/bin/bash
cat /home/mm/embedding/embedding.log 2>/dev/null || echo "日志文件不存在"
# 检查端口
netstat -tlnp 2>/dev/null | grep 8001 || ss -tlnp | grep 8001 || echo "端口8001未监听"
