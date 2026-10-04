from fastapi import APIRouter

from app.routers import ask, documents, user_routes

api_router = APIRouter()
api_router.include_router(documents.router)
api_router.include_router(ask.router)
api_router.include_router(user_routes.router)
