# -*- coding: utf-8 -*-
from neo4j import GraphDatabase

driver = GraphDatabase.driver('bolt://172.20.36.91:7687')
with driver.session() as session:
    # 删除所有没有 EXTRACTED_FROM 关系的节点
    result = session.run('''
        MATCH (n)
        WHERE NOT EXISTS(()-[:EXTRACTED_FROM]->(n))
        DETACH DELETE n
        RETURN count(n) as deleted
    ''')
    count = result.single()['deleted']
    print(f'Deleted: {count} nodes')

    # 验证
    total = session.run('MATCH (n) RETURN count(n) as count').single()
    print(f'Remaining nodes: {total["count"]}')

    rels = session.run('MATCH ()-[r]->() RETURN count(r) as count').single()
    print(f'Remaining relationships: {rels["count"]}')
driver.close()
print('Done!')