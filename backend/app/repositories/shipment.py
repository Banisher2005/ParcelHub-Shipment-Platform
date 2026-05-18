"""
Shipment repository — data access layer for shipments.
"""

import math
from datetime import datetime

from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models import Shipment, ShipmentStatus


class ShipmentRepository:
    """Encapsulates all shipment database queries."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, shipment: Shipment) -> Shipment:
        """Insert a new shipment."""
        self.session.add(shipment)
        await self.session.commit()
        await self.session.refresh(shipment)
        return shipment

    async def get_by_id(self, shipment_id: str) -> Shipment | None:
        """Get shipment by ID with events loaded."""
        stmt = (
            select(Shipment)
            .options(selectinload(Shipment.events))
            .where(Shipment.id == shipment_id, Shipment.is_archived == False)  # noqa: E712
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_list(
        self,
        page: int = 1,
        page_size: int = 20,
        status: str | None = None,
        carrier_code: str | None = None,
        tracking_source: str | None = None,
        search: str | None = None,
        include_archived: bool = False,
    ) -> tuple[list[Shipment], int]:
        """
        Get paginated shipment list with optional filters.
        Returns (shipments, total_count).
        """
        stmt = select(Shipment)

        if not include_archived:
            stmt = stmt.where(Shipment.is_archived == False)  # noqa: E712

        if status:
            stmt = stmt.where(Shipment.status == status)
        if carrier_code:
            stmt = stmt.where(Shipment.carrier_code == carrier_code)
        if tracking_source:
            stmt = stmt.where(Shipment.tracking_source == tracking_source)
        if search:
            search_filter = f"%{search}%"
            stmt = stmt.where(
                (Shipment.tracking_number.ilike(search_filter))
                | (Shipment.title.ilike(search_filter))
                | (Shipment.carrier_name.ilike(search_filter))
            )

        # Count total
        count_stmt = select(func.count()).select_from(stmt.subquery())
        total_result = await self.session.execute(count_stmt)
        total = total_result.scalar() or 0

        # Fetch page
        stmt = (
            stmt.order_by(Shipment.updated_at.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
        )
        result = await self.session.execute(stmt)
        shipments = list(result.scalars().all())

        return shipments, total

    async def update(
        self, shipment_id: str, **kwargs
    ) -> Shipment | None:
        """Update shipment fields."""
        kwargs["updated_at"] = datetime.utcnow()
        stmt = (
            update(Shipment)
            .where(Shipment.id == shipment_id)
            .values(**kwargs)
        )
        await self.session.execute(stmt)
        await self.session.commit()
        return await self.get_by_id(shipment_id)

    async def archive(self, shipment_id: str) -> bool:
        """Soft-delete a shipment."""
        stmt = (
            update(Shipment)
            .where(Shipment.id == shipment_id)
            .values(is_archived=True, updated_at=datetime.utcnow())
        )
        result = await self.session.execute(stmt)
        await self.session.commit()
        return result.rowcount > 0

    async def get_active_api_shipments(self) -> list[Shipment]:
        """Get all active API-trackable shipments for polling."""
        non_terminal = [
            ShipmentStatus.ORDERED.value,
            ShipmentStatus.PICKED_UP.value,
            ShipmentStatus.IN_TRANSIT.value,
            ShipmentStatus.CUSTOMS.value,
            ShipmentStatus.OUT_FOR_DELIVERY.value,
            ShipmentStatus.DELAYED.value,
            ShipmentStatus.UNKNOWN.value,
        ]
        stmt = (
            select(Shipment)
            .where(
                Shipment.tracking_source == "api",
                Shipment.is_archived == False,  # noqa: E712
                Shipment.status.in_(non_terminal),
            )
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_stats(self) -> dict[str, int]:
        """Get shipment counts by status."""
        stmt = (
            select(Shipment.status, func.count(Shipment.id))
            .where(Shipment.is_archived == False)  # noqa: E712
            .group_by(Shipment.status)
        )
        result = await self.session.execute(stmt)
        stats = {row[0]: row[1] for row in result.all()}

        # Ensure all statuses are present
        all_statuses = {s.value: 0 for s in ShipmentStatus}
        all_statuses.update(stats)
        all_statuses["total"] = sum(stats.values())

        return all_statuses

    async def exists(self, tracking_number: str, carrier_code: str) -> bool:
        """Check if a shipment with this tracking number + carrier already exists."""
        stmt = select(func.count()).where(
            Shipment.tracking_number == tracking_number,
            Shipment.carrier_code == carrier_code,
            Shipment.is_archived == False,  # noqa: E712
        )
        result = await self.session.execute(stmt)
        return (result.scalar() or 0) > 0
