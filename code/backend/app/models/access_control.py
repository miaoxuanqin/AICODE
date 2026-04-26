import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, Text, ForeignKey, CHAR, Enum, Integer
from sqlalchemy.orm import relationship
from app.database import Base
import enum


class AccessType(str, enum.Enum):
    PUBLIC = "public"        # 公开
    ORG = "org"             # 组织内
    CATEGORY = "category"   # 分类可见
    PRIVATE = "private"     # 私有


class AccessPermission(str, enum.Enum):
    READ = "read"
    WRITE = "write"
    ADMIN = "admin"


class KnowledgeAccess(Base):
    """知识数据访问控制表"""
    __tablename__ = "knowledge_access"

    id = Column(CHAR(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    # 三种授权方式（互斥）
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)      # 用户级别
    role_id = Column(CHAR(36), ForeignKey("roles.id"), nullable=True)      # 角色级别
    org_id = Column(CHAR(36), ForeignKey("organizations.id"), nullable=True)  # 组织级别

    access_type = Column(Enum(AccessType), nullable=False, default=AccessType.PUBLIC)
    target_id = Column(String(100), nullable=True)  # 分类ID或知识ID，NULL表示全部
    permission = Column(Enum(AccessPermission), nullable=False, default=AccessPermission.READ)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    description = Column(Text, nullable=True)

    user = relationship("User")
    role = relationship("Role")
    org = relationship("Organization")
