"""Models package. Import all models so they register with Base.metadata."""

from app.models.shipment import Shipment, ShipmentStatus, TrackingSource
from app.models.tracking_event import TrackingEvent
from app.models.carrier import Carrier, CarrierType
from app.models.user import User

__all__ = [
    "Shipment",
    "ShipmentStatus",
    "TrackingSource",
    "TrackingEvent",
    "Carrier",
    "CarrierType",
    "User",
]
