from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class KnowledgeUploadResponse(BaseModel):
    id: str
    title: str
    category: str
    file_type: str
    status: str


class KnowledgeItem(BaseModel):
    id: str
    title: str
    summary: Optional[str] = None
    category: str
    category_name: Optional[str] = None
    source: Optional[str] = None
    tags: List[str] = []
    view_count: int = 0
    favorite_count: int = 0
    created_at: datetime
    # 新增字段
    es_indexed: Optional[str] = "pending"
    vector_indexed: Optional[str] = "pending"
    graph_indexed: Optional[str] = "pending"
    file_type: Optional[str] = None
    file_path: Optional[str] = None

    class Config:
        from_attributes = True


class KnowledgeDetail(KnowledgeItem):
    content: Optional[str] = None  # 内容从ES获取，此处可能为空
    file_path: Optional[str] = None
    file_type: Optional[str] = None
    is_favorited: bool = False
    updated_at: datetime


class KnowledgeListResponse(BaseModel):
    items: List[KnowledgeItem]
    total: int
    page: int
    page_size: int


class KnowledgeCreate(BaseModel):
    title: str
    content: str
    summary: Optional[str] = None
    category: str = Field(..., pattern="^(law|tech|case|policy)$")
    source: Optional[str] = None
    tags: Optional[List[str]] = []


class KnowledgeUpdate(BaseModel):
    title: Optional[str] = None
    category: Optional[str] = Field(None, pattern="^(law|tech|case|policy)$")
    source: Optional[str] = None
    tags: Optional[List[str]] = None


class SearchResponse(BaseModel):
    items: List[dict]
    total: int
    page: int
    page_size: int
    search_type: str = "keyword"


class HotKnowledgeItem(BaseModel):
    id: str
    title: str
    view_count: int
    category: str


class LatestKnowledgeItem(BaseModel):
    id: str
    title: str
    created_at: datetime
    category: str


class CommentCreate(BaseModel):
    content: str


class CommentItem(BaseModel):
    id: str
    knowledge_id: str
    user_id: int
    user_name: Optional[str] = None
    content: str
    created_at: datetime

    class Config:
        from_attributes = True


class KnowledgeStatsResponse(BaseModel):
    total: int = 0
    esIndexed: int = 0
    vectorDone: int = 0
    graphDone: int = 0


class CategoryStatsItem(BaseModel):
    category: str
    category_name: str
    count: int


class TagStatsItem(BaseModel):
    tag: str
    count: int


class SourceStatsItem(BaseModel):
    source: str
    count: int


class TrendStatsItem(BaseModel):
    date: str
    new_count: int
    index_count: int


class IndexStatusItem(BaseModel):
    category: str
    category_name: str
    completed: int
    in_progress: int
    pending: int
    failed: int


class PortalStatsResponse(BaseModel):
    total: int = 0
    monthly_new: int = 0
    es_indexed: int = 0
    vector_indexed: int = 0
    graph_nodes: int = 0
    user_count: int = 0
    categories: List[CategoryStatsItem] = []
    tags: List[TagStatsItem] = []
    sources: List[SourceStatsItem] = []
    trend: List[TrendStatsItem] = []
    index_status: List[IndexStatusItem] = []


class RecentActivityItem(BaseModel):
    type: str  # upload, create, update, delete, search
    title: str
    description: str
    time: str


class IndexProgressItem(BaseModel):
    name: str
    current: int
    total: int
    percentage: float
    color: str
