"""
清理 Neo4j 中已删除知识的残留数据

遍历 Neo4j 中所有通过 EXTRACTED_FROM 关系关联的 knowledge_id，
如果该 knowledge_id 在 MySQL 中不存在，则强制删除其关联的实体。
"""
from app.database import get_db
from app.models.knowledge import Knowledge
from app.services.neo4j_service import get_neo4j_service


def cleanup_orphaned_knowledge():
    """清理孤立的知识实体"""
    db = next(get_db())
    neo4j = get_neo4j_service()

    # 获取 MySQL 中所有 knowledge IDs
    mysql_ids = set()
    knowledges = db.query(Knowledge.id).all()
    for k in knowledges:
        mysql_ids.add(k.id)
    print(f"MySQL knowledge count: {len(mysql_ids)}")

    # 获取 Neo4j 中所有有 EXTRACTED_FROM 关系的 unique knowledge_id
    with neo4j.driver.session() as session:
        result = session.run("""
        MATCH ()-[r:EXTRACTED_FROM]->(k)
        RETURN DISTINCT k.knowledge_id as kid
        """)
        neo4j_kids = set(r['kid'] for r in result)

    print(f"Neo4j knowledge_ids with EXTRACTED_FROM: {len(neo4j_kids)}")

    # 找出孤立的 knowledge_ids（Neo4j 有但 MySQL 没有）
    orphaned = neo4j_kids - mysql_ids
    print(f"Orphaned knowledge_ids (in Neo4j but not in MySQL): {len(orphaned)}")

    if not orphaned:
        print("No orphaned data found. Nothing to clean.")
        return

    # 删除每个孤立 knowledge 的关联实体
    total_deleted = 0
    total_relations = 0

    for kid in orphaned:
        print(f"\nProcessing orphaned kid: {kid}")
        stats = neo4j.force_delete_knowledge_reference(kid)
        print(f"  entities_checked: {stats['entities_checked']}")
        print(f"  entities_deleted: {stats['entities_deleted']}")
        print(f"  relations_deleted: {stats['relations_deleted']}")
        total_deleted += stats['entities_deleted']
        total_relations += stats['relations_deleted']

    print(f"\n=== Cleanup Summary ===")
    print(f"Total orphaned kids cleaned: {len(orphaned)}")
    print(f"Total entities deleted: {total_deleted}")
    print(f"Total relations deleted: {total_relations}")

    # 验证清理结果
    with neo4j.driver.session() as session:
        result = session.run("MATCH ()-[r:EXTRACTED_FROM]->(k) RETURN count(r) as cnt")
        remaining = result.single()['cnt']
        print(f"Remaining EXTRACTED_FROM relations: {remaining}")


if __name__ == "__main__":
    print("=" * 50)
    print("Neo4j Orphaned Knowledge Cleanup")
    print("=" * 50)
    cleanup_orphaned_knowledge()
    print("\nCleanup completed!")