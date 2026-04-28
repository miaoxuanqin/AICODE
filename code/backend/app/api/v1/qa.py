"""
问答助手 API 路由
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.qa import (
    QAChatRequest,
    QAChatResponse,
    QAStatsResponse,
    QAHotQuestionsResponse,
    QARateRequest,
    QAHistoryResponse,
    QASessionResponse,
    QASessionDetailResponse,
    QASessionListResponse,
    QAChatRequestWithSession,
    QASessionCreateRequest
)
from app.services.qa_service import qa_service
from core.rbac import get_current_user

router = APIRouter(prefix="/qa", tags=["问答助手"])


# ============ Session 管理 ============

@router.post("/session", response_model=QASessionResponse)
async def create_session(
    request: QASessionCreateRequest = None,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    创建新会话
    """
    title = request.title if request else "新对话"
    category = request.category if request else "qa"
    session = qa_service.create_session(str(current_user.id), db, title=title, category=category)
    if not session:
        raise HTTPException(status_code=500, detail="创建会话失败")
    return session


@router.get("/sessions", response_model=QASessionListResponse)
async def get_sessions(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    获取用户的所有会话
    """
    sessions = qa_service.get_sessions(str(current_user.id), db)
    return {"items": sessions}


@router.get("/session/{session_id}", response_model=QASessionDetailResponse)
async def get_session(
    session_id: str,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    获取会话详情（含消息历史）
    """
    session = qa_service.get_session_detail(session_id, str(current_user.id), db)
    if not session:
        raise HTTPException(status_code=404, detail="会话不存在")
    return session


@router.delete("/session/{session_id}")
async def delete_session(
    session_id: str,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    删除会话
    """
    success = qa_service.delete_session(session_id, str(current_user.id), db)
    return {"success": success}


@router.delete("/session/{session_id}/messages")
async def clear_session_messages(
    session_id: str,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    清除会话消息（保留会话）
    """
    success = qa_service.clear_session_messages(session_id, str(current_user.id), db)
    return {"success": success}


# ============ 核心问答 ============

@router.post("/chat", response_model=QAChatResponse)
async def chat(
    request: QAChatRequestWithSession,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    问答对话（支持多轮会话）

    - 接收用户问题
    - 检索相关知识
    - 调用 LLM 生成回答
    - 返回答案、知识卡片、相关问题
    - 如果传入 session_id，关联到对应会话
    """
    result = qa_service.ask(
        question=request.question,
        user_id=request.user_id or str(current_user.id),
        session_id=request.session_id,
        db=db,
        is_admin=current_user.is_superuser == 1
    )
    return result


@router.get("/stats", response_model=QAStatsResponse)
async def get_stats(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    获取问答统计

    - 累计问答数
    - 今日问答数
    - 满意度
    """
    user_id = str(current_user.id)
    stats = qa_service.get_stats(user_id, db)
    return stats


@router.get("/hot-questions", response_model=QAHotQuestionsResponse)
async def get_hot_questions(
    limit: int = 5,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    获取热门问题

    - limit: 返回数量
    """
    questions = qa_service.get_hot_questions(limit=limit, db=db)
    return {"items": questions}


@router.post("/rate")
async def rate(
    request: QARateRequest,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    评价问答结果

    - question_id: 问答记录ID
    - rating: up 或 down
    """
    success = qa_service.rate(request.question_id, request.rating, db)
    return {"success": success}


@router.get("/history", response_model=QAHistoryResponse)
async def get_history(
    limit: int = 10,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    获取问答历史记录

    - limit: 返回数量
    """
    user_id = str(current_user.id)
    history = qa_service.get_history(user_id, limit, db)
    return {"items": history}
