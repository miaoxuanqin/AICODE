from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status, Header
from sqlalchemy.orm import Session
from typing import Optional

from app.database import get_db
from app.schemas.user import LoginRequest, TokenResponse
from app.services.auth_service import AuthService
from app.utils.jwt import create_access_token, add_token_to_blacklist
from core.rbac import get_current_user
from app.models.user import User
from app.config import get_settings

router = APIRouter(prefix="/auth", tags=["认证"])
settings = get_settings()


@router.post("/login", response_model=TokenResponse)
def login(request: LoginRequest, db: Session = Depends(get_db)):
    """用户登录"""
    auth_service = AuthService(db)
    user = auth_service.authenticate_user(request.username, request.password)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误"
        )

    access_token = create_access_token(
        user_id=user.id,
        expires_delta=timedelta(minutes=settings.jwt_access_token_expire_minutes)
    )

    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        expires_in=settings.jwt_access_token_expire_minutes * 60
    )


@router.post("/logout")
def logout(
    authorization: Optional[str] = Header(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """用户登出"""
    if authorization and authorization.startswith("Bearer "):
        token = authorization[7:]
        add_token_to_blacklist(token, timedelta(minutes=settings.jwt_access_token_expire_minutes))

    return {"message": "登出成功"}


@router.get("/me")
def get_current_user_info(current_user: User = Depends(get_current_user)):
    """获取当前用户信息"""
    return {
        "id": current_user.id,
        "username": current_user.username,
        "email": current_user.email,
        "full_name": current_user.full_name,
        "org_id": current_user.org_id,
        "is_superuser": current_user.is_superuser
    }
