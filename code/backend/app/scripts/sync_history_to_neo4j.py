"""
批量同步历史知识到 Neo4j

使用方法:
    cd code/backend
    python -m app.scripts.sync_history_to_neo4j

功能:
    - 从 MySQL 获取所有知识
    - 从 ES 获取完整内容
    - 调用 GraphExtractor 抽取实体关系
    - 写入 Neo4j
"""
import asyncio
import sys
import os

# 添加项目根目录到 path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))


async def sync_single_knowledge(extractor, knowledge_id: str, content: str, batch_num: int):
    """同步单条知识到 Neo4j"""
    try:
        stats = await extractor.async_sync_to_neo4j(knowledge_id, content)
        print(f"[Batch {batch_num}] {knowledge_id}: "
              f"entities={stats['entities_created']}, relations={stats['relations_created']}")
        return True, stats
    except Exception as e:
        print(f"[Batch {batch_num}] {knowledge_id}: FAILED - {e}")
        return False, None


async def main():
    """主函数"""
    print("=" * 60)
    print("历史知识批量同步到 Neo4j")
    print("=" * 60)

    # 导入依赖
    from app.config import get_settings
    from app.database import get_db
    from app.models.knowledge import Knowledge
    from app.services.search_service import search_service
    from app.services.graph_extractor import get_graph_extractor

    settings = get_settings()

    # 检查 Neo4j 连接
    try:
        from app.services.neo4j_service import get_neo4j_service
        neo4j = get_neo4j_service()
        if not neo4j.verify_connectivity():
            print("ERROR: Neo4j 连接不可用，请检查配置")
            return
        print(f"Neo4j 连接正常: {settings.neo4j_uri}")
    except Exception as e:
        print(f"ERROR: Neo4j 连接失败 - {e}")
        return

    # 获取 Graph Extractor
    extractor = get_graph_extractor()
    print("Graph Extractor 初始化完成")

    # 从数据库获取所有知识
    db_gen = get_db()
    db = next(db_gen)

    try:
        all_knowledge = db.query(Knowledge).filter(
            Knowledge.status == "active"
        ).all()

        print(f"\n找到 {len(all_knowledge)} 条知识需要同步")

        # 统计
        success_count = 0
        failed_count = 0
        skip_count = 0
        total_entities = 0
        total_relations = 0

        # 批量处理
        batch_size = 5  # 每批处理数量
        for i in range(0, len(all_knowledge), batch_size):
            batch = all_knowledge[i:i + batch_size]
            batch_num = i // batch_size + 1

            tasks = []
            for k in batch:
                # 从 ES 获取完整内容
                try:
                    es_doc = search_service.get_by_id(k.id)
                    content = es_doc.get("content", "") if es_doc else ""
                except Exception:
                    content = ""

                if not content:
                    print(f"[Batch {batch_num}] {k.id} ({k.title}): SKIP - 无内容")
                    skip_count += 1
                    continue

                tasks.append(sync_single_knowledge(extractor, k.id, content, batch_num))

            # 并发执行
            if tasks:
                results = await asyncio.gather(*tasks, return_exceptions=True)

                for result in results:
                    if isinstance(result, Exception):
                        failed_count += 1
                    elif result[0]:
                        success_count += 1
                        total_entities += result[1].get('entities_created', 0)
                        total_relations += result[1].get('relations_created', 0)

            # 避免请求过快
            if i + batch_size < len(all_knowledge):
                await asyncio.sleep(0.5)

    finally:
        db.close()

    # 打印统计
    print("\n" + "=" * 60)
    print("同步完成")
    print("=" * 60)
    print(f"成功: {success_count}")
    print(f"失败: {failed_count}")
    print(f"跳过: {skip_count}")
    print(f"总实体数: {total_entities}")
    print(f"总关系数: {total_relations}")

    # 打印 Neo4j 统计
    try:
        stats = neo4j.get_stats()
        print("\nNeo4j 图谱统计:")
        for key, value in stats.items():
            print(f"  {key}: {value}")
    except Exception:
        pass


if __name__ == "__main__":
    asyncio.run(main())
