from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.user import RoleCreate, RoleUpdate, RoleResponse, RoleWithPermissions, PermissionResponse
from core.rbac import get_current_user, require_permissions
from app.models.user import User
from app.models.role import Role, Permission, RolePermission

router = APIRouter(prefix="/roles", tags=["角色管理"])


@router.get("/", response_model=List[RoleResponse])
def list_roles(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    is_active: Optional[bool] = None,
    current_user: User = Depends(require_permissions(["system:role:list"])),
    db: Session = Depends(get_db)
):
    """获取角色列表"""
    query = db.query(Role)
    if is_active is not None:
        query = query.filter(Role.is_active == is_active)
    roles = query.offset(skip).limit(limit).all()
    return roles


@router.get("/{role_id}", response_model=RoleWithPermissions)
def get_role(
    role_id: str,
    current_user: User = Depends(require_permissions(["system:role:read"])),
    db: Session = Depends(get_db)
):
    """获取角色详情（含权限）"""
    role = db.query(Role).filter(Role.id == role_id).first()
    if not role:
        raise HTTPException(status_code=404, detail="角色不存在")

    # 获取角色的权限
    permissions = db.query(Permission).join(
        RolePermission, RolePermission.permission_id == Permission.id
    ).filter(RolePermission.role_id == role_id).all()

    return {
        "id": role.id,
        "code": role.code,
        "name": role.name,
        "description": role.description,
        "is_system": role.is_system,
        "is_active": role.is_active,
        "created_at": role.created_at,
        "permissions": permissions
    }


@router.post("/", response_model=RoleResponse, status_code=status.HTTP_201_CREATED)
def create_role(
    role_data: RoleCreate,
    current_user: User = Depends(require_permissions(["system:role:create"])),
    db: Session = Depends(get_db)
):
    """创建角色"""
    existing = db.query(Role).filter(Role.code == role_data.code).first()
    if existing:
        raise HTTPException(status_code=400, detail="角色代码已存在")

    role = Role(
        code=role_data.code,
        name=role_data.name,
        description=role_data.description,
        is_system=False
    )
    db.add(role)
    db.flush()

    # 关联权限
    for perm_id in role_data.permission_ids:
        rp = RolePermission(role_id=role.id, permission_id=perm_id)
        db.add(rp)

    db.commit()
    db.refresh(role)
    return role


@router.patch("/{role_id}", response_model=RoleResponse)
def update_role(
    role_id: str,
    role_data: RoleUpdate,
    current_user: User = Depends(require_permissions(["system:role:update"])),
    db: Session = Depends(get_db)
):
    """更新角色"""
    role = db.query(Role).filter(Role.id == role_id).first()
    if not role:
        raise HTTPException(status_code=404, detail="角色不存在")

    if role.is_system:
        raise HTTPException(status_code=400, detail="系统预置角色不可修改")

    if role_data.name is not None:
        role.name = role_data.name
    if role_data.description is not None:
        role.description = role_data.description

    # 更新权限
    if role_data.permission_ids is not None:
        # 删除旧关联
        db.query(RolePermission).filter(RolePermission.role_id == role.id).delete()
        # 添加新关联
        for perm_id in role_data.permission_ids:
            rp = RolePermission(role_id=role.id, permission_id=perm_id)
            db.add(rp)

    db.commit()
    db.refresh(role)
    return role


@router.delete("/{role_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_role(
    role_id: str,
    current_user: User = Depends(require_permissions(["system:role:delete"])),
    db: Session = Depends(get_db)
):
    """删除角色"""
    role = db.query(Role).filter(Role.id == role_id).first()
    if not role:
        raise HTTPException(status_code=404, detail="角色不存在")

    if role.is_system:
        raise HTTPException(status_code=400, detail="系统预置角色不可删除")

    role.is_active = False
    db.commit()


# ============ 权限管理 ============

permission_router = APIRouter(prefix="/permissions", tags=["权限管理"])


@permission_router.get("/", response_model=List[PermissionResponse])
def list_permissions(
    module: Optional[str] = None,
    current_user: User = Depends(require_permissions(["system:permission:list"])),
    db: Session = Depends(get_db)
):
    """获取权限列表"""
    query = db.query(Permission)
    if module:
        query = query.filter(Permission.module == module)
    return query.all()
