"""
批量重建向量索引脚本
用于对已有知识建立 Qdrant 向量索引

用法:
    cd code/backend
    python -m app.scripts.rebuild_vector_index

参数:
    --recreate   删除旧 collection 并重新创建（当维度不匹配时使用）
"""
import sys
import os

# 添加 backend 目录到 path
backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, backend_dir)

from app.database import SessionLocal
from app.models.knowledge import Knowledge
from app.services.search_service import search_service
from app.services.embedding_service import embedding_service


def recreate_collection():
    """删除并重建 Qdrant collection（解决维度不匹配问题）"""
    from qdrant_client import QdrantClient
    from qdrant_client.models import Distance, VectorParams
    from app.config import get_settings

    settings = get_settings()
    client = QdrantClient(url=settings.qdrant_url)
    collection_name = "knowledge"
    vector_size = 768  # text2vec-base-chinese

    try:
        # 删除旧 collection
        client.delete_collection(collection_name=collection_name)
        print(f"已删除旧 collection: {collection_name}")
    except Exception as e:
        print(f"删除旧 collection 失败（可能不存在）: {e}")

    # 创建新 collection
    client.create_collection(
        collection_name=collection_name,
        vectors_config=VectorParams(size=vector_size, distance=Distance.COSINE)
    )
    print(f"已创建新 collection: {collection_name} (dim={vector_size})")


def rebuild_vector_index(batch_size: int = 50, recreate: bool = False):
    """批量重建向量索引"""
    # 如果需要，重建 collection
    if recreate:
        recreate_collection()

    db = SessionLocal()
    try:
        # 获取所有知识
        total = db.query(Knowledge).count()
        print(f"共 {total} 条知识需要建立向量索引")

        if total == 0:
            print("没有知识需要索引")
            return

        # 检查 Embedding 服务
        if not embedding_service.is_available():
            print("警告: Embedding 服务不可用，将使用 minimax 模式")

        success_count = 0
        fail_count = 0
        skip_count = 0

        offset = 0
        while offset < total:
            knowledge_list = db.query(Knowledge).offset(offset).limit(batch_size).all()

            for k in knowledge_list:
                try:
                    # 从 ES 获取完整内容
                    es_doc = search_service.get_by_id(k.id)

                    if not es_doc:
                        print(f"  [跳过] 知识 {k.id} ({k.title}) 在 ES 中不存在")
                        skip_count += 1
                        continue

                    content = es_doc.get("content", "")
                    if not content:
                        print(f"  [跳过] 知识 {k.id} ({k.title}) 内容为空")
                        skip_count += 1
                        continue

                    # 建立向量索引
                    search_service.index_vector(
                        knowledge_id=k.id,
                        title=k.title,
                        content=content,
                        category=k.category,
                        user_id=k.user_id
                    )

                    print(f"  [成功] {k.id} ({k.title})")
                    success_count += 1

                except Exception as e:
                    print(f"  [失败] {k.id} ({k.title}): {e}")
                    fail_count += 1

            offset += batch_size
            print(f"进度: {min(offset, total)}/{total}")

        print(f"\n完成!")
        print(f"  成功: {success_count}")
        print(f"  失败: {fail_count}")
        print(f"  跳过: {skip_count}")

    finally:
        db.close()


if __name__ == "__main__":
    print("=" * 50)
    print("批量重建向量索引脚本")
    print("=" * 50)

    recreate = "--recreate" in sys.argv
    if recreate:
        print("警告: 将删除并重建 Qdrant collection！")
        confirm = input("确认继续? (y/n): ")
        if confirm.lower() != 'y':
            print("已取消")
            sys.exit(0)

    rebuild_vector_index(recreate=recreate)