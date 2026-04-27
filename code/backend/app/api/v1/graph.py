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

router = APIRouter(prefix="/graph", tags=["图谱问答"])

settings = get_settings()


class GraphQARequest(BaseModel):
    """图谱问答请求"""
    question: str
    session_id: Optional[str] = None


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
    3. 多跳推理 - 扩展关联知识
    4. 图谱构建 - 可视化实体关系
    5. 回答生成 - 综合知识生成回答
    """
    user_id = str(current_user.id)

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