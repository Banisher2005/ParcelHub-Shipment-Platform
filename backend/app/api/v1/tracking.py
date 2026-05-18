"""
Tracking API routes.
"""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_async_session
from app.schemas import SuccessResponse
from app.services import TrackingService

router = APIRouter(prefix="/tracking", tags=["tracking"])


@router.post("/refresh-all", response_model=SuccessResponse)
async def refresh_all(
    session: AsyncSession = Depends(get_async_session),
):
    """
    Refresh tracking data for all active API-trackable shipments.
    Manual shipments are excluded from refresh.
    """
    service = TrackingService(session)
    count = await service.refresh_all_active()
    return SuccessResponse(message=f"Refreshed {count} shipments")
