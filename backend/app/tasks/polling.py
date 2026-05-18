"""
Background polling tasks using APScheduler.
"""

from apscheduler.schedulers.asyncio import AsyncIOScheduler

from app.core import get_settings
from app.core.logging import get_logger
from app.db import async_session_factory
from app.services import TrackingService

logger = get_logger("tasks.polling")

scheduler = AsyncIOScheduler()


async def poll_active_shipments():
    """
    Background job: refresh all active API-trackable shipments.
    Only runs for shipments with tracking_source='api' that aren't
    delivered or archived.
    """
    logger.info("Starting scheduled tracking refresh...")

    async with async_session_factory() as session:
        service = TrackingService(session)
        try:
            count = await service.refresh_all_active()
            logger.info(f"Scheduled refresh complete: {count} shipments updated")
        except Exception as e:
            logger.error(f"Scheduled refresh failed: {e}")


def start_scheduler():
    """Start the background polling scheduler."""
    settings = get_settings()

    # Add polling job
    scheduler.add_job(
        poll_active_shipments,
        "interval",
        minutes=settings.polling_interval_active_minutes,
        id="poll_active_shipments",
        name="Poll active API-trackable shipments",
        replace_existing=True,
    )

    scheduler.start()
    logger.info(
        f"Polling scheduler started "
        f"(interval: {settings.polling_interval_active_minutes}min)"
    )


def stop_scheduler():
    """Gracefully shut down the scheduler."""
    if scheduler.running:
        scheduler.shutdown(wait=False)
        logger.info("Polling scheduler stopped")
