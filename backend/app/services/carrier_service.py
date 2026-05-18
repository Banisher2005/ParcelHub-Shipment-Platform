"""
Carrier service — carrier detection and lookup.
"""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.logging import get_logger
from app.models import Carrier, CarrierType
from app.providers import get_tracking_provider

logger = get_logger("services.carrier")

# ──────────────────────────────────────────────
# Seed data for initial carriers
# ──────────────────────────────────────────────

SEED_CARRIERS = [
    # Tier 1 — API Trackable
    {"code": "delhivery", "name": "Delhivery", "carrier_type": "api_trackable", "country": "IN", "provider_codes": {"17track": 190011}, "tracking_url_template": "https://www.delhivery.com/track/package/{tracking_number}"},
    {"code": "bluedart", "name": "BlueDart", "carrier_type": "api_trackable", "country": "IN", "provider_codes": {"17track": 190023}, "tracking_url_template": "https://www.bluedart.com/tracking/{tracking_number}"},
    {"code": "india_post", "name": "India Post", "carrier_type": "api_trackable", "country": "IN", "provider_codes": {"17track": 190072}, "tracking_url_template": "https://www.indiapost.gov.in/_layouts/15/dop.portal.tracking/trackconsignment.aspx"},
    {"code": "dhl", "name": "DHL", "carrier_type": "api_trackable", "country": None, "provider_codes": {"17track": 100002}, "tracking_url_template": "https://www.dhl.com/en/express/tracking.html?AWB={tracking_number}"},
    {"code": "fedex", "name": "FedEx", "carrier_type": "api_trackable", "country": None, "provider_codes": {"17track": 100003}, "tracking_url_template": "https://www.fedex.com/fedextrack/?trknbr={tracking_number}"},
    {"code": "ups", "name": "UPS", "carrier_type": "api_trackable", "country": None, "provider_codes": {"17track": 100001}, "tracking_url_template": "https://www.ups.com/track?tracknum={tracking_number}"},
    {"code": "yunexpress", "name": "YunExpress", "carrier_type": "api_trackable", "country": "CN", "provider_codes": {"17track": 190275}, "tracking_url_template": "https://www.yunexpress.com/tracking/{tracking_number}"},
    {"code": "cainiao", "name": "Cainiao", "carrier_type": "api_trackable", "country": "CN", "provider_codes": {"17track": 190271}, "tracking_url_template": "https://global.cainiao.com/detail.htm?mailNoList={tracking_number}"},
    {"code": "yanwen", "name": "Yanwen", "carrier_type": "api_trackable", "country": "CN", "provider_codes": {"17track": 190012}, "tracking_url_template": "https://track.yanwen.com/en/{tracking_number}"},
    {"code": "4px", "name": "4PX", "carrier_type": "api_trackable", "country": "CN", "provider_codes": {"17track": 190233}, "tracking_url_template": "https://track.4px.com/#/result/0/{tracking_number}"},
    # Tier 2 — Manual Only
    {"code": "amazon", "name": "Amazon", "carrier_type": "manual_only", "country": None, "provider_codes": {}, "tracking_url_template": "https://www.amazon.in/gp/your-account/order-history"},
    {"code": "flipkart", "name": "Flipkart", "carrier_type": "manual_only", "country": "IN", "provider_codes": {}, "tracking_url_template": "https://www.flipkart.com/account/orders"},
    {"code": "other", "name": "Other", "carrier_type": "manual_only", "country": None, "provider_codes": {}, "tracking_url_template": None},
]


class CarrierService:
    """Business logic for carrier operations."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_all(self, carrier_type: str | None = None) -> list[Carrier]:
        """Get all active carriers, optionally filtered by type."""
        stmt = select(Carrier).where(Carrier.is_active == True)  # noqa: E712
        if carrier_type:
            stmt = stmt.where(Carrier.carrier_type == carrier_type)
        stmt = stmt.order_by(Carrier.name)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_by_code(self, code: str) -> Carrier | None:
        """Get a carrier by its internal code."""
        stmt = select(Carrier).where(Carrier.code == code)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def detect_carrier(self, tracking_number: str) -> dict:
        """
        Detect carrier from tracking number.
        Uses the configured tracking provider for detection.
        Returns detection result with carrier info.
        """
        provider = get_tracking_provider()
        matches = await provider.detect_carrier(tracking_number)

        if not matches:
            return {
                "detected": False,
                "carrier": None,
                "confidence": 0.0,
                "suggestions": [],
            }

        # Try to match provider result to our carrier DB
        best_match = matches[0]
        carrier = await self.get_by_code(best_match.carrier_code)

        # If not found by code, try by provider code
        if not carrier:
            for c in await self.get_all(carrier_type="api_trackable"):
                provider_codes = c.provider_codes or {}
                if provider_codes.get("17track") == best_match.provider_carrier_code:
                    carrier = c
                    break

        return {
            "detected": carrier is not None,
            "carrier": carrier,
            "confidence": best_match.confidence,
            "suggestions": [],
        }

    async def seed_carriers(self) -> int:
        """
        Seed the database with initial carrier data.
        Skips carriers that already exist. Returns count of new carriers.
        """
        count = 0
        for data in SEED_CARRIERS:
            existing = await self.get_by_code(data["code"])
            if existing:
                continue

            carrier = Carrier(
                code=data["code"],
                name=data["name"],
                carrier_type=data["carrier_type"],
                country=data["country"],
                provider_codes=data["provider_codes"],
                tracking_url_template=data.get("tracking_url_template"),
            )
            self.session.add(carrier)
            count += 1

        if count > 0:
            await self.session.commit()
            logger.info(f"Seeded {count} carriers")

        return count
