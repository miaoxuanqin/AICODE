# -*- coding: utf-8 -*-
"""
重新从 MySQL 索引知识到 ES
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'code', 'backend'))
os.chdir(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'code', 'backend'))

import pymysql
import json
import tempfile
import subprocess

def clean_for_json(text):
    """Remove or replace control characters that break ES JSON parsing"""
    if not text:
        return ''
    # Remove control chars 0x00-0x1f except tab(9), newline(10), cr(13)
    import re
    # Replace control chars with space, then collapse whitespace
    text = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f]', ' ', text)
    text = re.sub(r' +', ' ', text)
    return text.strip()

def reindex():
    # 连接 MySQL
    conn = pymysql.connect(
        host='172.20.36.91',
        user='myuser',
        password='1',
        database='mydatabase',
        charset='utf8mb4'
    )
    cursor = conn.cursor()

    # 获取所有知识
    cursor.execute('SELECT id, title, content, summary, category, source, tags, user_id, created_at FROM knowledge')
    rows = cursor.fetchall()
    print(f"找到 {len(rows)} 条知识")

    success = 0
    failed = 0

    for row in rows:
        kid, title, content, summary, category, source, tags_str, user_id, created_at = row

        # 跳过没有内容的
        if not content:
            print(f"  跳过 (无内容): {title[:30] if title else '无标题'}")
            continue

        # 解析 tags
        tags = []
        if tags_str:
            try:
                tags = json.loads(tags_str)
            except:
                tags = []

        # 构建 ES 文档 - 清理控制字符
        doc = {
            "id": kid,
            "title": clean_for_json(title or ''),
            "content": clean_for_json(content),
            "summary": clean_for_json(summary or ''),
            "category": category or 'tech',
            "source": source or '',
            "tags": tags,
            "user_id": user_id or '1',
            "created_at": str(created_at) if created_at else '',
            "view_count": 0
        }

        # 写入 ES
        with tempfile.NamedTemporaryFile(mode='wb', suffix='.json', delete=False) as f:
            json_bytes = json.dumps(doc, ensure_ascii=False).encode('utf-8')
            f.write(json_bytes)
            temp_file = f.name

        es_cmd = ['curl', '-s', '-X', 'PUT',
                   f'http://172.20.36.91:9200/knowledge/_doc/{kid}?refresh=true',
                   '-H', 'Content-Type: application/json',
                   '-d', f'@{temp_file}']

        result = subprocess.run(es_cmd, capture_output=True, text=True)
        import os
        os.unlink(temp_file)

        if '"result":"updated"' in result.stdout or '"result":"created"' in result.stdout:
            print(f"  OK: {(title or '无标题')[:40]}")
            success += 1
        else:
            print(f"  FAIL: {(title or '无标题')[:40]} - {result.stdout[:100]}")
            failed += 1

    cursor.close()
    conn.close()

    print(f"\n完成: 成功 {success}, 失败 {failed}")

if __name__ == '__main__':
    reindex()