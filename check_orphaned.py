# -*- coding: utf-8 -*-
from neo4j import GraphDatabase
from elasticsearch import Elasticsearch
from qdrant_client import QdrantClient

# Neo4j
uri = 'bolt://172.20.36.91:7687'
driver = GraphDatabase.driver(uri)
with driver.session() as session:
    result = session.run('''
        MATCH (n)
        WHERE NOT EXISTS(()-[:EXTRACTED_FROM]->(n))
        AND n.knowledge_id IS NULL
        RETURN count(n) as count, labels(n)[0] as label
    ''')
    print('=== Neo4j 孤立节点 ===')
    for r in result:
        print(f'  {r["label"]}: {r["count"]}')

    # 统计总节点
    total = session.run('MATCH (n) RETURN count(n) as count')
    print(f'\n总节点数: {total.single()["count"]}')

    # 检查有 knowledge_id 但关系不存在的
    orphan_by_kid = session.run('''
        MATCH (n)
        WHERE n.knowledge_id IS NOT NULL
        AND NOT EXISTS(()-[:EXTRACTED_FROM]->(n))
        RETURN count(n) as count
    ''')
    print(f'有 knowledge_id 但无关系的节点: {orphan_by_kid.single()["count"]}')

driver.close()

# ES
es = Elasticsearch(['http://172.20.36.91:9200'])
es_count = es.count(index='knowledge')['count']
print(f'\n=== ES 索引文档数 ===')
print(f'  {es_count}')

# Qdrant
qdrant = QdrantClient(url='http://172.20.36.91:6333')
try:
    collection = qdrant.get_collection('knowledge')
    print(f'\n=== Qdrant collection ===')
    print(f'  points: {collection.points_count}')
except Exception as e:
    print(f'Qdrant error: {e}')