"""
TrackingEvent ORM model.
"""

import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class TrackingEvent(Base):
    """
    A single tracking event in a shipment's lifecycle.

    Events are normalized from provider-specific formats into
    our universal schema. The raw_status field retains the
    original provider status for debugging.
    """
    __tablename__ = "tracking_events"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    shipment_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("shipments.id", ondelete="CASCADE"), index=True
    )
    status: Mapped[str] = mapped_column(String(30), index=True)
    description: Mapped[str] = mapped_column(Text)
    location: Mapped[str | None] = mapped_column(String(300), nullable=True)
    timestamp: Mapped[datetime] = mapped_column(DateTime, index=True)

    # Original provider data (for debugging / future re-normalization)
    raw_status: Mapped[str | None] = mapped_column(String(100), nullable=True)
    provider_code: Mapped[str | None] = mapped_column(
        String(30), nullable=True
    )

    # When we ingested this event
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now()
    )

    # Relationships
    shipment: Mapped["Shipment"] = relationship(
        "Shipment", back_populates="events"
    )

    def __repr__(self) -> str:
        return f"<TrackingEvent {self.status} @ {self.timestamp}>"


from app.models.shipment import Shipment  # noqa: E402, F401
