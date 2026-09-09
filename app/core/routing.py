from fastapi import APIRouter

from app.routers import ask, documents

api_router = APIRouter()
api_router.include_router(documents.router)
api_router.include_router(ask.router)
