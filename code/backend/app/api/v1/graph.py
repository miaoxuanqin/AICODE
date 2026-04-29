"""
图谱增强问答 API
基于知识图谱的多跳推理问答
"""
from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel
from typing import List, Optional, Dict, Any

from app.config import get_settings
from app.services.graph_service import graph_service
from core.rbac import get_current_user

# Neo4j 导入（可选）
try:
    from app.services.neo4j_service import get_neo4j_service, NEO4J_AVAILABLE
    from app.services.graph_extractor import get_graph_extractor
except ImportError:
    NEO4J_AVAILABLE = False
    get_neo4j_service = None
    get_graph_extractor = None

router = APIRouter(prefix="/graph", tags=["图谱问答"])

settings = get_settings()


class GraphQARequest(BaseModel):
    """图谱问答请求"""
    question: str
    session_id: Optional[str] = None
    use_neo4j: Optional[bool] = False  # 是否使用 Neo4j 增强推理


class GraphNodeData(BaseModel):
    """图谱节点"""
    id: str
    label: str
    type: str
    description: Optional[str] = ""
    attributes: Optional[List[Dict]] = []
    x: Optional[float] = 0
    y: Optional[float] = 0


class GraphEdgeData(BaseModel):
    """图谱边"""
    id: str
    source: str
    target: str
    label: str


class ReasoningStep(BaseModel):
    """推理步骤"""
    step: int
    query: str
    result: str
    entities: Optional[List[str]] = []
    details: Optional[Dict[str, Any]] = {}


class CitationItem(BaseModel):
    """引用来源"""
    id: str
    type: str
    typeName: str
    title: str


class GraphQAResponse(BaseModel):
    """图谱问答响应"""
    answer: str
    reasoning_chain: List[ReasoningStep]
    graph_data: Dict[str, Any]
    citations: List[CitationItem]


@router.post("/qa", response_model=GraphQAResponse)
async def graph_qa(
    request: GraphQARequest,
    current_user = Depends(get_current_user)
):
    """
    图谱增强问答

    1. 实体识别 - 理解问题关键实体
    2. 知识检索 - 从知识库检索相关内容
    3. 多跳推理 - 扩展关联知识（可选择使用 Neo4j）
    4. 图谱构建 - 可视化实体关系
    5. 回答生成 - 综合知识生成回答
    """
    user_id = str(current_user.id)

    # 根据 use_neo4j 参数选择推理方式
    if request.use_neo4j and NEO4J_AVAILABLE:
        result = graph_service.reason_with_neo4j(
            question=request.question,
            user_id=user_id
        )
    else:
        result = graph_service.reason(
            question=request.question,
            user_id=user_id
        )

    return GraphQAResponse(
        answer=result["answer"],
        reasoning_chain=[ReasoningStep(**step) for step in result["reasoning_chain"]],
        graph_data=result["graph_data"],
        citations=[CitationItem(**cit) for cit in result["citations"]]
    )


@router.get("/entity/extract")
def extract_entities(
    q: str = Query(..., min_length=1, description="文本内容"),
    current_user = Depends(get_current_user)
):
    """提取文本中的实体"""
    entities = graph_service.extract_entities(q)
    return {"entities": entities}


@router.post("/graph/build")
def build_graph(
    entities: List[Dict[str, str]],
    current_user = Depends(get_current_user)
):
    """根据实体列表构建图谱"""
    search_results = []
    nodes, edges = graph_service.build_graph(entities, search_results)
    return {"nodes": nodes, "edges": edges}


# ==================== Neo4j API ====================

@router.get("/neo4j/status")
def neo4j_status(current_user = Depends(get_current_user)):
    """查询 Neo4j 连接状态"""
    if not NEO4J_AVAILABLE:
        return {
            "available": False,
            "message": "Neo4j 驱动未安装"
        }

    try:
        neo4j = get_neo4j_service()
        connected = neo4j.verify_connectivity()
        stats = neo4j.get_stats() if connected else {}

        return {
            "available": connected,
            "stats": stats,
            "uri": settings.neo4j_uri
        }
    except Exception as e:
        return {
            "available": False,
            "message": str(e)
        }


@router.get("/neo4j/entity/{entity_name}")
def get_entity_graph(
    entity_name: str,
    depth: int = Query(2, ge=1, le=4, description="查询深度"),
    current_user = Depends(get_current_user)
):
    """获取实体的关联图谱"""
    if not NEO4J_AVAILABLE:
        return {"error": "Neo4j 驱动未安装"}

    try:
        neo4j = get_neo4j_service()
        subgraph = neo4j.get_subgraph(entity_name, depth=depth)
        return subgraph
    except Exception as e:
        return {"error": str(e)}


