#!/bin/bash
export PATH=/home/mm/.local/bin:$PATH
python3 -c "from sentence_transformers import SentenceTransformer; print('sentence-transformers OK')" 2>&1
pip3 list | grep -i "torch\|fastapi\|sentence" 2>&1
