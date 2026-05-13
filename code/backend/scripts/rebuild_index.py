"""
重建知识索引脚本
用于重新解析和索引状态为 pending 的知识
"""
import os
import tempfile
from app.database import get_db
from app.models.knowledge import Knowledge
from app.services.minio_service import minio_service
from app.services.parser_service import parser_service
from app.services.search_service import search_service


def rebuild_knowledge_index(knowledge_id: str) -> dict:
    """重建单个知识的索引"""
    db = next(get_db())

    knowledge = db.query(Knowledge).filter(Knowledge.id == knowledge_id).first()
    if not knowledge:
        return {"error": "Knowledge not found"}

    print(f"\nProcessing: {knowledge.title}")
    print(f"  File path: {knowledge.file_path}")
    print(f"  File type: {knowledge.file_type}")

    if not knowledge.file_path:
        return {"error": "No file path"}

    # 下载文件
    try:
        file_data = minio_service.download_file(knowledge.file_path)
        print(f"  File size: {len(file_data)} bytes")
    except Exception as e:
        return {"error": f"Download failed: {e}"}

    # 确定文件类型和扩展名
    ext = f".{knowledge.file_type}"

    # 解析文件
    parsed_content = ""
    parsed_summary = ""
    status = "active"

    with tempfile.NamedTemporaryFile(delete=False, suffix=ext) as tmp_file:
        tmp_file.write(file_data)
        tmp_path = tmp_file.name

    try:
        parsed = parser_service.parse(tmp_path, knowledge.file_type)
        parsed_content = parsed.content
        parsed_summary = parsed.summary[:500] if parsed.summary else ""
        print(f"  Parsed content length: {len(parsed_content)}")
    except Exception as e:
        status = "parse_failed"
        print(f"  Parse error: {e}")
    finally:
        os.unlink(tmp_path)

    # 更新状态
    es_status = "indexed" if status == "active" and parsed_content else "pending"
    vector_status = "done" if status == "active" and parsed_content else "pending"

    knowledge.status = status
    knowledge.es_indexed = es_status
    knowledge.vector_indexed = vector_status

    # 更新 ES 索引
    if parsed_content:
        try:
            # 先删除旧索引
            search_service.delete_knowledge_index(knowledge_id)

            # 重建索引
            search_service.index_knowledge(
                knowledge_id=knowledge_id,
                title=knowledge.title,
                content=parsed_content,
                summary=parsed_summary,
                category=knowledge.category,
                source=knowledge.source or "",
                tags=knowledge.tags or [],
                user_id=knowledge.user_id,
                created_at=str(knowledge.created_at),
                view_count=knowledge.view_count
            )

            # 重建向量索引
            search_service.index_vector(
                knowledge_id=knowledge_id,
                title=knowledge.title,
                content=parsed_content,
                category=knowledge.category,
                user_id=knowledge.user_id
            )

            print(f"  ES indexed: {es_status}")
            print(f"  Vector indexed: {vector_status}")
        except Exception as e:
            print(f"  Index error: {e}")

    db.commit()

    return {
        "id": knowledge_id,
        "status": status,
        "es_indexed": es_status,
        "vector_indexed": vector_status,
        "content_length": len(parsed_content)
    }


def rebuild_all_pending():
    """重建所有 pending 状态的知识"""
    db = next(get_db())

    # 找出所有 pending 的知识
    pending = db.query(Knowledge).filter(
        (Knowledge.es_indexed == "pending") | (Knowledge.vector_indexed == "pending")
    ).all()

    print(f"Found {len(pending)} knowledge items with pending status")

    results = []
    for k in pending:
        result = rebuild_knowledge_index(k.id)
        results.append(result)

    # 统计
    success = sum(1 for r in results if r.get("content_length", 0) > 0)
    failed = len(results) - success

    print(f"\n=== Summary ===")
    print(f"Total: {len(results)}")
    print(f"Success: {success}")
    print(f"Failed: {failed}")

    return results


if __name__ == "__main__":
    print("=" * 50)
    print("Rebuild Knowledge Index")
    print("=" * 50)
    rebuild_all_pending()
    print("\nDone!")