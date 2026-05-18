"""
Tracking event DTOs.
"""

from datetime import datetime

from pydantic import BaseModel, Field


class TrackingEventResponse(BaseModel):
    """Tracking event in API responses."""
    id: str
    shipment_id: str
    status: str
    description: str
    location: str | None = None
    timestamp: datetime
    raw_status: str | None = None
    provider_code: str | None = None
    created_at: datetime

    model_config = {"from_attributes": True}


class ManualStatusUpdate(BaseModel):
    """Request body for manual status update."""
    status: str = Field(..., description="New status (must be valid ShipmentStatus)")
    description: str = Field(
        default="", description="Optional description for the status change"
    )
    location: str | None = Field(
        default=None, description="Optional location for the event"
    )
