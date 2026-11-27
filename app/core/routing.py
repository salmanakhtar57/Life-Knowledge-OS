from fastapi import APIRouter

from app.routers import ask, documents, user_routes, stats, posts, suggestions
from app.services import sources

# Each router sets its own prefix (/documents, /ask, /auth), so none is added here.
api_router = APIRouter()

api_router.include_router(documents.router)
api_router.include_router(ask.router)
api_router.include_router(user_routes.router)
api_router.include_router(sources.router)
api_router.include_router(posts.router)
api_router.include_router(stats.router)
api_router.include_router(suggestions.router)