from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, ConfigDict


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