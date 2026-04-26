"""
问答模块 Pydantic Schemas
"""
from pydantic import BaseModel, Field
from typing import List, Optional


class QAChatRequest(BaseModel):
    """问答请求"""
    question: str = Field(..., min_length=1, max_length=1000, description="用户问题")
    user_id: Optional[str] = Field(None, description="用户ID")


class KnowledgeCard(BaseModel):
    """知识卡片"""
    id: str
    title: str
    summary: str
    category: str = ""
    source: str = ""
    confidence: int = 0


class QAChatResponse(BaseModel):
    """问答响应"""
    id: str = Field(description="问答记录ID")
    question: str = Field(description="用户问题")
    answer: str = Field(description="回答内容")
    cards: List[KnowledgeCard] = Field(default_factory=list, description="知识卡片")
    related_questions: List[str] = Field(default_factory=list, description="相关问题推荐")


class QAStatsResponse(BaseModel):
    """问答统计响应"""
    total_count: int = Field(description="累计问答数")
    today_count: int = Field(description="今日问答数")
    satisfaction: int = Field(description="满意度百分比")


class HotQuestion(BaseModel):
    """热门问题"""
    question: str
    count: int


class QAHotQuestionsResponse(BaseModel):
    """热门问题响应"""
    items: List[HotQuestion] = Field(default_factory=list)


class QARateRequest(BaseModel):
    """评价请求"""
    question_id: str = Field(..., description="问答记录ID")
    rating: str = Field(..., pattern="^(up|down)$", description="评价：up或down")


class QAHistoryItem(BaseModel):
    """问答历史记录"""
    question: str
    time: str


class QAHistoryResponse(BaseModel):
    """问答历史响应"""
    items: List[QAHistoryItem] = Field(default_factory=list)


# ============ Session 管理 ============

class SessionMessage(BaseModel):
    """会话消息"""
    id: str
    role: str
    content: str
    time: str


class QASessionResponse(BaseModel):
    """会话响应"""
    id: str
    title: str
    category: Optional[str] = Field(None, description="会话分类：law_general/qa")
    is_active: int
    created_at: str
    updated_at: str


class QASessionCreateRequest(BaseModel):
    """创建会话请求"""
    title: Optional[str] = Field("新对话", description="会话标题")
    category: Optional[str] = Field("qa", description="会话分类：law_general/qa")


class QASessionDetailResponse(BaseModel):
    """会话详情响应"""
    id: str
    title: str
    is_active: int
    created_at: str
    updated_at: str
    messages: List[SessionMessage] = Field(default_factory=list)


class QASessionListResponse(BaseModel):
    """会话列表响应"""
    items: List[QASessionResponse] = Field(default_factory=list)


class QAChatRequestWithSession(BaseModel):
    """带会话的问答请求"""
    question: str = Field(..., min_length=1, max_length=1000, description="用户问题")
    session_id: Optional[str] = Field(None, description="会话ID，为空则创建新会话")
    user_id: Optional[str] = Field(None, description="用户ID")