from typing import AsyncGenerator
import logging
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from app.config.settings import settings

logger = logging.getLogger(__name__)

# SQLAlchemy async engine and session maker
_engine = None
_async_session_maker: async_sessionmaker[AsyncSession] | None = None

async def create_pg_db_pool():
    """Initializes the SQLAlchemy async engine and session maker."""
    global _engine, _async_session_maker
    if _engine is not None:
        return
    db_url = f"postgresql+asyncpg://{settings.pg_db_user}:{settings.pg_db_password}@{settings.pg_db_host}:{settings.pg_db_port}/{settings.pg_db_database}"
    _engine = create_async_engine(db_url, pool_size=settings.pg_db_pool_max_size)
    _async_session_maker = async_sessionmaker(_engine, expire_on_commit=False, class_=AsyncSession)
    logger.info("🛢️ SQLAlchemy async engine and session maker created.")

async def close_pg_db_pool():
    """Disposes the SQLAlchemy engine."""
    global _engine, _async_session_maker
    if _engine is not None:
        await _engine.dispose()
        _engine = None
        _async_session_maker = None
        logger.info("🛢️ SQLAlchemy engine disposed.")

async def get_pg_db_connection() -> AsyncGenerator[AsyncSession, None]:
    """Dependency that yields a SQLAlchemy AsyncSession."""
    global _async_session_maker
    if _async_session_maker is None:
        logger.info("🛢️ SQLAlchemy session maker was not initialized.")
        raise ConnectionError("Database session maker is not initialized.")
    async with _async_session_maker() as session:
        yield session