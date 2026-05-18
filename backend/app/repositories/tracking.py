"""
Tracking event repository — data access layer for tracking events.
"""

from datetime import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import TrackingEvent


class TrackingRepository:
    """Encapsulates all tracking event database queries."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, event: TrackingEvent) -> TrackingEvent:
        """Insert a new tracking event."""
        self.session.add(event)
        await self.session.commit()
        await self.session.refresh(event)
        return event

    async def create_many(self, events: list[TrackingEvent]) -> list[TrackingEvent]:
        """Insert multiple tracking events."""
        self.session.add_all(events)
        await self.session.commit()
        for event in events:
            await self.session.refresh(event)
        return events

    async def get_by_shipment(
        self, shipment_id: str
    ) -> list[TrackingEvent]:
        """Get all events for a shipment, newest first."""
        stmt = (
            select(TrackingEvent)
            .where(TrackingEvent.shipment_id == shipment_id)
            .order_by(TrackingEvent.timestamp.desc())
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def event_exists(
        self,
        shipment_id: str,
        timestamp: datetime,
        description: str,
    ) -> bool:
        """
        Check if an event already exists (dedup by timestamp + description).
        Prevents duplicate events from multiple provider polls.
        """
        stmt = select(TrackingEvent).where(
            TrackingEvent.shipment_id == shipment_id,
            TrackingEvent.timestamp == timestamp,
            TrackingEvent.description == description,
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none() is not None
