"""
Carrier DTOs.
"""

from datetime import datetime

from pydantic import BaseModel


class CarrierResponse(BaseModel):
    """Carrier in API responses."""
    id: str
    code: str
    name: str
    carrier_type: str
    country: str | None = None
    tracking_url_template: str | None = None
    logo_url: str | None = None
    is_active: bool

    model_config = {"from_attributes": True}


class CarrierDetectRequest(BaseModel):
    """Request body for carrier detection."""
    tracking_number: str


class CarrierDetectResponse(BaseModel):
    """Response for carrier detection."""
    detected: bool
    carrier: CarrierResponse | None = None
    confidence: float = 0.0
    suggestions: list[CarrierResponse] = []
