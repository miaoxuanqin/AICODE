import os
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    # Database
    database_url: str = "mysql://myuser:1@172.20.36.91:3306/mydatabase"

    # Redis
    redis_url: str = "redis://172.20.36.91:6379"

    # JWT
    jwt_secret: str = "your-secret-key-change-in-production"
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_minutes: int = 60 * 24  # 24 hours

    # Elasticsearch
    elasticsearch_url: str = "http://172.20.36.91:9200"

    # Qdrant
    qdrant_url: str = "http://172.20.36.91:6333"

    # MinIO (File Service)
    minio_endpoint: str = "172.20.36.91:9000"
    minio_access_key: str = "minioadmin"
    minio_secret_key: str = "minioadmin123"
    minio_bucket: str = "knowledge"

    # MiniMax (Embedding)
    minimax_api_key: str = ""
    minimax_group_id: str = ""

    # Embedding 服务配置
    embedding_mode: str = "local"  # "local" 或 "minimax"
    embedding_service_url: str = "http://172.20.36.91:8001"

    # Anthropic LLM (MiniMax)
    anthropic_auth_token: str = ""
    anthropic_base_url: str = "https://api.minimaxi.com/anthropic"
    anthropic_default_haiku_model: str = "MiniMax-M2.7"

    class Config:
        env_file = ".env"
        extra = "allow"


@lru_cache()
def get_settings() -> Settings:
    return Settings()
