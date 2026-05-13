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


@router.get("/{user_id}/favorites")
def list_user_favorites(
    user_id: str,
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取用户收藏列表"""
    # 只能查看自己的收藏，或管理员可以查看
    is_admin = current_user.is_superuser == 1
    if not is_admin and str(current_user.id) != user_id:
        raise HTTPException(status_code=403, detail="无权访问")

    from app.models.knowledge import UserFavorite, Knowledge

    total = db.query(UserFavorite).filter(UserFavorite.user_id == user_id).count()
    favorites = db.query(UserFavorite).filter(
        UserFavorite.user_id == user_id
    ).order_by(UserFavorite.created_at.desc()).offset((page - 1) * page_size).limit(page_size).all()

    items = []
    for f in favorites:
        knowledge = db.query(Knowledge).filter(Knowledge.id == f.knowledge_id).first()
        if knowledge:
            items.append({
                "id": f.id,
                "knowledge_id": f.knowledge_id,
                "title": knowledge.title,
                "summary": knowledge.summary,
                "category": knowledge.category,
                "category_name": knowledge.category,
                "file_type": knowledge.file_type,
                "favorited_at": f.created_at
            })

    return {"items": items, "total": total, "page": page, "page_size": page_size}


@router.delete("/{user_id}/favorites/{knowledge_id}")
def delete_user_favorite(
    user_id: str,
    knowledge_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """取消收藏"""
    is_admin = current_user.is_superuser == 1
    if not is_admin and str(current_user.id) != user_id:
        raise HTTPException(status_code=403, detail="无权访问")

    from app.models.knowledge import UserFavorite

    favorite = db.query(UserFavorite).filter(
        UserFavorite.user_id == user_id,
        UserFavorite.knowledge_id == knowledge_id
    ).first()

    if not favorite:
        raise HTTPException(status_code=404, detail="收藏不存在")

    db.delete(favorite)
    db.commit()
    return {"message": "已取消收藏"}


@router.get("/{user_id}/comments")
def list_user_comments(
    user_id: str,
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取用户评论列表"""
    is_admin = current_user.is_superuser == 1
    if not is_admin and str(current_user.id) != user_id:
        raise HTTPException(status_code=403, detail="无权访问")

    from app.models.knowledge import KnowledgeComment, Knowledge

    total = db.query(KnowledgeComment).filter(KnowledgeComment.user_id == user_id).count()
    comments = db.query(KnowledgeComment).filter(
        KnowledgeComment.user_id == user_id
    ).order_by(KnowledgeComment.created_at.desc()).offset((page - 1) * page_size).limit(page_size).all()

    items = []
    for c in comments:
        knowledge = db.query(Knowledge).filter(Knowledge.id == c.knowledge_id).first()
        items.append({
            "id": c.id,
            "knowledge_id": c.knowledge_id,
            "knowledge_title": knowledge.title if knowledge else "未知",
            "content": c.content,
            "created_at": c.created_at
        })

    return {"items": items, "total": total, "page": page, "page_size": page_size}


@router.delete("/{user_id}/comments/{comment_id}")
def delete_user_comment(
    user_id: str,
    comment_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """删除评论"""
    is_admin = current_user.is_superuser == 1
    if not is_admin and str(current_user.id) != user_id:
        raise HTTPException(status_code=403, detail="无权访问")

    from app.models.knowledge import KnowledgeComment

    comment = db.query(KnowledgeComment).filter(
        KnowledgeComment.id == comment_id,
        KnowledgeComment.user_id == user_id
    ).first()

    if not comment:
        raise HTTPException(status_code=404, detail="评论不存在")

    db.delete(comment)
    db.commit()
    return {"message": "评论已删除"}
