# -*- coding: utf-8 -*-
import sys
import os
backend_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'code', 'backend')
sys.path.insert(0, backend_path)
os.chdir(backend_path)

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from app.config import get_settings

settings = get_settings()
engine = create_engine(settings.database_url)
Session = sessionmaker(bind=engine)
db = Session()

# 检查 content 字段是否有乱码
result = db.execute(text("SELECT id, title, LEFT(content, 100) as content_preview FROM knowledge WHERE content IS NOT NULL AND content != '' LIMIT 5"))

print("=== MySQL 知识内容检查 ===")
for row in result:
    print(f"ID: {row.id}")
    print(f"Title: {row.title}")
    print(f"Content preview: {row.content_preview[:80]}...")
    print()

db.close()