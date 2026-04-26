#!/bin/bash
if [ -f /home/mm/embedding/embedding_service.py ]; then
    echo "文件已存在"
    head -5 /home/mm/embedding/embedding_service.py
else
    echo "文件不存在"
fi
ls -la /home/mm/embedding/ 2>/dev/null || echo "目录不存在"
