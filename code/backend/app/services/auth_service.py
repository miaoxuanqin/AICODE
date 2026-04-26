from datetime import datetime
from typing import Optional
from sqlalchemy.orm import Session
from app.models.user import User
from app.models.role import Role, Permission, RolePermission, UserRole
from app.utils.security import verify_password, get_password_hash
from app.utils.jwt import create_access_token, decode_token
from app.config import get_settings

settings = get_settings()


class AuthService:
    def __init__(self, db: Session):
        self.db = db

    def authenticate_user(self, username: str, password: str) -> Optional[User]:
        user = self.db.query(User).filter(User.username == username).first()
        if not user:
            return None
        if not verify_password(password, user.password_hash):
            return None
        if not user.is_active:
            return None
        # 更新最后登录时间
        user.last_login_at = datetime.utcnow()
        self.db.commit()
        return user

    def create_user(self, username: str, password: str, **kwargs) -> User:
        hashed_password = get_password_hash(password)
        user = User(
            username=username,
            password_hash=hashed_password,
            **kwargs
        )
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user

    def get_user_by_id(self, user_id: str) -> Optional[User]:
        return self.db.query(User).filter(User.id == user_id).first()

    def get_user_permissions(self, user_id: str, org_id: str = None) -> list[str]:
        """获取用户的权限编码列表"""
        # 获取用户直接关联的角色
        user_roles_query = self.db.query(UserRole.role_id).filter(
            UserRole.user_id == user_id
        )
        # 如果指定了组织，只获取该组织下有效的角色
        if org_id:
            user_roles_query = user_roles_query.filter(
                (UserRole.org_id == org_id) | (UserRole.org_id == None)
            )
        role_ids = [r[0] for r in user_roles_query.all()]

        if not role_ids:
            return []

        # 获取角色关联的权限
        permissions = self.db.query(Permission.code).join(
            RolePermission, RolePermission.permission_id == Permission.id
        ).filter(
            RolePermission.role_id.in_(role_ids),
            Permission.is_active == True
        ).distinct().all()

        return [p[0] for p in permissions]

    def is_superuser(self, user_id: str) -> bool:
        user = self.get_user_by_id(user_id)
        return user.is_superuser if user else False


def get_current_user(db: Session, token: str = None) -> Optional[User]:
    """从token获取当前用户"""
    if not token:
        return None
    payload = decode_token(token)
    if not payload:
        return None
    user_id = payload.get("sub")
    if not user_id:
        return None
    auth_service = AuthService(db)
    return auth_service.get_user_by_id(user_id)
