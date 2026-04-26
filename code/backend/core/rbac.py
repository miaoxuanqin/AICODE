from typing import Optional, List
from fastapi import HTTPException, status, Depends, Header
from sqlalchemy.orm import Session
from app.database import get_db
from app.services.auth_service import AuthService, get_current_user as _get_current_user
from app.utils.jwt import decode_token, is_token_blacklisted
from app.models.user import User


def get_current_user(
    authorization: Optional[str] = Header(None),
    db: Session = Depends(get_db)
) -> User:
    """获取当前登录用户"""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="未提供认证令牌"
        )

    token = authorization[7:]

    # 检查黑名单
    if is_token_blacklisted(token):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="令牌已失效"
        )

    # 解码token
    payload = decode_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="令牌无效"
        )

    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="令牌无效"
        )

    user = _get_current_user(db, token)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户不存在"
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="用户已被禁用"
        )

    return user


def require_permissions(required_permissions: List[str]):
    """权限检查依赖"""
    def dependency(
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
    ) -> User:
        # 超级管理员拥有所有权限
        if current_user.is_superuser:
            return current_user

        # 获取用户权限
        auth_service = AuthService(db)
        user_permissions = auth_service.get_user_permissions(current_user.id)

        # 检查是否有需要的权限
        for perm in required_permissions:
            if perm not in user_permissions:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"缺少权限: {perm}"
                )

        return current_user

    return dependency
