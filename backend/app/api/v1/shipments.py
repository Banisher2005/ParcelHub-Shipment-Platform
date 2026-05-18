"""
Shipment API routes — CRUD and tracking operations.
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_async_session
from app.schemas import (
    ManualStatusUpdate,
    PaginatedResponse,
    ShipmentCreate,
    ShipmentDetailResponse,
    ShipmentStatsResponse,
    ShipmentUpdate,
    SuccessResponse,
    TrackingEventResponse,
)
from app.services import ShipmentService, TrackingService

router = APIRouter(prefix="/shipments", tags=["shipments"])


@router.post("", response_model=ShipmentDetailResponse, status_code=201)
async def create_shipment(
    data: ShipmentCreate,
    session: AsyncSession = Depends(get_async_session),
):
    """
    Add a new shipment to track.

    For API-trackable carriers: auto-detects carrier, registers with provider,
    and fetches initial tracking events.

    For manual carriers: creates shipment with initial status event.
    """
    service = ShipmentService(session)
    try:
        return await service.create_shipment(data)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("", response_model=PaginatedResponse)
async def list_shipments(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    status: str | None = Query(default=None),
    carrier_code: str | None = Query(default=None),
    tracking_source: str | None = Query(default=None),
    search: str | None = Query(default=None),
    session: AsyncSession = Depends(get_async_session),
):
    """List shipments with pagination and filters."""
    service = ShipmentService(session)
    return await service.list_shipments(
        page=page,
        page_size=page_size,
        status=status,
        carrier_code=carrier_code,
        tracking_source=tracking_source,
        search=search,
    )


@router.get("/stats", response_model=ShipmentStatsResponse)
async def get_stats(
    session: AsyncSession = Depends(get_async_session),
):
    """Get dashboard statistics (shipment counts by status)."""
    service = ShipmentService(session)
    return await service.get_stats()


@router.get("/{shipment_id}", response_model=ShipmentDetailResponse)
async def get_shipment(
    shipment_id: str,
    session: AsyncSession = Depends(get_async_session),
):
    """Get shipment detail with full event history."""
    service = ShipmentService(session)
    result = await service.get_shipment(shipment_id)
    if not result:
        raise HTTPException(status_code=404, detail="Shipment not found")
    return result


@router.patch("/{shipment_id}", response_model=ShipmentDetailResponse)
async def update_shipment(
    shipment_id: str,
    data: ShipmentUpdate,
    session: AsyncSession = Depends(get_async_session),
):
    """Update shipment metadata (title, archive status)."""
    service = ShipmentService(session)
    result = await service.update_shipment(shipment_id, data)
    if not result:
        raise HTTPException(status_code=404, detail="Shipment not found")
    return result


@router.delete("/{shipment_id}", response_model=SuccessResponse)
async def archive_shipment(
    shipment_id: str,
    session: AsyncSession = Depends(get_async_session),
):
    """Archive (soft-delete) a shipment."""
    service = ShipmentService(session)
    success = await service.archive_shipment(shipment_id)
    if not success:
        raise HTTPException(status_code=404, detail="Shipment not found")
    return SuccessResponse(message="Shipment archived")


@router.post(
    "/{shipment_id}/refresh", response_model=ShipmentDetailResponse
)
async def refresh_shipment(
    shipment_id: str,
    session: AsyncSession = Depends(get_async_session),
):
    """
    Force refresh tracking data for a shipment.
    Only works for API-trackable shipments (returns 400 for manual).
    """
    service = ShipmentService(session)
    shipment_detail = await service.get_shipment(shipment_id)
    if not shipment_detail:
        raise HTTPException(status_code=404, detail="Shipment not found")

    if shipment_detail.tracking_source != "api":
        raise HTTPException(
            status_code=400,
            detail="Cannot refresh manual shipment. Use manual status update instead.",
        )

    from app.repositories import ShipmentRepository

    repo = ShipmentRepository(session)
    shipment = await repo.get_by_id(shipment_id)
    tracking_service = TrackingService(session)
    await tracking_service.refresh_shipment(shipment)

    return await service.get_shipment(shipment_id)


@router.post(
    "/{shipment_id}/status", response_model=TrackingEventResponse
)
async def manual_status_update(
    shipment_id: str,
    data: ManualStatusUpdate,
    session: AsyncSession = Depends(get_async_session),
):
    """
    Manually update shipment status. Creates a new tracking event.
    Primarily for manual-only carriers (Amazon, Flipkart, etc.),
    but also allowed for API carriers as an override.
    """
    from app.repositories import ShipmentRepository

    repo = ShipmentRepository(session)
    shipment = await repo.get_by_id(shipment_id)
    if not shipment:
        raise HTTPException(status_code=404, detail="Shipment not found")

    tracking_service = TrackingService(session)
    try:
        event = await tracking_service.manual_status_update(
            shipment=shipment,
            status=data.status,
            description=data.description,
            location=data.location,
        )
        return TrackingEventResponse.model_validate(event)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
