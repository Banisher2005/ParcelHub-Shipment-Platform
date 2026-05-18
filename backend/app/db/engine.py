"""
Async database engine and session factory.
"""

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.core import get_settings

settings = get_settings()

engine = create_async_engine(
    settings.database_url,
    echo=False,
    pool_pre_ping=True,
    # SQLite doesn't support pool_size/max_overflow, but PostgreSQL does.
    # These are ignored for SQLite.
    **(
        {}
        if "sqlite" in settings.database_url
        else {"pool_size": 10, "max_overflow": 20}
    ),
)

async_session_factory = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def get_async_session():
    """FastAPI dependency that yields an async session."""
    async with async_session_factory() as session:
        try:
            yield session
        finally:
            await session.close()


async def create_tables():
    """Create all tables. Used for development; Alembic for production."""
    from app.db.base import Base
    # Import all models so they register with Base.metadata
    import app.models  # noqa: F401

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def dispose_engine():
    """Dispose of the engine connection pool."""
    await engine.dispose()
