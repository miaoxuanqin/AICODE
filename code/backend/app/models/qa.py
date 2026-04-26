"""
问答助手数据库模型
"""
from sqlalchemy import Column, String, Integer, Text, DateTime, JSON, Enum as SQLEnum, ForeignKey, SmallInteger
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base


class QARecord(Base):
    """问答记录表"""
    __tablename__ = "qa_records"

    id = Column(String(36), primary_key=True)
    user_id = Column(String(36), nullable=False, index=True)
    question = Column(Text, nullable=False)
    answer = Column(Text, nullable=False)
    search_results = Column(JSON, nullable=True)  # 检索到的知识列表
    rating = Column(String(10), nullable=True)     # up/down/null
    created_at = Column(DateTime, server_default=func.now(), index=True)


class QAHotQuestion(Base):
    """热门问题表"""
    __tablename__ = "qa_hot_questions"

    id = Column(String(36), primary_key=True)
    question = Column(String(500), nullable=False)
    count = Column(Integer, default=1)
    last_updated = Column(DateTime, server_default=func.now(), onupdate=func.now())


class QAHistory(Base):
    """问答历史记录表"""
    __tablename__ = "qa_history"

    id = Column(String(36), primary_key=True)
    user_id = Column(String(36), nullable=False, index=True)
    question = Column(String(500), nullable=False)
    answer = Column(Text, nullable=True)
    created_at = Column(DateTime, server_default=func.now(), index=True)


class QASession(Base):
    """QA 会话表"""
    __tablename__ = "qa_session"

    id = Column(String(36), primary_key=True)
    user_id = Column(String(36), nullable=False, index=True)
    title = Column(String(200), default='新对话')
    category = Column(String(50), default='qa', index=True)  # qa/law_general/supervise
    is_active = Column(SmallInteger, default=1)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    # 关联消息
    messages = relationship("QASessionMessage", back_populates="session",
                           cascade="all, delete-orphan", order_by="QASessionMessage.created_at")


class QASessionMessage(Base):
    """QA 会话消息表"""
    __tablename__ = "qa_session_message"

    id = Column(String(36), primary_key=True)
    session_id = Column(String(36), ForeignKey("qa_session.id", ondelete="CASCADE"), nullable=False, index=True)
    role = Column(SQLEnum('user', 'assistant', name='message_role'), nullable=False)
    content = Column(Text, nullable=False)
    qa_record_id = Column(String(36), nullable=True)
    created_at = Column(DateTime, server_default=func.now())

    # 关联会话
    session = relationship("QASession", back_populates="messages")