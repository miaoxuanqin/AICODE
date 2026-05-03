"""
批量同步知识状态脚本
用于将 ES/Neo4j 中已有的索引状态同步到数据库
"""
import sys
sys.path.insert(0, '.')

from app.database import SessionLocal
from app.models.knowledge import Knowledge
from app.services.search_service import search_service
from app.services.neo4j_service import get_neo4j_service

def sync_es_status(db):
    """同步 ES 索引状态"""
    all_knowledge = db.query(Knowledge).all()
    synced = 0

    for k in all_knowledge:
        if k.content:  # 有内容才有可能是已索引
            doc = search_service.get_by_id(k.id)
            if doc:
                k.es_indexed = "indexed"
                k.vector_indexed = "done"  # ES索引成功说明向量也应该成功
                synced += 1

    db.commit()
    return synced

def sync_neo4j_status(db):
    """同步 Neo4j 图谱状态"""
    neo4j = get_neo4j_service()

    try:
        with neo4j.driver.session() as session:
            # 获取所有有 knowledge_id 的节点
            result = session.run("""
                MATCH (n) WHERE n.knowledge_id IS NOT NULL
                RETURN DISTINCT n.knowledge_id as knowledge_id
            """)
            knowledge_ids = [record["knowledge_id"] for record in result]

        # 更新数据库中这些 knowledge_id 的图谱状态为 done
        updated = 0
        for kid in knowledge_ids:
            k = db.query(Knowledge).filter(Knowledge.id == kid).first()
            if k and k.graph_indexed != "done":
                k.graph_indexed = "done"
                updated += 1

        db.commit()
        return updated
    except Exception as e:
        print(f"Neo4j 状态同步失败: {e}")
        db.rollback()
        return 0

if __name__ == "__main__":
    db = SessionLocal()
    try:
        es_count = sync_es_status(db)
        print(f"已同步 {es_count} 条知识的 ES/向量状态")

        graph_count = sync_neo4j_status(db)
        print(f"已同步 {graph_count} 条知识的图谱状态")
    finally:
        db.close()