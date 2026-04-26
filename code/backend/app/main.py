from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1 import api_router
from app.config import get_settings

settings = get_settings()

app = FastAPI(
    title="海南省住建知识库 API",
    description="行业知识图谱模块后端服务",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API路由
app.include_router(api_router)


@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.get("/")
def root():
    return {
        "name": "海南省住建知识库 API",
        "version": "1.0.0",
        "docs": "/docs"
    }
