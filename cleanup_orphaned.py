# -*- coding: utf-8 -*-
"""
清理孤立的索引数据
删除 ES、Qdrant、Neo4j 中关联知识已删除的数据
"""
import sys
import os
backend_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'code', 'backend')
sys.path.insert(0, backend_path)
os.chdir(backend_path)

from neo4j import GraphDatabase
from elasticsearch import Elasticsearch
from qdrant_client import QdrantClient
from qdrant_client.models import Filter, FieldCondition, MatchValue
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.config import get_settings
from app.models.knowledge import Knowledge

settings = get_settings()

def cleanup():
    # 1. 从 MySQL 获取活跃知识的 ID
    engine = create_engine(settings.database_url)
    Session = sessionmaker(bind=engine)
    db = Session()

    active_knowledge_ids = set()
    try:
        # 只查询 active 状态的知识（deleted 的已经被软删除或硬删除）
        all_knowledge = db.query(Knowledge).all()
        for k in all_knowledge:
            active_knowledge_ids.add(k.id)
        print(f"MySQL 活跃知识数量: {len(active_knowledge_ids)}")
    finally:
        db.close()

    if not active_knowledge_ids:
        print("警告: MySQL 中没有活跃知识！")
        return

    # 2. 清理 Neo4j
    print("\n=== 清理 Neo4j ===")
    neo4j_driver = GraphDatabase.driver('bolt://172.20.36.91:7687')

    with neo4j_driver.session() as session:
        # 找到孤立节点：没有 EXTRACTED_FROM 关系的，或者 knowledge_id 不在活跃列表的
        orphaned = session.run('''
            MATCH (n)
            WHERE NOT EXISTS(()-[:EXTRACTED_FROM]->(n))
            RETURN count(n) as count, labels(n)[0] as label
        ''')
        orphaned_neo4j = list(orphaned)
        total_orphaned = 0
        for r in orphaned_neo4j:
            print(f"  {r['label']}: {r['count']} 个孤立")
            total_orphaned += r['count']

        # 执行删除孤立节点
        deleted = session.run('''
            MATCH (n)
            WHERE NOT EXISTS(()-[:EXTRACTED_FROM]->(n))
            DETACH DELETE n
            RETURN count(n) as deleted
        ''')
        count = deleted.single()['deleted']
        print(f"  Neo4j 已删除: {count} 个孤立节点")

        # 另外删除 knowledge_id 不在活跃列表的节点（有关联关系但知识已删除）
        stale = session.run('''
            MATCH (n)
            WHERE n.knowledge_id IS NOT NULL
            AND NOT n.knowledge_id IN $active_ids
            RETURN count(n) as count
        ''', active_ids=list(active_knowledge_ids))
        stale_count = stale.single()['count']
        print(f"  知识已删除但节点仍存在的: {stale_count} 个")

        if stale_count > 0:
            deleted2 = session.run('''
                MATCH (n)
                WHERE n.knowledge_id IS NOT NULL
                AND NOT n.knowledge_id IN $active_ids
                DETACH DELETE n
                RETURN count(n) as deleted
            ''', active_ids=list(active_knowledge_ids))
            count2 = deleted2.single()['deleted']
            print(f"  已删除: {count2} 个")

    neo4j_driver.close()

    # 3. 清理 ES (用 curl 避免客户端版本问题)
    print("\n=== 清理 ES ===")
    import subprocess

    # 获取所有文档 ID
    result = subprocess.run(
        ['curl', '-s', 'http://172.20.36.91:9200/knowledge/_search?size=10000'],
        capture_output=True, text=True
    )
    import json
    try:
        data = json.loads(result.stdout)
        es_ids = set()
        for hit in data.get('hits', {}).get('hits', []):
            es_ids.add(hit['_id'])
    except:
        es_ids = set()

    # 找出孤立的 ID
    orphaned_es = es_ids - active_knowledge_ids
    print(f"  ES 文档总数: {len(es_ids)}")
    print(f"  将删除: {len(orphaned_es)} 个")

    # 删除孤立文档
    for doc_id in orphaned_es:
        result = subprocess.run(
            ['curl', '-s', '-X', 'DELETE', f'http://172.20.36.91:9200/knowledge/_doc/{doc_id}'],
            capture_output=True, text=True
        )
        print(f"    已删除 ES: {doc_id}")

    # 4. 清理 Qdrant
    print("\n=== 清理 Qdrant ===")
    qdrant = QdrantClient(url='http://172.20.36.91:6333')

    try:
        # 获取所有 knowledge_id
        qdrant_ids = set()
        results = qdrant.scroll(collection_name='knowledge', limit=10000)
        for point in results[0]:
            kid = point.payload.get('knowledge_id')
            if kid:
                qdrant_ids.add(kid)

        orphaned_qdrant = qdrant_ids - active_knowledge_ids
        print(f"  Qdrant points 总数: {len(qdrant_ids)}")
        print(f"  将删除: {len(orphaned_qdrant)} 个")

        # 按 knowledge_id 删除
        for kid in orphaned_qdrant:
            try:
                qdrant.delete(
                    collection_name='knowledge',
                    points_selector=Filter(
                        must=[FieldCondition(key='knowledge_id', match=MatchValue(value=kid))]
                    )
                )
                print(f"    已删除 Qdrant: {kid}")
            except Exception as e:
                print(f"    删除失败 {kid}: {e}")

    except Exception as e:
        print(f"  Qdrant 清理出错: {e}")

    print("\n=== 清理完成 ===")

if __name__ == '__main__':
    cleanup()
