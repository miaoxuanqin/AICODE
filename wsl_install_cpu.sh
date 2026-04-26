#!/bin/bash
export PATH=/home/mm/.local/bin:$PATH

# 安装 CPU 版本的 torch（不含 CUDA，更小更快）
pip3 install --break-system-packages torch --index-url https://download.pytorch.org/whl/cpu

# 安装其他依赖
pip3 install --break-system-packages fastapi uvicorn sentence-transformers

# 检查
python3 -c "from sentence_transformers import SentenceTransformer; print('安装成功')"
