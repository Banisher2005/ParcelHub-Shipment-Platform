"""
17TRACK tracking provider implementation.

Integrates with the 17TRACK API v2.2 to register tracking numbers,
fetch tracking info, and detect carriers.

API Docs: https://api.17track.net/en/doc
Auth: 17token header
Rate limit: 3 req/s
"""

import httpx

from app.core.logging import get_logger
from app.providers.base import (
    CarrierMatch,
    NormalizedEvent,
    RegistrationResult,
    TrackingProvider,
    TrackingResult,
)
from app.providers.normalizer import (
    normalize_17track_status,
    normalize_status_from_description,
)
from datetime import datetime

logger = get_logger("providers.17track")

BASE_URL = "https://api.17track.net/track/v2.2"


class SeventeenTrackProvider(TrackingProvider):
    """
    17TRACK API provider.

    Uses the register → gettrackinfo flow.
    Events are normalized through our normalizer layer.
    """

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.client = httpx.AsyncClient(
            base_url=BASE_URL,
            headers={
                "17token": api_key,
                "Content-Type": "application/json",
            },
            timeout=30.0,
        )

    @property
    def provider_name(self) -> str:
        return "17track"

    async def register_tracking(
        self, tracking_number: str, carrier_code: int | None = None
    ) -> RegistrationResult:
        """Register a tracking number with 17TRACK for monitoring."""
        payload = [{"number": tracking_number}]
        if carrier_code:
            payload[0]["carrier"] = carrier_code

        try:
            response = await self.client.post("/register", json=payload)
            data = response.json()

            if data.get("code") == 0 and data.get("data", {}).get("accepted"):
                logger.info(f"Registered tracking: {tracking_number}")
                return RegistrationResult(
                    success=True, tracking_number=tracking_number
                )

            # Check if already registered (not an error)
            rejected = data.get("data", {}).get("rejected", [])
            if rejected and rejected[0].get("error", {}).get("code") == -18019901:
                logger.info(f"Already registered: {tracking_number}")
                return RegistrationResult(
                    success=True, tracking_number=tracking_number
                )

            error_msg = str(rejected[0].get("error", {})) if rejected else str(data)
            logger.warning(f"Registration rejected: {tracking_number} — {error_msg}")
            return RegistrationResult(
                success=False,
                tracking_number=tracking_number,
                error=error_msg,
            )

        except Exception as e:
            logger.error(f"17TRACK registration error: {e}")
            return RegistrationResult(
                success=False,
                tracking_number=tracking_number,
                error=str(e),
            )

    async def get_tracking_info(
        self, tracking_number: str, carrier_code: int | None = None
    ) -> TrackingResult:
        """Fetch and normalize tracking info from 17TRACK."""
        payload = [{"number": tracking_number}]
        if carrier_code:
            payload[0]["carrier"] = carrier_code

        try:
            response = await self.client.post("/gettrackinfo", json=payload)
            data = response.json()

            if data.get("code") != 0:
                return TrackingResult(
                    success=False,
                    tracking_number=tracking_number,
                    error=f"API error: {data.get('code')}",
                    raw_data=data,
                )

            accepted = data.get("data", {}).get("accepted", [])
            if not accepted:
                return TrackingResult(
                    success=False,
                    tracking_number=tracking_number,
                    error="No tracking data found",
                    raw_data=data,
                )

            track_data = accepted[0]
            track_info = track_data.get("track_info", {})

            # Extract events
            events: list[NormalizedEvent] = []
            raw_events = track_info.get("tracking", {}).get("providers", [])

            for provider_data in raw_events:
                for event in provider_data.get("events", []):
                    status_code = event.get("sub_status") or event.get("status", 0)
                    description = event.get("description", "")
                    location = event.get("location", None)
                    time_str = event.get("time_iso", "")

                    # Normalize status
                    if isinstance(status_code, int):
                        normalized_status = normalize_17track_status(status_code)
                    else:
                        normalized_status = normalize_status_from_description(description)

                    # Parse timestamp
                    try:
                        timestamp = datetime.fromisoformat(time_str.replace("Z", "+00:00"))
                    except (ValueError, AttributeError):
                        timestamp = datetime.utcnow()

                    events.append(
                        NormalizedEvent(
                            status=normalized_status.value,
                            description=description,
                            location=location,
                            timestamp=timestamp,
                            raw_status=str(status_code),
                        )
                    )

            # Extract metadata
            latest_status = track_info.get("latest_status", {})
            carrier_info = track_info.get("tracking", {}).get("providers", [{}])[0] if raw_events else {}

            return TrackingResult(
                success=True,
                tracking_number=tracking_number,
                carrier_code=carrier_info.get("carrier", {}).get("key"),
                carrier_name=carrier_info.get("carrier", {}).get("name"),
                events=events,
                origin=track_info.get("shipping_info", {}).get("shipper_address", {}).get("country"),
                destination=track_info.get("shipping_info", {}).get("recipient_address", {}).get("country"),
                raw_data=data,
            )

        except Exception as e:
            logger.error(f"17TRACK fetch error for {tracking_number}: {e}")
            return TrackingResult(
                success=False,
                tracking_number=tracking_number,
                error=str(e),
            )

    async def detect_carrier(
        self, tracking_number: str
    ) -> list[CarrierMatch]:
        """Use 17TRACK to detect carrier from tracking number."""
        try:
            response = await self.client.post(
                "/gettrackinfo",
                json=[{"number": tracking_number}],
            )
            data = response.json()

            accepted = data.get("data", {}).get("accepted", [])
            if not accepted:
                return []

            track_info = accepted[0].get("track_info", {})
            providers = track_info.get("tracking", {}).get("providers", [])

            matches = []
            for p in providers:
                carrier = p.get("carrier", {})
                matches.append(
                    CarrierMatch(
                        carrier_code=carrier.get("key", ""),
                        carrier_name=carrier.get("name", "Unknown"),
                        provider_carrier_code=carrier.get("key"),
                        confidence=0.9,
                    )
                )

            return matches

        except Exception as e:
            logger.error(f"17TRACK carrier detection error: {e}")
            return []

    async def close(self):
        """Close the HTTP client."""
        await self.client.aclose()
