from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, ConfigDict


# ============ 用户 Schema ============

class UserBase(BaseModel):
    username: str
    email: Optional[str] = None
    phone: Optional[str] = None
    full_name: Optional[str] = None
    org_id: Optional[str] = None
    is_active: bool = True


class UserCreate(UserBase):
    password: str


class UserUpdate(BaseModel):
    email: Optional[str] = None
    phone: Optional[str] = None
    full_name: Optional[str] = None
    org_id: Optional[str] = None
    is_active: Optional[bool] = None


class UserResponse(UserBase):
    id: int
    is_superuser: bool
    created_at: datetime
    last_login_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class UserWithRoles(UserResponse):
    roles: List["RoleResponse"] = []

    model_config = ConfigDict(from_attributes=True)


class UserWithRoleIds(UserResponse):
    role_ids: List[str] = []

    model_config = ConfigDict(from_attributes=True)


# ============ 组织 Schema ============

class OrganizationBase(BaseModel):
    name: str
    code: str
    parent_id: Optional[str] = None
    level: str
    path: str
    description: Optional[str] = None


class OrganizationCreate(OrganizationBase):
    pass


class OrganizationResponse(OrganizationBase):
    id: str
    is_active: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# ============ 角色 Schema ============

class PermissionBase(BaseModel):
    code: str
    name: str
    module: str
    description: Optional[str] = None


class PermissionCreate(PermissionBase):
    pass


class PermissionResponse(PermissionBase):
    id: str
    is_active: bool

    model_config = ConfigDict(from_attributes=True)


class RoleBase(BaseModel):
    code: str
    name: str
    description: Optional[str] = None


class RoleCreate(RoleBase):
    permission_ids: List[str] = []


class RoleUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    permission_ids: Optional[List[str]] = None


class RoleResponse(RoleBase):
    id: str
    is_system: bool
    is_active: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class RoleWithPermissions(RoleResponse):
    permissions: List[PermissionResponse] = []

    model_config = ConfigDict(from_attributes=True)


# ============ 认证 Schema ============

class LoginRequest(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int


class TokenPayload(BaseModel):
    sub: str  # user_id
    exp: datetime


# ============ 访问控制 Schema ============

class KnowledgeAccessBase(BaseModel):
    access_type: str
    target_id: Optional[str] = None
    permission: str = "read"
    description: Optional[str] = None


class KnowledgeAccessCreate(KnowledgeAccessBase):
    user_id: Optional[str] = None
    role_id: Optional[str] = None
    org_id: Optional[str] = None


class KnowledgeAccessResponse(KnowledgeAccessBase):
    id: str
    user_id: Optional[str] = None
    role_id: Optional[str] = None
    org_id: Optional[str] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# Forward reference
UserWithRoles.model_rebuild()
