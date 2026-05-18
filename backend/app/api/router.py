"""
Root API router — aggregates all versioned route modules.
"""

from fastapi import APIRouter

from app.api.v1 import shipments, tracking, carriers

api_router = APIRouter(prefix="/api/v1")

api_router.include_router(shipments.router)
api_router.include_router(tracking.router)
api_router.include_router(carriers.router)
