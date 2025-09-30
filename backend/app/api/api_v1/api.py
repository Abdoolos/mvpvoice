"""
API v1 router that includes all endpoint routers.
Designer: Abdullah Alawiss
"""

from fastapi import APIRouter

from .endpoints import calls, upload, analysis, health

api_router = APIRouter()

# Include all endpoint routers
api_router.include_router(calls.router, prefix="/calls", tags=["calls"])
api_router.include_router(upload.router, prefix="/upload", tags=["upload"])
api_router.include_router(analysis.router, prefix="/analysis", tags=["analysis"])
api_router.include_router(health.router, prefix="/health", tags=["health"])
