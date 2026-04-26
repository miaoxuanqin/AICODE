#!/bin/bash
set -e

# 1. 安装依赖
export PATH=/home/mm/.local/bin:$PATH
pip3 install --break-system-packages fastapi uvicorn sentence-transformers

# 2. 检查模型
python3 -c "from sentence_transformers import SentenceTransformer; print('模型可用')"

# 3. 启动服务
cd /home/mm/embedding
python3 embedding_service.py
