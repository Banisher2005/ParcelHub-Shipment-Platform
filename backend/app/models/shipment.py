"""
Shipment ORM model.
"""

import uuid
from datetime import datetime
from enum import Enum

from sqlalchemy import JSON, Boolean, DateTime, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class ShipmentStatus(str, Enum):
    """Universal shipment status, normalized across all carriers."""
    ORDERED = "ordered"
    PICKED_UP = "picked_up"
    IN_TRANSIT = "in_transit"
    CUSTOMS = "customs"
    OUT_FOR_DELIVERY = "out_for_delivery"
    DELIVERED = "delivered"
    DELAYED = "delayed"
    EXCEPTION = "exception"
    UNKNOWN = "unknown"


class TrackingSource(str, Enum):
    """How this shipment's tracking data is obtained."""
    API = "api"              # Auto-tracked via provider (17TRACK, etc.)
    MANUAL = "manual"        # User manually updates status
    EMAIL = "email"          # Parsed from email (future)
    EXTENSION = "extension"  # Scraped via browser extension (future)


class Shipment(Base):
    """
    Core shipment entity. Represents a single package being tracked.

    Supports both API-trackable carriers (auto-refresh via providers)
    and manual-only carriers (user updates status directly).
    """
    __tablename__ = "shipments"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    tracking_number: Mapped[str] = mapped_column(String(100), index=True)
    carrier_code: Mapped[str] = mapped_column(String(50), index=True)
    carrier_name: Mapped[str] = mapped_column(String(100))
    title: Mapped[str | None] = mapped_column(String(200), nullable=True)
    status: Mapped[str] = mapped_column(
        String(30), default=ShipmentStatus.UNKNOWN.value, index=True
    )
    tracking_source: Mapped[str] = mapped_column(
        String(20), default=TrackingSource.API.value, index=True
    )

    # Location & delivery
    origin: Mapped[str | None] = mapped_column(String(200), nullable=True)
    destination: Mapped[str | None] = mapped_column(String(200), nullable=True)
    estimated_delivery: Mapped[datetime | None] = mapped_column(
        DateTime, nullable=True
    )

    # Last known event (denormalized for fast list queries)
    last_event_at: Mapped[datetime | None] = mapped_column(
        DateTime, nullable=True
    )
    last_event_description: Mapped[str | None] = mapped_column(
        Text, nullable=True
    )

    # Provider-specific data
    provider_carrier_code: Mapped[int | None] = mapped_column(
        Integer, nullable=True
    )
    raw_provider_data: Mapped[dict | None] = mapped_column(
        JSON, nullable=True
    )

    # Multi-user support (future)
    user_id: Mapped[str | None] = mapped_column(
        String(36), nullable=True, index=True
    )

    # Soft delete
    is_archived: Mapped[bool] = mapped_column(Boolean, default=False)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now()
    )

    # Relationships
    events: Mapped[list["TrackingEvent"]] = relationship(
        "TrackingEvent",
        back_populates="shipment",
        cascade="all, delete-orphan",
        order_by="TrackingEvent.timestamp.desc()",
        lazy="selectin",
    )

    def __repr__(self) -> str:
        return f"<Shipment {self.tracking_number} [{self.status}]>"


# Import here to avoid circular import issues with relationship
from app.models.tracking_event import TrackingEvent  # noqa: E402, F401
