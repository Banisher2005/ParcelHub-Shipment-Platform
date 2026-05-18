"""
Shipment service — core business logic for shipments.
"""

import math

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.logging import get_logger
from app.models import Carrier, CarrierType, Shipment, ShipmentStatus, TrackingSource
from app.providers import get_tracking_provider
from app.repositories import ShipmentRepository
from app.schemas import (
    PaginatedResponse,
    ShipmentCreate,
    ShipmentDetailResponse,
    ShipmentResponse,
    ShipmentStatsResponse,
    ShipmentUpdate,
)
from app.services.carrier_service import CarrierService
from app.services.tracking_service import TrackingService

logger = get_logger("services.shipment")


class ShipmentService:
    """
    Core business logic for shipment CRUD and tracking orchestration.
    This is the primary service the API routes interact with.
    """

    def __init__(self, session: AsyncSession):
        self.session = session
        self.repo = ShipmentRepository(session)
        self.carrier_service = CarrierService(session)
        self.tracking_service = TrackingService(session)

    async def create_shipment(self, data: ShipmentCreate) -> ShipmentDetailResponse:
        """
        Create a new shipment. Handles both API-trackable and manual carriers.

        Flow:
        1. Detect or lookup carrier
        2. Determine tracking source (API vs manual)
        3. Create shipment record
        4. For API carriers: register with provider + fetch initial events
        5. For manual carriers: create initial event with provided status
        """
        carrier: Carrier | None = None
        tracking_source = TrackingSource.MANUAL.value
        provider_carrier_code: int | None = None

        # If carrier_code provided, look it up
        if data.carrier_code:
            carrier = await self.carrier_service.get_by_code(data.carrier_code)

        # If no carrier specified, try auto-detection
        if not carrier:
            detection = await self.carrier_service.detect_carrier(
                data.tracking_number
            )
            if detection["detected"] and detection["carrier"]:
                carrier = detection["carrier"]

        # Determine tracking source and carrier details
        if carrier:
            if carrier.carrier_type == CarrierType.API_TRACKABLE.value:
                tracking_source = TrackingSource.API.value
                provider_codes = carrier.provider_codes or {}
                provider_carrier_code = provider_codes.get("17track")
            carrier_code = carrier.code
            carrier_name = carrier.name
        else:
            # Unknown carrier — treat as manual
            carrier_code = data.carrier_code or "other"
            carrier_name = data.carrier_code or "Other"

        # Check for duplicates
        if await self.repo.exists(data.tracking_number, carrier_code):
            raise ValueError(
                f"Shipment with tracking number {data.tracking_number} "
                f"and carrier {carrier_code} already exists"
            )

        # Create shipment
        initial_status = data.status or ShipmentStatus.ORDERED.value
        shipment = Shipment(
            tracking_number=data.tracking_number,
            carrier_code=carrier_code,
            carrier_name=carrier_name,
            title=data.title,
            status=initial_status,
            tracking_source=tracking_source,
            provider_carrier_code=provider_carrier_code,
        )
        shipment = await self.repo.create(shipment)

        # For API carriers: register and fetch initial tracking
        if tracking_source == TrackingSource.API.value:
            provider = get_tracking_provider()
            await provider.register_tracking(
                tracking_number=data.tracking_number,
                carrier_code=provider_carrier_code,
            )
            # Fetch initial tracking data
            shipment = await self.tracking_service.refresh_shipment(shipment)

        # For manual carriers: create initial event
        if tracking_source == TrackingSource.MANUAL.value:
            await self.tracking_service.manual_status_update(
                shipment=shipment,
                status=initial_status,
                description=f"Shipment added — tracking via {carrier_name}",
            )

        # Reload with events
        shipment = await self.repo.get_by_id(shipment.id)

        logger.info(
            f"Created shipment {shipment.tracking_number} "
            f"[{carrier_name}, {tracking_source}]"
        )

        return ShipmentDetailResponse.model_validate(shipment)

    async def get_shipment(self, shipment_id: str) -> ShipmentDetailResponse | None:
        """Get shipment detail with events."""
        shipment = await self.repo.get_by_id(shipment_id)
        if not shipment:
            return None
        return ShipmentDetailResponse.model_validate(shipment)

    async def list_shipments(
        self,
        page: int = 1,
        page_size: int = 20,
        status: str | None = None,
        carrier_code: str | None = None,
        tracking_source: str | None = None,
        search: str | None = None,
    ) -> PaginatedResponse:
        """Get paginated shipment list."""
        shipments, total = await self.repo.get_list(
            page=page,
            page_size=page_size,
            status=status,
            carrier_code=carrier_code,
            tracking_source=tracking_source,
            search=search,
        )

        return PaginatedResponse(
            items=[ShipmentResponse.model_validate(s) for s in shipments],
            total=total,
            page=page,
            page_size=page_size,
            total_pages=math.ceil(total / page_size) if total > 0 else 0,
        )

    async def update_shipment(
        self, shipment_id: str, data: ShipmentUpdate
    ) -> ShipmentDetailResponse | None:
        """Update shipment metadata (title, archive status)."""
        update_data = data.model_dump(exclude_none=True)
        if not update_data:
            return await self.get_shipment(shipment_id)

        shipment = await self.repo.update(shipment_id, **update_data)
        if not shipment:
            return None
        return ShipmentDetailResponse.model_validate(shipment)

    async def archive_shipment(self, shipment_id: str) -> bool:
        """Soft-delete a shipment."""
        return await self.repo.archive(shipment_id)

    async def get_stats(self) -> ShipmentStatsResponse:
        """Get dashboard statistics."""
        stats = await self.repo.get_stats()
        return ShipmentStatsResponse(**stats)
