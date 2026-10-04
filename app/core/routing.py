# from app.apis.api_v1 import control_panel, user_routes, chat_routes, export_data, appointment
from app.routers import documents
from fastapi import APIRouter

api_router = APIRouter()

api_router.include_router(documents.router, prefix="/documents")