import redis
from datetime import datetime, timedelta
from jose import jwt, JWTError
from app.config import get_settings

settings = get_settings()

# Redis client for token blacklist
redis_client = redis.from_url(settings.redis_url, decode_responses=True)


def create_access_token(user_id, expires_delta: timedelta = None) -> str:
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.jwt_access_token_expire_minutes)

    to_encode = {
        "sub": str(user_id),
        "exp": expire,
        "iat": datetime.utcnow()
    }
    encoded_jwt = jwt.encode(to_encode, settings.jwt_secret, algorithm=settings.jwt_algorithm)
    return encoded_jwt


def decode_token(token: str) -> dict:
    try:
        payload = jwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_algorithm])
        return payload
    except JWTError:
        return None


def add_token_to_blacklist(token: str, expires_delta: timedelta) -> None:
    """将token加入黑名单"""
    try:
        payload = jwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_algorithm])
        exp = payload.get("exp")
        if exp:
            ttl = exp - int(datetime.utcnow().timestamp())
            if ttl > 0:
                redis_client.setex(f"blacklist:{token}", ttl, "1")
    except JWTError:
        pass


def is_token_blacklisted(token: str) -> bool:
    """检查token是否在黑名单中"""
    return redis_client.exists(f"blacklist:{token}") > 0
