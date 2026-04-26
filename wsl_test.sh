#!/bin/bash
echo "=== Health ==="
curl -s http://localhost:8001/health
echo ""
echo "=== Test Embed ==="
curl -s -X POST http://localhost:8001/embed -H "Content-Type: application/json" -d '["混凝土强度不足"]'
echo ""
