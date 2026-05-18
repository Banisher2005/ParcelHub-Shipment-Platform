"""
ParcelHub Backend — FastAPI Application Entry Point.

Lifespan management:
- Creates database tables on startup
- Seeds carrier data
- Starts background polling scheduler
- Gracefully shuts down on exit
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.router import api_router
from app.core import get_settings
from app.core.logging import setup_logging, get_logger
from app.db.engine import create_tables, dispose_engine, async_session_factory
from app.services.carrier_service import CarrierService
from app.tasks.polling import start_scheduler, stop_scheduler

setup_logging()
logger = get_logger("main")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan — startup and shutdown."""
    logger.info("Starting ParcelHub backend...")

    # Create tables (dev mode; use Alembic in production)
    await create_tables()
    logger.info("Database tables ready")

    # Seed carriers
    async with async_session_factory() as session:
        carrier_service = CarrierService(session)
        count = await carrier_service.seed_carriers()
        if count > 0:
            logger.info(f"Seeded {count} carriers")

    # Start polling scheduler
    settings = get_settings()
    if settings.tracking_provider != "mock" or settings.app_env == "development":
        start_scheduler()

    yield

    # Shutdown
    stop_scheduler()
    await dispose_engine()
    logger.info("ParcelHub backend stopped")


settings = get_settings()

app = FastAPI(
    title="ParcelHub API",
    description="Universal shipment tracking platform API",
    version="0.1.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount API routes
app.include_router(api_router)


@app.get("/health")
async def health_check():
    """Health check endpoint for deployment monitoring."""
    return {
        "status": "healthy",
        "service": "parcelhub-api",
        "version": "0.1.0",
        "provider": settings.tracking_provider,
    }
