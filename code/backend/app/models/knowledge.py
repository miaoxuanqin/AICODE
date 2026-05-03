import uuid
from datetime import datetime
from sqlalchemy import Column, String, Text, DateTime, ForeignKey, CHAR, Integer, JSON
from sqlalchemy.orm import relationship
from app.database import Base


class Knowledge(Base):
    __tablename__ = "knowledge"

    id = Column(CHAR(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    title = Column(String(500), nullable=False, index=True)
    content = Column(Text, nullable=True)  # 内容存ES，MySQL只存摘要
    summary = Column(Text, nullable=True)
    # 兼容旧数据：category 存储分类标识字符串（如 law/tech/case/policy）
    # 注意：category_id 外键暂未添加到数据库，只用 category 字符串字段
    category = Column(String(50), nullable=False, index=True)
    source = Column(String(500), nullable=True)
    tags = Column(JSON, nullable=True, default=list)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    file_path = Column(String(1000), nullable=True)
    file_type = Column(String(20), nullable=True)  # pdf/doc/docx/html
    view_count = Column(Integer, default=0)
    favorite_count = Column(Integer, default=0)
    status = Column(String(20), default="active")  # active/parse_failed
    # 索引状态字段
    es_indexed = Column(String(20), default="pending")  # indexed/pending/failed/none
    vector_indexed = Column(String(20), default="pending")  # done/pending/failed/none
    graph_indexed = Column(String(20), default="pending")  # done/pending/failed/none
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User", backref="knowledge_items")
    favorites = relationship("UserFavorite", back_populates="knowledge", cascade="all, delete-orphan")
    comments = relationship("KnowledgeComment", back_populates="knowledge", cascade="all, delete-orphan")


class UserFavorite(Base):
    __tablename__ = "user_favorites"

    id = Column(CHAR(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    knowledge_id = Column(CHAR(36), ForeignKey("knowledge.id"), nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    knowledge = relationship("Knowledge", back_populates="favorites")


class KnowledgeComment(Base):
    __tablename__ = "knowledge_comments"

    id = Column(CHAR(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    knowledge_id = Column(CHAR(36), ForeignKey("knowledge.id"), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    knowledge = relationship("Knowledge", back_populates="comments")
    user = relationship("User", backref="knowledge_comments")
