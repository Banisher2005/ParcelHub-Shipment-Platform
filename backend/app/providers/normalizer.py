"""
Event normalizer — maps provider-specific status codes/strings
to our universal ShipmentStatus enum.

This is the ONLY place where provider-specific logic leaks
into our domain. Everything upstream and downstream speaks
our universal status language.
"""

from app.models import ShipmentStatus

# ──────────────────────────────────────────────
# 17TRACK status mapping
# 17TRACK uses numeric status codes:
#   0 = NotFound, 10 = InfoReceived, 20 = InTransit,
#   30 = Expired, 35 = AvailableForPickup, 40 = OutForDelivery,
#   50 = DeliveryFailure, 60 = Delivered, 70 = Exception
# Sub-statuses add more detail but we normalize to our 7+2 statuses.
# ──────────────────────────────────────────────

SEVENTEEN_TRACK_STATUS_MAP: dict[int, ShipmentStatus] = {
    0: ShipmentStatus.UNKNOWN,        # NotFound
    10: ShipmentStatus.ORDERED,       # InfoReceived
    20: ShipmentStatus.IN_TRANSIT,    # InTransit
    30: ShipmentStatus.DELAYED,       # Expired
    35: ShipmentStatus.OUT_FOR_DELIVERY,  # AvailableForPickup
    40: ShipmentStatus.OUT_FOR_DELIVERY,  # OutForDelivery
    50: ShipmentStatus.EXCEPTION,     # DeliveryFailure
    60: ShipmentStatus.DELIVERED,     # Delivered
    70: ShipmentStatus.EXCEPTION,     # Exception
}

# Keywords in event descriptions that hint at specific statuses.
# Used as a fallback when the provider's status code is ambiguous.
KEYWORD_STATUS_MAP: list[tuple[list[str], ShipmentStatus]] = [
    (["delivered", "delivery confirmed"], ShipmentStatus.DELIVERED),
    (["out for delivery", "with delivery courier"], ShipmentStatus.OUT_FOR_DELIVERY),
    (["customs", "held by customs", "clearance"], ShipmentStatus.CUSTOMS),
    (["picked up", "collected", "pickup"], ShipmentStatus.PICKED_UP),
    (["delayed", "delay", "rescheduled"], ShipmentStatus.DELAYED),
    (["exception", "failed", "returned", "undeliverable"], ShipmentStatus.EXCEPTION),
    (["in transit", "departed", "arrived", "processing", "en route", "hub"], ShipmentStatus.IN_TRANSIT),
    (["order placed", "shipment info received", "label created"], ShipmentStatus.ORDERED),
]


def normalize_17track_status(status_code: int) -> ShipmentStatus:
    """Map a 17TRACK numeric status to our universal status."""
    return SEVENTEEN_TRACK_STATUS_MAP.get(status_code, ShipmentStatus.UNKNOWN)


def normalize_status_from_description(description: str) -> ShipmentStatus:
    """
    Fallback: infer status from event description text.
    Useful for providers that don't give clean status codes.
    """
    desc_lower = description.lower()
    for keywords, status in KEYWORD_STATUS_MAP:
        if any(kw in desc_lower for kw in keywords):
            return status
    return ShipmentStatus.IN_TRANSIT  # Safe default for ambiguous events
