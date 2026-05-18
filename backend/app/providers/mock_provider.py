"""
Mock tracking provider for development and testing.

Generates realistic tracking data without calling any external API.
Enables full frontend/backend development without API keys and
serves as demo mode for portfolio presentations.
"""

import hashlib
import random
from datetime import datetime, timedelta

from app.models import ShipmentStatus
from app.providers.base import (
    CarrierMatch,
    NormalizedEvent,
    RegistrationResult,
    TrackingProvider,
    TrackingResult,
)

# Realistic carrier data for mock responses
MOCK_CARRIERS = {
    "delhivery": {"name": "Delhivery", "code": 190011, "country": "IN"},
    "bluedart": {"name": "BlueDart", "code": 190023, "country": "IN"},
    "india_post": {"name": "India Post", "code": 190072, "country": "IN"},
    "dhl": {"name": "DHL", "code": 100002, "country": None},
    "fedex": {"name": "FedEx", "code": 100003, "country": None},
    "ups": {"name": "UPS", "code": 100001, "country": None},
    "yunexpress": {"name": "YunExpress", "code": 190275, "country": "CN"},
    "cainiao": {"name": "Cainiao", "code": 190271, "country": "CN"},
    "yanwen": {"name": "Yanwen", "code": 190012, "country": "CN"},
    "4px": {"name": "4PX", "code": 190233, "country": "CN"},
}

# Realistic event templates per status
EVENT_TEMPLATES: dict[str, list[dict]] = {
    ShipmentStatus.ORDERED.value: [
        {"desc": "Shipment information received", "loc": "Seller Warehouse"},
        {"desc": "Label created, awaiting pickup", "loc": "Origin Facility"},
        {"desc": "Order confirmed, preparing for dispatch", "loc": None},
    ],
    ShipmentStatus.PICKED_UP.value: [
        {"desc": "Package picked up by courier", "loc": "Origin City"},
        {"desc": "Collected from sender", "loc": "Local Hub"},
        {"desc": "Shipment picked up", "loc": "Pickup Point"},
    ],
    ShipmentStatus.IN_TRANSIT.value: [
        {"desc": "Departed from origin facility", "loc": "Origin Sort Center"},
        {"desc": "In transit to destination", "loc": "Regional Hub"},
        {"desc": "Arrived at sorting center", "loc": "Transit Hub"},
        {"desc": "Package is being processed", "loc": "Distribution Center"},
        {"desc": "Departed transit facility", "loc": "City Hub"},
        {"desc": "Arrived at destination city", "loc": "Destination City"},
    ],
    ShipmentStatus.CUSTOMS.value: [
        {"desc": "Arrived at customs", "loc": "International Gateway"},
        {"desc": "Customs clearance in progress", "loc": "Customs Facility"},
        {"desc": "Released from customs", "loc": "Customs Office"},
    ],
    ShipmentStatus.OUT_FOR_DELIVERY.value: [
        {"desc": "Out for delivery", "loc": "Local Delivery Hub"},
        {"desc": "With delivery courier", "loc": "Last Mile Center"},
    ],
    ShipmentStatus.DELIVERED.value: [
        {"desc": "Delivered — signed by recipient", "loc": "Delivery Address"},
        {"desc": "Delivered successfully", "loc": "Destination"},
        {"desc": "Package delivered to mailbox", "loc": "Recipient Address"},
    ],
    ShipmentStatus.DELAYED.value: [
        {"desc": "Delivery delayed — weather conditions", "loc": "Transit Hub"},
        {"desc": "Shipment rescheduled", "loc": "Local Hub"},
    ],
}

# Realistic tracking scenarios
SCENARIOS = [
    # (final_status, statuses_in_order)
    (ShipmentStatus.DELIVERED.value, ["ordered", "picked_up", "in_transit", "in_transit", "in_transit", "out_for_delivery", "delivered"]),
    (ShipmentStatus.IN_TRANSIT.value, ["ordered", "picked_up", "in_transit", "in_transit"]),
    (ShipmentStatus.OUT_FOR_DELIVERY.value, ["ordered", "picked_up", "in_transit", "in_transit", "out_for_delivery"]),
    (ShipmentStatus.ORDERED.value, ["ordered"]),
    (ShipmentStatus.CUSTOMS.value, ["ordered", "picked_up", "in_transit", "customs"]),
    (ShipmentStatus.DELAYED.value, ["ordered", "picked_up", "in_transit", "delayed"]),
    (ShipmentStatus.PICKED_UP.value, ["ordered", "picked_up"]),
]


def _tracking_hash(tracking_number: str) -> int:
    """Deterministic hash for consistent mock data per tracking number."""
    return int(hashlib.md5(tracking_number.encode()).hexdigest(), 16)


class MockTrackingProvider(TrackingProvider):
    """
    Mock provider that generates realistic tracking data.
    Data is deterministic per tracking number (same number → same events).
    """

    @property
    def provider_name(self) -> str:
        return "mock"

    async def register_tracking(
        self, tracking_number: str, carrier_code: int | None = None
    ) -> RegistrationResult:
        return RegistrationResult(
            success=True,
            tracking_number=tracking_number,
        )

    async def get_tracking_info(
        self, tracking_number: str, carrier_code: int | None = None
    ) -> TrackingResult:
        h = _tracking_hash(tracking_number)
        random.seed(h)

        # Pick a scenario deterministically
        scenario = SCENARIOS[h % len(SCENARIOS)]
        final_status, status_sequence = scenario

        # Pick a carrier
        carrier_codes = list(MOCK_CARRIERS.keys())
        carrier_key = carrier_codes[h % len(carrier_codes)]
        carrier = MOCK_CARRIERS[carrier_key]

        # Generate events
        events: list[NormalizedEvent] = []
        base_time = datetime.utcnow() - timedelta(
            days=len(status_sequence) * 1.5
        )

        for i, status in enumerate(status_sequence):
            templates = EVENT_TEMPLATES.get(status, [{"desc": f"Status: {status}", "loc": None}])
            template = templates[h % len(templates)]

            event_time = base_time + timedelta(
                days=i * 1.2, hours=random.randint(0, 12)
            )

            events.append(
                NormalizedEvent(
                    status=status,
                    description=template["desc"],
                    location=template["loc"],
                    timestamp=event_time,
                    raw_status=f"mock_{status}",
                )
            )

        # Determine origin/destination
        origins = ["Mumbai, IN", "Shanghai, CN", "Shenzhen, CN", "Delhi, IN", "Memphis, US"]
        destinations = ["Bangalore, IN", "New Delhi, IN", "Mumbai, IN", "Hyderabad, IN", "Chennai, IN"]

        return TrackingResult(
            success=True,
            tracking_number=tracking_number,
            carrier_code=carrier_key,
            carrier_name=carrier["name"],
            events=events,
            origin=origins[h % len(origins)],
            destination=destinations[h % len(destinations)],
            estimated_delivery=(
                datetime.utcnow() + timedelta(days=random.randint(1, 5))
                if final_status != ShipmentStatus.DELIVERED.value
                else None
            ),
            raw_data={"provider": "mock", "scenario": final_status},
        )

    async def detect_carrier(
        self, tracking_number: str
    ) -> list[CarrierMatch]:
        h = _tracking_hash(tracking_number)
        carrier_codes = list(MOCK_CARRIERS.keys())
        carrier_key = carrier_codes[h % len(carrier_codes)]
        carrier = MOCK_CARRIERS[carrier_key]

        return [
            CarrierMatch(
                carrier_code=carrier_key,
                carrier_name=carrier["name"],
                provider_carrier_code=carrier["code"],
                confidence=0.95,
            )
        ]
