import os
import re
import uuid
import asyncio
import tempfile
import redis
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, Query, Path
from sqlalchemy.orm import Session
from typing import Optional

from app.config import get_settings
from app.database import get_db
from app.models.user import User
from app.models.knowledge import Knowledge, UserFavorite, KnowledgeComment
from app.schemas.knowledge import (
    KnowledgeUploadResponse, KnowledgeItem, KnowledgeDetail,
    KnowledgeListResponse, KnowledgeUpdate, KnowledgeCreate, SearchResponse,
    HotKnowledgeItem, LatestKnowledgeItem, CommentCreate, CommentItem,
    KnowledgeStatsResponse
)
from app.services.parser_service import parser_service
from app.services.minio_service import minio_service
from app.services.search_service import search_service
from core.rbac import get_current_user

# Neo4j 导入（可选）
try:
    from app.services.graph_extractor import get_graph_extractor
    GRAPH_EXTRACTOR_AVAILABLE = True
except ImportError:
    GRAPH_EXTRACTOR_AVAILABLE = False
    get_graph_extractor = None

router = APIRouter(prefix="/knowledge", tags=["知识管理"])

settings = get_settings()
redis_client = redis.from_url(settings.redis_url, decode_responses=True)
HOT_TERMS_KEY = "search:hot_terms"


def _sync_knowledge_to_neo4j(knowledge_id: str, content: str):
    """
    异步同步知识到 Neo4j（后台执行，不阻塞主流程）

    Args:
        knowledge_id: 知识ID
        content: 知识内容
    """
    if not GRAPH_EXTRACTOR_AVAILABLE or not content:
        return

    try:
        # 创建独立的数据库会话（异步线程需要自己的会话）
        from app.database import SessionLocal
        db = SessionLocal()

        extractor = get_graph_extractor()
        stats = extractor.sync_to_neo4j(knowledge_id, content)

        # 更新数据库中的图谱状态
        knowledge = db.query(Knowledge).filter(Knowledge.id == knowledge_id).first()
        if knowledge:
            if stats['entities_created'] > 0 or stats['relations_created'] > 0:
                knowledge.graph_indexed = "done"
            else:
                knowledge.graph_indexed = "failed"
            db.commit()

        print(f"Neo4j 同步完成: knowledge_id={knowledge_id}, "
              f"entities={stats['entities_created']}, relations={stats['relations_created']}")
    except Exception as e:
        print(f"Neo4j 同步失败: {e}")
        # 更新状态为失败
        try:
            from app.database import SessionLocal
            db = SessionLocal()
            knowledge = db.query(Knowledge).filter(Knowledge.id == knowledge_id).first()
            if knowledge:
                knowledge.graph_indexed = "failed"
                db.commit()
        except Exception:
            pass
    finally:
        if 'db' in dir():
            db.close()


CATEGORY_NAMES = {
    "law": "法律法规",
    "tech": "技术标准",
    "case": "执法案例",
    "policy": "政策文件"
}

ALLOWED_EXTENSIONS = {".pdf", ".docx", ".doc"}
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB


def get_category_name(category: str) -> str:
    return CATEGORY_NAMES.get(category, category)


