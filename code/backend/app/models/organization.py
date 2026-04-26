import uuid
from datetime import datetime
from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.dialects.mysql import CHAR
from sqlalchemy.orm import relationship
from app.database import Base


class Organization(Base):
    __tablename__ = "organizations"

    id = Column(CHAR(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(100), nullable=False)
    code = Column(String(50), unique=True, nullable=False)
    parent_id = Column(CHAR(36), ForeignKey("organizations.id"), nullable=True)
    level = Column(String(20), nullable=False)  # 1=省级, 2=市县级, 3=区县级
    path = Column(String(255), nullable=False)  # 海南/海口市
    description = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    parent = relationship("Organization", remote_side=[id], backref="children")
    users = relationship("User", back_populates="organization")
