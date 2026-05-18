"""
Carrier ORM model.
"""

import uuid
from datetime import datetime
from enum import Enum

from sqlalchemy import JSON, Boolean, DateTime, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class CarrierType(str, Enum):
    """Classification of carrier tracking capability."""
    API_TRACKABLE = "api_trackable"
    MANUAL_ONLY = "manual_only"


class Carrier(Base):
    """
    Carrier/courier entity.

    Carriers are classified as either api_trackable (can be auto-tracked
    via providers like 17TRACK) or manual_only (requires user to update
    status, e.g. Amazon, Flipkart).
    """
    __tablename__ = "carriers"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    code: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(100))
    carrier_type: Mapped[str] = mapped_column(
        String(20), default=CarrierType.API_TRACKABLE.value
    )
    country: Mapped[str | None] = mapped_column(String(5), nullable=True)
    provider_codes: Mapped[dict] = mapped_column(JSON, default=dict)
    tracking_url_template: Mapped[str | None] = mapped_column(
        String(500), nullable=True
    )
    logo_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now()
    )

    def __repr__(self) -> str:
        return f"<Carrier {self.code} ({self.carrier_type})>"
