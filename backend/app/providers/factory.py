"""
Provider factory — creates the configured tracking provider.

Uses the TRACKING_PROVIDER setting to determine which provider to instantiate.
This is the single entry point for provider creation in the application.
"""

from app.core import get_settings
from app.core.logging import get_logger
from app.providers.base import TrackingProvider
from app.providers.mock_provider import MockTrackingProvider
from app.providers.seventeen_track import SeventeenTrackProvider

logger = get_logger("providers.factory")


def create_tracking_provider() -> TrackingProvider:
    """
    Create a tracking provider based on configuration.

    Returns MockTrackingProvider for development or when no API key is set.
    Returns SeventeenTrackProvider when configured with a valid API key.
    """
    settings = get_settings()
    provider_name = settings.tracking_provider.lower()

    if provider_name == "17track":
        if not settings.seventeen_track_api_key:
            logger.warning(
                "17TRACK provider selected but no API key configured. "
                "Falling back to mock provider."
            )
            return MockTrackingProvider()

        logger.info("Using 17TRACK tracking provider")
        return SeventeenTrackProvider(
            api_key=settings.seventeen_track_api_key
        )

    # Default to mock
    logger.info("Using mock tracking provider")
    return MockTrackingProvider()


# Singleton provider instance
_provider: TrackingProvider | None = None


def get_tracking_provider() -> TrackingProvider:
    """Get the singleton tracking provider instance."""
    global _provider
    if _provider is None:
        _provider = create_tracking_provider()
    return _provider
