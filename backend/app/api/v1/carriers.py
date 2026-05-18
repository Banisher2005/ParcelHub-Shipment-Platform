"""
Carrier API routes.
"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_async_session
from app.schemas import CarrierDetectRequest, CarrierDetectResponse, CarrierResponse
from app.services import CarrierService

router = APIRouter(prefix="/carriers", tags=["carriers"])


@router.get("", response_model=list[CarrierResponse])
async def list_carriers(
    carrier_type: str | None = Query(default=None),
    session: AsyncSession = Depends(get_async_session),
):
    """List all supported carriers, optionally filtered by type."""
    service = CarrierService(session)
    carriers = await service.get_all(carrier_type=carrier_type)
    return [CarrierResponse.model_validate(c) for c in carriers]


@router.post("/detect", response_model=CarrierDetectResponse)
async def detect_carrier(
    data: CarrierDetectRequest,
    session: AsyncSession = Depends(get_async_session),
):
    """
    Detect carrier from a tracking number.
    Uses the configured tracking provider for detection.
    """
    service = CarrierService(session)
    result = await service.detect_carrier(data.tracking_number)

    carrier_response = None
    if result["carrier"]:
        carrier_response = CarrierResponse.model_validate(result["carrier"])

    return CarrierDetectResponse(
        detected=result["detected"],
        carrier=carrier_response,
        confidence=result["confidence"],
        suggestions=result.get("suggestions", []),
    )
