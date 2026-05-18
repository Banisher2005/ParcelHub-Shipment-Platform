"""
Shipment DTOs for API request/response.
"""

from datetime import datetime

from pydantic import BaseModel, Field

from app.schemas.tracking import TrackingEventResponse


class ShipmentCreate(BaseModel):
    """Request body for creating a new shipment."""
    tracking_number: str = Field(
        ..., min_length=1, max_length=100,
        description="Tracking number or order ID"
    )
    carrier_code: str | None = Field(
        default=None,
        description="Carrier code (auto-detected if not provided)"
    )
    title: str | None = Field(
        default=None, max_length=200,
        description="User-friendly label for this shipment"
    )
    status: str | None = Field(
        default=None,
        description="Initial status (for manual carriers only)"
    )


class ShipmentUpdate(BaseModel):
    """Request body for updating a shipment."""
    title: str | None = None
    is_archived: bool | None = None


class ShipmentResponse(BaseModel):
    """Shipment in API responses (list view, without events)."""
    id: str
    tracking_number: str
    carrier_code: str
    carrier_name: str
    title: str | None = None
    status: str
    tracking_source: str
    origin: str | None = None
    destination: str | None = None
    estimated_delivery: datetime | None = None
    last_event_at: datetime | None = None
    last_event_description: str | None = None
    is_archived: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class ShipmentDetailResponse(ShipmentResponse):
    """Shipment detail with full event history."""
    events: list[TrackingEventResponse] = []


class ShipmentStatsResponse(BaseModel):
    """Dashboard statistics."""
    total: int = 0
    ordered: int = 0
    picked_up: int = 0
    in_transit: int = 0
    customs: int = 0
    out_for_delivery: int = 0
    delivered: int = 0
    delayed: int = 0
    exception: int = 0
