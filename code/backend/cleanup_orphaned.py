"""
清理孤立数据：
1. ES 中已删除知识但索引仍存在的文档
2. MinIO 中已删除知识但文件仍存在的文件

运行方式：python cleanup_orphaned.py
"""
from app.database import SessionLocal
from app.models.knowledge import Knowledge
from app.services.search_service import search_service
from app.services.minio_service import minio_service


def cleanup_es():
    """清理 ES 中孤立文档"""
    db = SessionLocal()
    try:
        # 获取 MySQL 中所有知识 ID
        mysql_ids = set(row[0] for row in db.query(Knowledge.id).all())
        print(f"MySQL 知识数量: {len(mysql_ids)}")

        # 获取 ES 中所有文档 ID（需要scroll全部拉取）
        from elasticsearch import Elasticsearch
        from app.config import get_settings
        settings = get_settings()
        es = Elasticsearch([settings.elasticsearch_url])

        es_ids = set()
        if es.indices.exists(index=search_service.INDEX_NAME):
            # 使用 scroll API 遍历所有文档
            result = es.search(
                index=search_service.INDEX_NAME,
                body={"query": {"match_all": {}}, "size": 1000},
                scroll='2m'
            )
            scroll_id = result.get('_scroll_id')
            hits = result['hits']['hits']

            while hits:
                for hit in hits:
                    es_ids.add(hit['_source'].get('id') or hit['_id'])
                result = es.scroll(scroll_id=scroll_id, scroll='2m')
                scroll_id = result.get('_scroll_id')
                hits = result['hits']['hits']

            if scroll_id:
                try:
                    es.clear_scroll(scroll_id=scroll_id)
                except Exception:
                    pass

        print(f"ES 索引知识数量: {len(es_ids)}")

        # 找出孤立 ID（ES里有但MySQL没有）
        orphaned_ids = es_ids - mysql_ids
        print(f"ES 孤立文档数量: {len(orphaned_ids)}")

        if orphaned_ids:
            for oid in orphaned_ids:
                try:
                    search_service.delete_knowledge_index(oid)
                    print(f"  删除 ES 文档: {oid}")
                except Exception as e:
                    print(f"  删除失败 {oid}: {e}")
            print(f"ES 清理完成")
        else:
            print("ES 无需清理")

    finally:
        db.close()


def cleanup_minio():
    """清理 MinIO 中孤立文件"""
    db = SessionLocal()
    try:
        # 获取 MySQL 中所有文件的 file_path
        mysql_paths = set()
        for row in db.query(Knowledge.file_path).filter(Knowledge.file_path.isnot(None)).all():
            if row[0]:
                mysql_paths.add(row[0])
        print(f"MySQL 知识文件数: {len(mysql_paths)}")

        # 列出 MinIO 中所有文件
        try:
            minio_files = minio_service.list_files()
            minio_paths = set(minio_files)
            print(f"MinIO 文件数: {len(minio_paths)}")
        except Exception as e:
            print(f"列出 MinIO 文件失败: {e}")
            return

        # 找出孤立文件
        orphaned_paths = minio_paths - mysql_paths
        print(f"MinIO 孤立文件数: {len(orphaned_paths)}")

        if orphaned_paths:
            for path in orphaned_paths:
                try:
                    minio_service.delete_file(path)
                    print(f"  删除 MinIO 文件: {path}")
                except Exception as e:
                    print(f"  删除失败 {path}: {e}")
            print(f"MinIO 清理完成")
        else:
            print("MinIO 无需清理")

    finally:
        db.close()


if __name__ == "__main__":
    print("=" * 40)
    print("开始清理孤立数据...")
    print("=" * 40)

    print("\n>>> 清理 ES 孤立文档")
    cleanup_es()

    print("\n>>> 清理 MinIO 孤立文件")
    cleanup_minio()

    print("\n" + "=" * 40)
    print("清理完成")
    print("=" * 40)
