import uuid
from datetime import datetime
from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey, CHAR, Integer
from sqlalchemy.orm import relationship
from app.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    email = Column(String(100), nullable=True)
    phone = Column(String(20), nullable=True)
    full_name = Column(String(100), nullable=True)
    org_id = Column(CHAR(36), ForeignKey("organizations.id"), nullable=True)
    is_active = Column(Integer, default=True)
    is_superuser = Column(Integer, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login_at = Column(DateTime, nullable=True)

    organization = relationship("Organization", back_populates="users")
    roles = relationship("UserRole", back_populates="user")
