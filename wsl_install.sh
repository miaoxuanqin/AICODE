#!/bin/bash
export PATH=/home/mm/.local/bin:$PATH
pip3 install --break-system-packages fastapi uvicorn sentence-transformers 2>&1
echo "安装完成"