@router.post("/upload", response_model=KnowledgeUploadResponse)
async def upload_knowledge(
    file: UploadFile = File(...),
    title: Optional[str] = Form(None),
    category: str = Form(...),
    source: Optional[str] = Form(None),
    tags: Optional[str] = Form(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """上传知识文件并解析"""
    # 验证文件类型
    if not file.filename:
        raise HTTPException(status_code=400, detail="文件名不能为空")

    ext = os.path.splitext(file.filename)[-1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"不支持的文件格式，仅支持: {', '.join(ALLOWED_EXTENSIONS)}"
        )

    # 读取文件数据
    file_data = await file.read()
    file_size = len(file_data)

    if file_size > MAX_FILE_SIZE:
        raise HTTPException(status_code=413, detail="文件大小超过限制（最大50MB）")

    # 确定文件类型
    file_type = ext[1:]  # 去掉点

    # 上传到 MinIO
    try:
        file_path = minio_service.upload_file(
            file_data=file_data,
            file_name=file.filename,
            content_type=file.content_type or "application/octet-stream",
            user_id=str(current_user.id)
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"文件上传失败: {str(e)}")

    # 保存知识记录
    knowledge_id = str(uuid.uuid4())
    status = "active"

    # 解析文件获取标题、摘要和完整内容
    parsed_content = ""
    parsed_summary = ""
    with tempfile.NamedTemporaryFile(delete=False, suffix=ext) as tmp_file:
        tmp_file.write(file_data)
        tmp_path = tmp_file.name

    try:
        parsed = parser_service.parse(tmp_path, file_type)
        parsed_title = title or parsed.title
        parsed_content = parsed.content  # 完整内容，用于ES索引
        parsed_summary = parsed.summary[:500] if parsed.summary else ""
    except Exception as e:
        status = "parse_failed"
        parsed_title = title or file.filename
        parsed_content = ""
        parsed_summary = ""
    finally:
        os.unlink(tmp_path)

    # 处理标签
    tag_list = []
    if tags:
        tag_list = [t.strip() for t in tags.split(",") if t.strip()]

    # 创建知识记录（content不存MySQL，只存ES）
    # 设置初始索引状态
    es_status = "indexed" if status == "active" and parsed_content else "pending"
    vector_status = "done" if status == "active" and parsed_content else "pending"
    graph_status = "pending"  # 图谱异步处理，初始为pending

    knowledge = Knowledge(
        id=knowledge_id,
        title=parsed_title,
        summary=parsed_summary,
        category=category,
        source=source,
        tags=tag_list,
        user_id=str(current_user.id),
        file_path=file_path,
        file_type=file_type,
        status=status,
        view_count=0,
        favorite_count=0,
        es_indexed=es_status,
        vector_indexed=vector_status,
        graph_indexed=graph_status
    )
    db.add(knowledge)
    db.commit()

    # 建立搜索索引（ES存content + Qdrant存向量）
    if status == "active" and parsed_content:
        try:
            search_service.index_knowledge(
                knowledge_id=knowledge_id,
                title=parsed_title,
                content=parsed_content,
                summary=parsed_summary,
                category=category,
                source=source or "",
                tags=tag_list,
                user_id=str(current_user.id),
                created_at=str(knowledge.created_at),
                view_count=0
            )
            # 同步建立向量索引（Qdrant）
            search_service.index_vector(
                knowledge_id=knowledge_id,
                title=parsed_title,
                content=parsed_content,
                category=category,
                user_id=str(current_user.id)
            )

            # 异步同步到 Neo4j（图谱抽取，不阻塞主流程）
            if parsed_content:
                asyncio.create_task(
                    asyncio.to_thread(_sync_knowledge_to_neo4j, knowledge_id, parsed_content)
                )
        except Exception as e:
            print(f"索引失败: {e}")
            pass  # 索引失败不影响主流程

    return KnowledgeUploadResponse(
        id=knowledge_id,
        title=parsed_title,
        category=category,
        file_type=file_type,
        status=status
    )


@router.post("/manual", response_model=KnowledgeUploadResponse)
async def create_knowledge_manual(
    knowledge_data: KnowledgeCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """手动创建知识（富文本内容）"""
    knowledge_id = str(uuid.uuid4())

    # 处理摘要
    summary = knowledge_data.summary or ""
    if not summary and knowledge_data.content:
        plain_text = re.sub(r'<[^>]+>', '', knowledge_data.content)  # 去除HTML标签
        summary = plain_text[:500]

    # 处理标签
    tag_list = knowledge_data.tags or []

    # 创建知识记录
    knowledge = Knowledge(
        id=knowledge_id,
        title=knowledge_data.title,
        summary=summary,
        content=None,  # 不存MySQL，只存ES
        category=knowledge_data.category,
        source=knowledge_data.source,
        tags=tag_list,
        user_id=str(current_user.id),
        status="active",
        view_count=0,
        favorite_count=0,
        file_type="html",
        es_indexed="indexed",
        vector_indexed="done",
        graph_indexed="pending"
    )
    db.add(knowledge)
    db.commit()

    # 建立搜索索引（ES存完整content + Qdrant存向量）
    try:
        search_service.index_knowledge(
            knowledge_id=knowledge_id,
            title=knowledge_data.title,
            content=knowledge_data.content,
            summary=summary,
            category=knowledge_data.category,
            source=knowledge_data.source or "",
            tags=tag_list,
            user_id=str(current_user.id),
            created_at=str(knowledge.created_at),
            view_count=0
        )
        # 同步建立向量索引（Qdrant）
        search_service.index_vector(
            knowledge_id=knowledge_id,
            title=knowledge_data.title,
            content=knowledge_data.content,
            category=knowledge_data.category,
            user_id=str(current_user.id)
        )

        # 异步同步到 Neo4j（图谱抽取，不阻塞主流程）
        if knowledge_data.content:
            asyncio.create_task(
                asyncio.to_thread(_sync_knowledge_to_neo4j, knowledge_id, knowledge_data.content)
            )
    except Exception as e:
        print(f"索引失败: {e}")
        pass  # 索引失败不影响主流程

    return KnowledgeUploadResponse(
        id=knowledge_id,
        title=knowledge_data.title,
        category=knowledge_data.category,
        file_type="html",
        status="active"
    )


@router.get("", response_model=KnowledgeListResponse)
def list_knowledge(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    category: Optional[str] = Query(None, description="分类ID"),
    keyword: Optional[str] = Query(None),
    type: Optional[str] = Query(None, description="文件类型: pdf, doc, text"),
    es_indexed: Optional[str] = Query(None, description="全文检索状态: indexed, pending, failed"),
    vector_indexed: Optional[str] = Query(None, description="语义搜索状态: done, pending, failed"),
    graph_indexed: Optional[str] = Query(None, description="知识图谱状态: done, pending, failed, none"),
    sort: Optional[str] = Query("created_at desc"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取知识列表"""
    is_admin = current_user.is_superuser == 1

    if is_admin:
        query = db.query(Knowledge)
    else:
        query = db.query(Knowledge).filter(Knowledge.user_id == str(current_user.id))

    if category:
        query = query.filter(Knowledge.category == category)

    if keyword:
        query = query.filter(Knowledge.title.contains(keyword))

    if type:
        query = query.filter(Knowledge.file_type == type)

    if es_indexed:
        query = query.filter(Knowledge.es_indexed == es_indexed)

    if vector_indexed:
        query = query.filter(Knowledge.vector_indexed == vector_indexed)

    if graph_indexed:
        query = query.filter(Knowledge.graph_indexed == graph_indexed)

    # 排序
    if sort == "view_count desc":
        query = query.order_by(Knowledge.view_count.desc())
    else:
        query = query.order_by(Knowledge.created_at.desc())

    total = query.count()
    items = query.offset((page - 1) * page_size).limit(page_size).all()

    return KnowledgeListResponse(
        items=[
            KnowledgeItem(
                id=k.id,
                title=k.title,
                summary=k.summary,
                category=k.category,
                category_name=get_category_name(k.category),
                source=k.source,
                tags=k.tags or [],
                view_count=k.view_count,
                favorite_count=k.favorite_count,
                created_at=k.created_at,
                es_indexed=k.es_indexed or "pending",
                vector_indexed=k.vector_indexed or "pending",
                graph_indexed=k.graph_indexed or "pending",
                file_type=k.file_type,
                file_path=k.file_path
            )
            for k in items
        ],
        total=total,
        page=page,
        page_size=page_size
    )


@router.get("/search", response_model=SearchResponse)
def search_knowledge(
    q: str = Query(..., min_length=1),
    search_type: str = Query("keyword", pattern="^(keyword|vector|hybrid)$"),
    category: Optional[str] = Query(None, description="分类ID"),
    source: Optional[str] = Query(None),
    date_from: Optional[str] = Query(None),
    date_to: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    sort: str = Query("relevance"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """搜索知识"""
    user_id = str(current_user.id)
    is_admin = current_user.is_superuser == 1

    if search_type == "vector":
        # 向量搜索
        try:
            from app.services.embedding_service import embedding_service
            query_vector = embedding_service.encode_single(q)
            knowledge_ids = search_service.search_vector(
                query_vector=query_vector,
                user_id=user_id,
                category=category,
                limit=page_size,
                is_admin=is_admin
            )
            # 从 ES 获取详情
            items = []
            for kid in knowledge_ids:
                doc = search_service.get_by_id(kid)
                if doc:
                    items.append({
                        "id": doc["id"],
                        "title": doc["title"],
                        "summary": doc.get("summary", ""),
                        "category": doc.get("category", ""),
                        "source": doc.get("source", ""),
                        "tags": doc.get("tags", []),
                        "view_count": doc.get("view_count", 0),
                        "score": 0.9,
                        "highlight": {}
                    })
            result = {
                "items": items,
                "total": len(items),
                "page": 1,
                "page_size": page_size
            }
        except Exception as e:
            print(f"向量搜索失败，fallback到关键词搜索: {e}")
            result = search_service.search_keyword(
                query=q, user_id=user_id, category=category,
                page=page, page_size=page_size, is_admin=is_admin
            )
    elif search_type == "hybrid":
        # 混合搜索：同时返回关键词和向量结果，去重合并
        try:
            from app.services.embedding_service import embedding_service

            # 向量搜索
            query_vector = embedding_service.encode_single(q)
            vector_ids = search_service.search_vector(
                query_vector=query_vector,
                user_id=user_id,
                category=category,
                limit=page_size,
                is_admin=is_admin
            )

            # 关键词搜索
            keyword_result = search_service.search_keyword(
                query=q, user_id=user_id, category=category,
                page=1, page_size=page_size, is_admin=is_admin
            )

            # 合并结果，向量结果优先
            seen_ids = set()
            merged_items = []

            for kid in vector_ids:
                if kid not in seen_ids:
                    doc = search_service.get_by_id(kid)
                    if doc:
                        merged_items.append({
                            "id": doc["id"],
                            "title": doc["title"],
                            "summary": doc.get("summary", ""),
                            "category": doc.get("category", ""),
                            "source": doc.get("source", ""),
                            "tags": doc.get("tags", []),
                            "view_count": doc.get("view_count", 0),
                            "score": 0.9,
                            "highlight": {}
                        })
                        seen_ids.add(kid)

            for item in keyword_result["items"]:
                if item["id"] not in seen_ids:
                    merged_items.append(item)
                    seen_ids.add(item["id"])

            result = {
                "items": merged_items[:page_size],
                "total": len(merged_items),
                "page": page,
                "page_size": page_size
            }
        except Exception as e:
            print(f"混合搜索失败，fallback到关键词搜索: {e}")
            result = search_service.search_keyword(
                query=q, user_id=user_id, category=category,
                page=page, page_size=page_size, is_admin=is_admin
            )
    else:
        # 关键词搜索（默认）
        result = search_service.search_keyword(
            query=q,
            user_id=user_id,
            category=category,
            page=page,
            page_size=page_size,
            is_admin=is_admin
        )

    # 补充分类名称
    for item in result["items"]:
        item["category_name"] = get_category_name(item["category"])

    # 记录热搜词
    try:
        redis_client.zincrby(HOT_TERMS_KEY, 1, q)
    except Exception:
        pass

    result["search_type"] = search_type
    return SearchResponse(**result)


@router.get("/suggest")
def suggest_knowledge(
    q: str = Query(..., min_length=1),
    limit: int = Query(10, ge=1, le=50),
    current_user: User = Depends(get_current_user)
):
    """搜索建议"""
    is_admin = current_user.is_superuser == 1
    return search_service.suggest(
        query=q,
        user_id=str(current_user.id),
        limit=limit,
        is_admin=is_admin
    )


@router.get("/search/hot-terms")
def get_hot_search_terms(
    limit: int = Query(10, ge=1, le=50),
    current_user: User = Depends(get_current_user)
):
    """获取热门搜索词"""
    try:
        # 返回按搜索次数倒序的热搜词
        terms = redis_client.zrevrange(HOT_TERMS_KEY, 0, limit - 1, withscores=True)
        return [{"term": term, "count": int(score)} for term, score in terms]
    except Exception:
        return []


@router.get("/hot", response_model=list[HotKnowledgeItem])
def get_hot_knowledge(
    limit: int = Query(10, ge=1, le=50),
    current_user: User = Depends(get_current_user)
):
    """获取热门知识"""
    is_admin = current_user.is_superuser == 1
    return search_service.get_hot_knowledge(
        user_id=str(current_user.id),
        limit=limit,
        is_admin=is_admin
    )


@router.get("/latest", response_model=list[LatestKnowledgeItem])
def get_latest_knowledge(
    limit: int = Query(10, ge=1, le=50),
    current_user: User = Depends(get_current_user)
):
    """获取最新知识"""
    is_admin = current_user.is_superuser == 1
    return search_service.get_latest_knowledge(
        user_id=str(current_user.id),
        limit=limit,
        is_admin=is_admin
    )


@router.get("/stats", response_model=KnowledgeStatsResponse)
def get_knowledge_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取知识统计信息"""
    is_admin = current_user.is_superuser == 1

    if is_admin:
        query = db.query(Knowledge)
    else:
        query = db.query(Knowledge).filter(Knowledge.user_id == str(current_user.id))

    total = query.count()
    esIndexed = query.filter(Knowledge.es_indexed == "indexed").count()
    vectorDone = query.filter(Knowledge.vector_indexed == "done").count()
    graphDone = query.filter(Knowledge.graph_indexed == "done").count()

    return KnowledgeStatsResponse(
        total=total,
        esIndexed=esIndexed,
        vectorDone=vectorDone,
        graphDone=graphDone
    )


@router.get("/{knowledge_id}/file-url")
def get_knowledge_file_url(
    knowledge_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取知识文件下载链接"""
    is_admin = current_user.is_superuser == 1

    if is_admin:
        knowledge = db.query(Knowledge).filter(Knowledge.id == knowledge_id).first()
    else:
        knowledge = db.query(Knowledge).filter(
            Knowledge.id == knowledge_id,
            Knowledge.user_id == str(current_user.id)
        ).first()

    if not knowledge:
        raise HTTPException(status_code=404, detail="知识不存在")

    if not knowledge.file_path:
        raise HTTPException(status_code=404, detail="该知识没有关联文件")

    try:
        url = minio_service.get_file_url(knowledge.file_path)
        return {"url": url, "file_type": knowledge.file_type}
    except Exception as e:
        print(f"获取文件URL失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取文件URL失败: {str(e)}")


@router.get("/{knowledge_id}/download")
def download_knowledge_file(
    knowledge_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """下载知识文件（后端代理下载）"""
    is_admin = current_user.is_superuser == 1

    if is_admin:
        knowledge = db.query(Knowledge).filter(Knowledge.id == knowledge_id).first()
    else:
        knowledge = db.query(Knowledge).filter(
            Knowledge.id == knowledge_id,
            Knowledge.user_id == str(current_user.id)
        ).first()

    if not knowledge:
        raise HTTPException(status_code=404, detail="知识不存在")

    if not knowledge.file_path:
        raise HTTPException(status_code=404, detail="该知识没有关联文件")

    try:
        file_data = minio_service.download_file(knowledge.file_path)

        # 根据文件类型确定 content-type
        content_types = {
            'pdf': 'application/pdf',
            'doc': 'application/msword',
            'docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
        }
        content_type = content_types.get(knowledge.file_type, 'application/octet-stream')

        from fastapi.responses import Response
        import urllib.parse

        # URL编码文件名，避免中文编码问题
        filename = urllib.parse.quote(f"{knowledge.title}.{knowledge.file_type}")
        return Response(
            content=file_data,
            media_type=content_type,
            headers={
                'Content-Disposition': f'attachment; filename="{filename}"; filename*=UTF-8\'\'{filename}'
            }
        )
    except Exception as e:
        print(f"下载文件失败: {e}")
        raise HTTPException(status_code=500, detail=f"下载文件失败: {str(e)}")


@router.get("/{knowledge_id}", response_model=KnowledgeDetail)
def get_knowledge_detail(
    knowledge_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取知识详情"""
    is_admin = current_user.is_superuser == 1

    if is_admin:
        knowledge = db.query(Knowledge).filter(Knowledge.id == knowledge_id).first()
    else:
        knowledge = db.query(Knowledge).filter(
            Knowledge.id == knowledge_id,
            Knowledge.user_id == str(current_user.id)
        ).first()

    if not knowledge:
        raise HTTPException(status_code=404, detail="知识不存在")

    # 增加浏览次数
    knowledge.view_count += 1
    db.commit()

    # 同步更新 ES 的 view_count
    try:
        from elasticsearch import Elasticsearch
        es = Elasticsearch([settings.elasticsearch_url])
        es.update(
            index=search_service.INDEX_NAME,
            id=knowledge_id,
            body={"doc": {"view_count": knowledge.view_count}}
        )
    except Exception:
        pass

    # 检查是否已收藏
    is_favorited = db.query(UserFavorite).filter(
        UserFavorite.user_id == str(current_user.id),
        UserFavorite.knowledge_id == knowledge_id
    ).first() is not None

    # 从ES获取完整content（MySQL只存了summary）
    content = None
    try:
        es_doc = search_service.get_by_id(knowledge_id)
        if es_doc:
            content = es_doc.get("content")
    except Exception:
        pass

    return KnowledgeDetail(
        id=knowledge.id,
        title=knowledge.title,
        content=content,  # 从ES获取的完整内容
        summary=knowledge.summary,
        category=knowledge.category,
        category_name=get_category_name(knowledge.category),
        source=knowledge.source,
        tags=knowledge.tags or [],
        view_count=knowledge.view_count,
        favorite_count=knowledge.favorite_count,
        created_at=knowledge.created_at,
        updated_at=knowledge.updated_at,
        file_path=knowledge.file_path,
        file_type=knowledge.file_type,
        is_favorited=is_favorited
    )


@router.put("/{knowledge_id}")
def update_knowledge(
    knowledge_id: str,
    update_data: KnowledgeUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """更新知识"""
    knowledge = db.query(Knowledge).filter(
        Knowledge.id == knowledge_id,
        Knowledge.user_id == str(current_user.id)
    ).first()

    if not knowledge:
        raise HTTPException(status_code=404, detail="知识不存在")

    if update_data.title is not None:
        knowledge.title = update_data.title
    if update_data.category is not None:
        knowledge.category = update_data.category
    if update_data.source is not None:
        knowledge.source = update_data.source
    if update_data.tags is not None:
        knowledge.tags = update_data.tags

    db.commit()

    return {"message": "更新成功"}


@router.delete("/{knowledge_id}")
def delete_knowledge(
    knowledge_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """删除知识"""
    knowledge = db.query(Knowledge).filter(
        Knowledge.id == knowledge_id,
        Knowledge.user_id == str(current_user.id)
    ).first()

    if not knowledge:
        raise HTTPException(status_code=404, detail="知识不存在")

    # 删除 MinIO 文件
    if knowledge.file_path:
        try:
            minio_service.delete_file(knowledge.file_path)
        except Exception:
            pass

    # 删除搜索索引
    try:
        search_service.delete_knowledge_index(knowledge_id)
    except Exception:
        pass

    # 删除 Neo4j 相关数据（通过 knowledge_id 关联的实体）
    try:
        if GRAPH_EXTRACTOR_AVAILABLE:
            extractor = get_graph_extractor()
            stats = extractor.delete_from_neo4j(knowledge_id)
            print(f"Neo4j 清理完成: knowledge_id={knowledge_id}, "
                  f"checked={stats['entities_checked']}, "
                  f"deleted={stats['entities_deleted']}, "
                  f"retained={stats['entities_retained']}")
    except Exception as e:
        print(f"Neo4j 清理失败: {e}")

    # 删除数据库记录
    db.delete(knowledge)
    db.commit()

    return {"message": "删除成功"}


@router.post("/{knowledge_id}/favorite")
def favorite_knowledge(
    knowledge_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """收藏知识"""
    is_admin = current_user.is_superuser == 1

    if is_admin:
        knowledge = db.query(Knowledge).filter(Knowledge.id == knowledge_id).first()
    else:
        knowledge = db.query(Knowledge).filter(
            Knowledge.id == knowledge_id,
            Knowledge.user_id == str(current_user.id)
        ).first()

    if not knowledge:
        raise HTTPException(status_code=404, detail="知识不存在")

    # 检查是否已收藏
    existing = db.query(UserFavorite).filter(
        UserFavorite.user_id == str(current_user.id),
        UserFavorite.knowledge_id == knowledge_id
    ).first()

    if existing:
        return {"message": "已收藏"}

    favorite = UserFavorite(
        id=str(uuid.uuid4()),
        user_id=str(current_user.id),
        knowledge_id=knowledge_id
    )
    db.add(favorite)

    # 增加收藏数
    knowledge.favorite_count += 1
    db.commit()

    return {"message": "收藏成功"}


@router.delete("/{knowledge_id}/favorite")
def unfavorite_knowledge(
    knowledge_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """取消收藏"""
    favorite = db.query(UserFavorite).filter(
        UserFavorite.user_id == str(current_user.id),
        UserFavorite.knowledge_id == knowledge_id
    ).first()

    if favorite:
        knowledge = db.query(Knowledge).filter(Knowledge.id == knowledge_id).first()
        if knowledge and knowledge.favorite_count > 0:
            knowledge.favorite_count -= 1
        db.delete(favorite)
        db.commit()

    return {"message": "已取消收藏"}


@router.get("/{knowledge_id}/comments", response_model=list[CommentItem])
def list_comments(
    knowledge_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取评论列表"""
    comments = db.query(KnowledgeComment).filter(
        KnowledgeComment.knowledge_id == knowledge_id
    ).order_by(KnowledgeComment.created_at.desc()).all()

    return [
        CommentItem(
            id=c.id,
            knowledge_id=c.knowledge_id,
            user_id=c.user_id,
            user_name=c.user.full_name if c.user else "未知",
            content=c.content,
            created_at=c.created_at
        )
        for c in comments
    ]


@router.post("/{knowledge_id}/comments", response_model=CommentItem)
def create_comment(
    knowledge_id: str,
    comment_data: CommentCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """添加评论"""
    is_admin = current_user.is_superuser == 1

    if is_admin:
        knowledge = db.query(Knowledge).filter(Knowledge.id == knowledge_id).first()
    else:
        knowledge = db.query(Knowledge).filter(
            Knowledge.id == knowledge_id,
            Knowledge.user_id == str(current_user.id)
        ).first()

    if not knowledge:
        raise HTTPException(status_code=404, detail="知识不存在")

    comment = KnowledgeComment(
        id=str(uuid.uuid4()),
        knowledge_id=knowledge_id,
        user_id=str(current_user.id),
        content=comment_data.content
    )
    db.add(comment)
    db.commit()

    return CommentItem(
        id=comment.id,
        knowledge_id=comment.knowledge_id,
        user_id=comment.user_id,
        user_name=current_user.full_name,
        content=comment.content,
        created_at=comment.created_at
    )


@router.post("/{knowledge_id}/rebuild/{index_type}")
def rebuild_knowledge_index(
    knowledge_id: str,
    index_type: str = Path(..., pattern="^(es|vector|graph)$"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """重建指定知识的索引"""
    is_admin = current_user.is_superuser == 1

    if is_admin:
        knowledge = db.query(Knowledge).filter(Knowledge.id == knowledge_id).first()
    else:
        knowledge = db.query(Knowledge).filter(
            Knowledge.id == knowledge_id,
            Knowledge.user_id == str(current_user.id)
        ).first()

    if not knowledge:
        raise HTTPException(status_code=404, detail="知识不存在")

    # 更新状态为pending并触发重建
    if index_type == "es":
        knowledge.es_indexed = "pending"
        try:
            search_service.delete_knowledge_index(knowledge_id)
            if knowledge.content:
                search_service.index_knowledge(
                    knowledge_id=knowledge_id,
                    title=knowledge.title,
                    content=knowledge.content,
                    summary=knowledge.summary or "",
                    category=knowledge.category,
                    source=knowledge.source or "",
                    tags=knowledge.tags or [],
                    user_id=str(knowledge.user_id),
                    created_at=str(knowledge.created_at),
                    view_count=knowledge.view_count
                )
                knowledge.es_indexed = "indexed"
        except Exception as e:
            print(f"ES索引重建失败: {e}")
            knowledge.es_indexed = "failed"
    elif index_type == "vector":
        knowledge.vector_indexed = "pending"
        try:
            search_service.delete_knowledge_index(knowledge_id)
            if knowledge.content:
                search_service.index_vector(
                    knowledge_id=knowledge_id,
                    title=knowledge.title,
                    content=knowledge.content,
                    category=knowledge.category,
                    user_id=str(knowledge.user_id)
                )
                knowledge.vector_indexed = "done"
        except Exception as e:
            print(f"向量索引重建失败: {e}")
            knowledge.vector_indexed = "failed"
    elif index_type == "graph":
        knowledge.graph_indexed = "pending"
        db.commit()
        # 异步重建图谱
        # 先尝试从ES获取content（MySQL不存完整content）
        content = None
        try:
            es_doc = search_service.get_by_id(knowledge_id)
            if es_doc:
                content = es_doc.get("content")
        except Exception:
            pass

        if GRAPH_EXTRACTOR_AVAILABLE and content:
            try:
                extractor = get_graph_extractor()
                extractor.delete_from_neo4j(knowledge_id)
                # 直接线程调用，不依赖 asyncio 事件循环
                import threading
                thread = threading.Thread(
                    target=_sync_knowledge_to_neo4j,
                    args=(knowledge_id, content),
                    daemon=True
                )
                thread.start()
            except Exception as e:
                print(f"图谱重建失败: {e}")
                knowledge.graph_indexed = "failed"
        else:
            knowledge.graph_indexed = "failed"

    db.commit()

    return {"message": "已提交重建任务", "status": getattr(knowledge, f"{index_type}_indexed")}


@router.delete("/{knowledge_id}/clear/{index_type}")
def clear_knowledge_index(
    knowledge_id: str,
    index_type: str = Path(..., pattern="^(es|vector|graph)$"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """清空指定知识的索引"""
    is_admin = current_user.is_superuser == 1

    if is_admin:
        knowledge = db.query(Knowledge).filter(Knowledge.id == knowledge_id).first()
    else:
        knowledge = db.query(Knowledge).filter(
            Knowledge.id == knowledge_id,
            Knowledge.user_id == str(current_user.id)
        ).first()

    if not knowledge:
        raise HTTPException(status_code=404, detail="知识不存在")

    # 清空对应索引
    if index_type == "es":
        knowledge.es_indexed = "none"
        try:
            search_service.delete_knowledge_index(knowledge_id)
        except Exception:
            pass
    elif index_type == "vector":
        knowledge.vector_indexed = "none"
        try:
            search_service.delete_knowledge_index(knowledge_id)
        except Exception:
            pass
    elif index_type == "graph":
        knowledge.graph_indexed = "none"
        try:
            if GRAPH_EXTRACTOR_AVAILABLE:
                extractor = get_graph_extractor()
                extractor.delete_from_neo4j(knowledge_id)
        except Exception:
            pass

    db.commit()

    return {"message": "已清空数据"}