@router.get("/neo4j/path")
def find_entity_paths(
    from_name: str = Query(..., description="起始实体"),
    to_name: str = Query(..., description="目标实体"),
    max_depth: int = Query(4, ge=1, le=6, description="最大深度"),
    current_user = Depends(get_current_user)
):
    """查找两实体间的路径"""
    if not NEO4J_AVAILABLE:
        return {"error": "Neo4j 驱动未安装"}

    try:
        neo4j = get_neo4j_service()
        paths = neo4j.find_paths(from_name, to_name, max_depth=max_depth)
        return {"paths": paths}
    except Exception as e:
        return {"error": str(e)}


@router.post("/neo4j/sync/{knowledge_id}")
def sync_knowledge_to_neo4j(
    knowledge_id: str,
    text: str = Query(..., description="知识内容"),
    current_user = Depends(get_current_user)
):
    """同步知识到 Neo4j"""
    if not NEO4J_AVAILABLE:
        return {"error": "Neo4j 驱动未安装"}

    if not get_graph_extractor:
        return {"error": "Graph Extractor 未安装"}

    try:
        extractor = get_graph_extractor()
        stats = extractor.sync_to_neo4j(knowledge_id, text)
        return {
            "success": True,
            "knowledge_id": knowledge_id,
            "stats": stats
        }
    except Exception as e:
        return {"error": str(e)}


@router.get("/neo4j/entities/{label}")
def get_entities_by_type(
    label: str,
    limit: int = Query(100, ge=1, le=500, description="返回数量"),
    current_user = Depends(get_current_user)
):
    """按类型获取实体列表"""
    if not NEO4J_AVAILABLE:
        return {"error": "Neo4j 驱动未安装"}

    try:
        neo4j = get_neo4j_service()
        entities = neo4j.get_entity_by_type(label, limit=limit)
        return {"label": label, "count": len(entities), "entities": entities}
    except Exception as e:
        return {"error": str(e)}


# ==================== 图谱浏览 API ====================

@router.get("/explorer/stats")
def get_graph_stats(current_user = Depends(get_current_user)):
    """获取图谱统计信息"""
    if not NEO4J_AVAILABLE:
        return {"available": False, "message": "Neo4j 驱动未安装"}

    try:
        neo4j = get_neo4j_service()
        if not neo4j.verify_connectivity():
            return {"available": False, "message": "Neo4j 连接失败"}

        stats = neo4j.get_graph_stats()
        return {
            "available": True,
            "total_nodes": stats["total_nodes"],
            "total_edges": stats["total_edges"],
            "by_type": stats.get("by_type", {})
        }
    except Exception as e:
        return {"available": False, "message": str(e)}


@router.get("/explorer/center")
def get_center_nodes(
    limit: int = Query(50, ge=10, le=100, description="返回节点数"),
    current_user = Depends(get_current_user)
):
    """获取中心节点（采样展示）"""
    if not NEO4J_AVAILABLE:
        return {"error": "Neo4j 驱动未安装"}

    try:
        neo4j = get_neo4j_service()
        result = neo4j.get_center_nodes(limit=limit)
        return result
    except Exception as e:
        return {"error": str(e)}


@router.get("/explorer/neighbors/{node_name:path}")
def get_node_neighbors(
    node_name: str,
    depth: int = Query(1, ge=1, le=2, description="展开深度"),
    current_user = Depends(get_current_user)
):
    """获取节点的邻居"""
    if not NEO4J_AVAILABLE:
        return {"error": "Neo4j 驱动未安装"}

    try:
        neo4j = get_neo4j_service()
        result = neo4j.get_neighbors(node_name, depth=depth)
        return result
    except Exception as e:
        return {"error": str(e)}


@router.get("/explorer/search")
def search_graph_nodes(
    q: str = Query("", min_length=0, description="搜索关键词"),
    label: str = Query(None, description="按类型筛选"),
    limit: int = Query(20, ge=1, le=50, description="返回数量"),
    current_user = Depends(get_current_user)
):
    """搜索实体"""
    if not NEO4J_AVAILABLE:
        return {"error": "Neo4j 驱动未安装"}

    try:
        neo4j = get_neo4j_service()
        keyword = q if q else None
        results = neo4j.search_nodes(keyword=keyword, label=label, limit=limit)
        return {"results": results, "query": q}
    except Exception as e:
        return {"error": str(e)}


@router.get("/explorer/node/{node_name:path}/relations")
def get_node_relations(
    node_name: str,
    current_user = Depends(get_current_user)
):
    """获取节点的所有关联关系"""
    if not NEO4J_AVAILABLE:
        return {"error": "Neo4j 驱动未安装"}

    try:
        neo4j = get_neo4j_service()
        relations = neo4j.get_node_relations(node_name)
        return {"node_name": node_name, "relations": relations}
    except Exception as e:
        return {"error": str(e)}