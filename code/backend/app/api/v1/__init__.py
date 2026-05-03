from fastapi import APIRouter
from app.api.v1 import auth, users, roles, knowledge, qa, graph, category

api_router = APIRouter(prefix="/api/v1")

api_router.include_router(auth.router)
api_router.include_router(users.router)
api_router.include_router(roles.router)
api_router.include_router(roles.permission_router)
api_router.include_router(knowledge.router)
api_router.include_router(qa.router)
api_router.include_router(graph.router)
api_router.include_router(category.router)
