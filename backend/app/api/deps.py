"""
FastAPI dependency injection.
"""

from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_async_session
from app.services import ShipmentService, TrackingService, CarrierService


async def get_shipment_service(
    session: AsyncSession = None,
) -> ShipmentService:
    """Get ShipmentService with a DB session."""
    # This will be called with session from route dependency
    return ShipmentService(session)


async def get_tracking_service(
    session: AsyncSession = None,
) -> TrackingService:
    """Get TrackingService with a DB session."""
    return TrackingService(session)


async def get_carrier_service(
    session: AsyncSession = None,
) -> CarrierService:
    """Get CarrierService with a DB session."""
    return CarrierService(session)
