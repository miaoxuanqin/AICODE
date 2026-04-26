from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.user import UserCreate, UserUpdate, UserResponse, UserWithRoles, UserWithRoleIds
from app.services.auth_service import AuthService
from core.rbac import get_current_user, require_permissions
from app.models.user import User
from app.models.role import UserRole

router = APIRouter(prefix="/users", tags=["用户管理"])


@router.get("/", response_model=List[UserWithRoleIds])
def list_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    org_id: Optional[str] = None,
    is_active: Optional[bool] = None,
    current_user: User = Depends(require_permissions(["system:user:list"])),
    db: Session = Depends(get_db)
):
    """获取用户列表"""
    query = db.query(User)
    if org_id:
        query = query.filter(User.org_id == org_id)
    if is_active is not None:
        query = query.filter(User.is_active == is_active)

    users = query.offset(skip).limit(limit).all()

    # 获取每个用户的角色ID
    result = []
    for user in users:
        role_ids = db.query(UserRole.role_id).filter(UserRole.user_id == user.id).all()
        user_dict = {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "phone": user.phone,
            "full_name": user.full_name,
            "org_id": user.org_id,
            "is_active": user.is_active,
            "is_superuser": user.is_superuser,
            "created_at": user.created_at,
            "last_login_at": user.last_login_at,
            "role_ids": [r[0] for r in role_ids]
        }
        result.append(user_dict)

    return result


@router.get("/{user_id}", response_model=UserWithRoles)
def get_user(
    user_id: str,
    current_user: User = Depends(require_permissions(["system:user:read"])),
    db: Session = Depends(get_db)
):
    """获取用户详情"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    return user


@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def create_user(
    user_data: UserCreate,
    current_user: User = Depends(require_permissions(["system:user:create"])),
    db: Session = Depends(get_db)
):
    """创建用户"""
    existing = db.query(User).filter(User.username == user_data.username).first()
    if existing:
        raise HTTPException(status_code=400, detail="用户名已存在")

    auth_service = AuthService(db)
    user = auth_service.create_user(
        username=user_data.username,
        password=user_data.password,
        email=user_data.email,
        phone=user_data.phone,
        full_name=user_data.full_name,
        org_id=user_data.org_id,
        is_active=user_data.is_active
    )
    return user


@router.patch("/{user_id}", response_model=UserResponse)
def update_user(
    user_id: str,
    user_data: UserUpdate,
    current_user: User = Depends(require_permissions(["system:user:update"])),
    db: Session = Depends(get_db)
):
    """更新用户"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")

    update_data = user_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        if value is not None:
            setattr(user, field, value)

    db.commit()
    db.refresh(user)
    return user


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(
    user_id: str,
    current_user: User = Depends(require_permissions(["system:user:delete"])),
    db: Session = Depends(get_db)
):
    """删除用户（软删除）"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")

    user.is_active = False
    db.commit()


@router.post("/{user_id}/roles")
def assign_user_roles(
    user_id: str,
    role_ids: List[str],
    current_user: User = Depends(require_permissions(["system:user:update"])),
    db: Session = Depends(get_db)
):
    """为用户分配角色"""
    from app.models.role import UserRole
    import uuid

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")

    # 删除旧的角色关联
    db.query(UserRole).filter(UserRole.user_id == user_id).delete()

    # 添加新的角色关联
    for role_id in role_ids:
        ur = UserRole(
            id=str(uuid.uuid4()),
            user_id=user_id,
            role_id=role_id
        )
        db.add(ur)

    db.commit()
    return {"message": "角色分配成功"}
