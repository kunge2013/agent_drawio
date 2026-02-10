"""API v1 routes configuration."""
from fastapi import APIRouter
from app.api.v1.endpoints import health, chat, export

api_router = APIRouter()

# Health check endpoint
api_router.include_router(health.router, tags=["health"])

# Chat endpoints
api_router.include_router(chat.router, prefix="/chat", tags=["chat"])

# Export endpoints
api_router.include_router(export.router, prefix="/export", tags=["export"])
