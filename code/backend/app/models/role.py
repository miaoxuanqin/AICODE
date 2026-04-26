import uuid
from datetime import datetime
from sqlalchemy import Column, String, Boolean, DateTime, Text, ForeignKey, CHAR, Table, Integer
from sqlalchemy.orm import relationship
from app.database import Base


class Permission(Base):
    __tablename__ = "permissions"

    id = Column(CHAR(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    code = Column(String(100), unique=True, nullable=False, index=True)
    name = Column(String(100), nullable=False)
    module = Column(String(50), nullable=False)  # knowledge/portal/config/system
    description = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    roles = relationship("RolePermission", back_populates="permission")


class Role(Base):
    __tablename__ = "roles"

    id = Column(CHAR(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    code = Column(String(50), unique=True, nullable=False, index=True)
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    is_system = Column(Boolean, default=False)  # 系统预置角色不可删除
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    permissions = relationship("RolePermission", back_populates="role")
    users = relationship("UserRole", back_populates="role")


# 角色-权限关联表
class RolePermission(Base):
    __tablename__ = "role_permissions"

    id = Column(CHAR(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    role_id = Column(CHAR(36), ForeignKey("roles.id"), nullable=False)
    permission_id = Column(CHAR(36), ForeignKey("permissions.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    role = relationship("Role", back_populates="permissions")
    permission = relationship("Permission", back_populates="roles")


# 用户-角色关联表（角色在特定组织下生效）
class UserRole(Base):
    __tablename__ = "user_roles"

    id = Column(CHAR(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    role_id = Column(CHAR(36), ForeignKey("roles.id"), nullable=False)
    org_id = Column(CHAR(36), ForeignKey("organizations.id"), nullable=True)  # NULL表示全局
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="roles")
    role = relationship("Role", back_populates="users")
