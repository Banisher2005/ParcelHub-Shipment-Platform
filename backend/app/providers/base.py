"""
Abstract tracking provider interface.

All tracking providers (17TRACK, AfterShip, future) must implement
this interface. The application NEVER directly calls a provider —
it always goes through this abstraction.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class NormalizedEvent:
    """A tracking event normalized into our universal schema."""
    status: str
    description: str
    location: str | None = None
    timestamp: datetime = field(default_factory=datetime.utcnow)
    raw_status: str | None = None


@dataclass
class CarrierMatch:
    """A detected carrier with confidence."""
    carrier_code: str
    carrier_name: str
    provider_carrier_code: int | None = None
    confidence: float = 0.0


@dataclass
class TrackingResult:
    """Result from a tracking info fetch."""
    success: bool
    tracking_number: str
    carrier_code: str | None = None
    carrier_name: str | None = None
    events: list[NormalizedEvent] = field(default_factory=list)
    origin: str | None = None
    destination: str | None = None
    estimated_delivery: datetime | None = None
    raw_data: dict | None = None
    error: str | None = None


@dataclass
class RegistrationResult:
    """Result from registering a tracking number with a provider."""
    success: bool
    tracking_number: str
    error: str | None = None


class TrackingProvider(ABC):
    """
    Abstract interface all tracking providers must implement.

    This is the ONLY boundary between our app and external tracking APIs.
    The service layer calls these methods; providers handle the translation.
    """

    @property
    @abstractmethod
    def provider_name(self) -> str:
        """Unique identifier for this provider (e.g., '17track', 'aftership')."""
        ...

    @abstractmethod
    async def register_tracking(
        self, tracking_number: str, carrier_code: int | None = None
    ) -> RegistrationResult:
        """
        Register a tracking number with the provider for updates.
        Some providers require this before you can fetch tracking info.
        """
        ...

    @abstractmethod
    async def get_tracking_info(
        self, tracking_number: str, carrier_code: int | None = None
    ) -> TrackingResult:
        """
        Fetch the latest tracking information for a tracking number.
        Returns normalized events in our universal schema.
        """
        ...

    @abstractmethod
    async def detect_carrier(
        self, tracking_number: str
    ) -> list[CarrierMatch]:
        """
        Attempt to detect the carrier from a tracking number.
        Returns a list of possible matches ranked by confidence.
        """
        ...
