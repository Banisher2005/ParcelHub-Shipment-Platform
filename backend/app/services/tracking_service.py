"""
Tracking service — orchestrates tracking operations.
"""

from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.logging import get_logger
from app.models import Shipment, ShipmentStatus, TrackingEvent, TrackingSource
from app.providers import get_tracking_provider
from app.repositories import ShipmentRepository, TrackingRepository

logger = get_logger("services.tracking")


class TrackingService:
    """
    Orchestrates tracking operations:
    - Fetching tracking info from providers
    - Normalizing and persisting events
    - Updating shipment status
    - Manual status updates
    """

    def __init__(self, session: AsyncSession):
        self.session = session
        self.shipment_repo = ShipmentRepository(session)
        self.tracking_repo = TrackingRepository(session)

    async def refresh_shipment(self, shipment: Shipment) -> Shipment:
        """
        Refresh tracking data for a single API-trackable shipment.
        Fetches from provider, normalizes events, upserts new ones.
        """
        if shipment.tracking_source != TrackingSource.API.value:
            logger.warning(
                f"Cannot refresh manual shipment {shipment.id}"
            )
            return shipment

        provider = get_tracking_provider()
        result = await provider.get_tracking_info(
            tracking_number=shipment.tracking_number,
            carrier_code=shipment.provider_carrier_code,
        )

        if not result.success:
            logger.warning(
                f"Failed to refresh {shipment.tracking_number}: {result.error}"
            )
            return shipment

        # Upsert new events (dedup by timestamp + description)
        new_events_count = 0
        latest_event = None

        for event_data in result.events:
            exists = await self.tracking_repo.event_exists(
                shipment_id=shipment.id,
                timestamp=event_data.timestamp,
                description=event_data.description,
            )
            if exists:
                continue

            event = TrackingEvent(
                shipment_id=shipment.id,
                status=event_data.status,
                description=event_data.description,
                location=event_data.location,
                timestamp=event_data.timestamp,
                raw_status=event_data.raw_status,
                provider_code=provider.provider_name,
            )
            await self.tracking_repo.create(event)
            new_events_count += 1

            if latest_event is None or event_data.timestamp > latest_event.timestamp:
                latest_event = event_data

        # Update shipment with latest info
        update_data: dict = {
            "raw_provider_data": result.raw_data,
        }

        if latest_event:
            update_data["status"] = latest_event.status
            update_data["last_event_at"] = latest_event.timestamp
            update_data["last_event_description"] = latest_event.description

        if result.origin:
            update_data["origin"] = result.origin
        if result.destination:
            update_data["destination"] = result.destination
        if result.estimated_delivery:
            update_data["estimated_delivery"] = result.estimated_delivery

        updated = await self.shipment_repo.update(shipment.id, **update_data)

        logger.info(
            f"Refreshed {shipment.tracking_number}: "
            f"{new_events_count} new events, status={update_data.get('status', shipment.status)}"
        )

        return updated or shipment

    async def refresh_all_active(self) -> int:
        """
        Refresh all active API-trackable shipments.
        Returns count of shipments refreshed.
        """
        shipments = await self.shipment_repo.get_active_api_shipments()
        logger.info(f"Refreshing {len(shipments)} active shipments")

        refreshed = 0
        for shipment in shipments:
            try:
                await self.refresh_shipment(shipment)
                refreshed += 1
            except Exception as e:
                logger.error(
                    f"Error refreshing {shipment.tracking_number}: {e}"
                )

        return refreshed

    async def manual_status_update(
        self,
        shipment: Shipment,
        status: str,
        description: str = "",
        location: str | None = None,
    ) -> TrackingEvent:
        """
        Create a manual tracking event and update shipment status.
        Used for manual-only carriers (Amazon, Flipkart, etc.)
        """
        # Validate status
        try:
            ShipmentStatus(status)
        except ValueError:
            raise ValueError(f"Invalid status: {status}")

        # Auto-generate description if not provided
        if not description:
            status_labels = {
                "ordered": "Order placed",
                "picked_up": "Package picked up",
                "in_transit": "Package in transit",
                "customs": "At customs",
                "out_for_delivery": "Out for delivery",
                "delivered": "Package delivered",
                "delayed": "Delivery delayed",
                "exception": "Delivery exception",
            }
            description = status_labels.get(status, f"Status updated to {status}")

        # Create event
        event = TrackingEvent(
            shipment_id=shipment.id,
            status=status,
            description=description,
            location=location,
            timestamp=datetime.utcnow(),
            raw_status=f"manual_{status}",
            provider_code="manual",
        )
        await self.tracking_repo.create(event)

        # Update shipment
        await self.shipment_repo.update(
            shipment.id,
            status=status,
            last_event_at=event.timestamp,
            last_event_description=description,
        )

        logger.info(
            f"Manual status update for {shipment.tracking_number}: {status}"
        )

        return event
