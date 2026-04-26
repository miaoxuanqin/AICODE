#!/bin/bash
cd /home/mm/embedding
export PATH=/home/mm/.local/bin:$PATH
nohup python3 embedding_service.py > embedding.log 2>&1 &
sleep 5
cat embedding.log
