# -*- coding: utf-8 -*-
from neo4j import GraphDatabase

driver = GraphDatabase.driver('bolt://172.20.36.91:7687')
with driver.session() as session:
    # 没有 EXTRACTED_FROM 关系的节点
    result = session.run('''
        MATCH (n)
        WHERE NOT EXISTS(()-[:EXTRACTED_FROM]->(n))
        RETURN count(n) as count, labels(n)[0] as label
        ORDER BY count DESC
    ''')
    print('=== 没有 EXTRACTED_FROM 关系的节点 ===')
    for r in result:
        print(f'  {r["label"]}: {r["count"]}')

    # 有 EXTRACTED_FROM 关系的节点
    result2 = session.run('''
        MATCH (n)
        WHERE EXISTS(()-[:EXTRACTED_FROM]->(n))
        RETURN count(n) as count, labels(n)[0] as label
    ''')
    print('\n=== 有 EXTRACTED_FROM 关系的节点 ===')
    for r in result2:
        print(f'  {r["label"]}: {r["count"]}')

    # 总节点数
    total = session.run('MATCH (n) RETURN count(n) as count').single()
    print(f'\n总节点数: {total["count"]}')

    # 关系总数
    rels = session.run('MATCH ()-[r]->() RETURN count(r) as count').single()
    print(f'总关系数: {rels["count"]}')

driver.close()