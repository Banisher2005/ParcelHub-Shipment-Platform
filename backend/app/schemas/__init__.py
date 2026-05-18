"""Schemas package."""

from app.schemas.common import (
    PaginationParams,
    PaginatedResponse,
    ErrorResponse,
    SuccessResponse,
)
from app.schemas.shipment import (
    ShipmentCreate,
    ShipmentUpdate,
    ShipmentResponse,
    ShipmentDetailResponse,
    ShipmentStatsResponse,
)
from app.schemas.tracking import TrackingEventResponse, ManualStatusUpdate
from app.schemas.carrier import (
    CarrierResponse,
    CarrierDetectRequest,
    CarrierDetectResponse,
)

__all__ = [
    "PaginationParams",
    "PaginatedResponse",
    "ErrorResponse",
    "SuccessResponse",
    "ShipmentCreate",
    "ShipmentUpdate",
    "ShipmentResponse",
    "ShipmentDetailResponse",
    "ShipmentStatsResponse",
    "TrackingEventResponse",
    "ManualStatusUpdate",
    "CarrierResponse",
    "CarrierDetectRequest",
    "CarrierDetectResponse",
]
