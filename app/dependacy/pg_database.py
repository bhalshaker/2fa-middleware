import asyncpg
from typing import AsyncGenerator
from app.config.settings import settings
import logging

logger = logging.getLogger(__name__)

# Global variable for the connection pool
db_pool = None

async def create_db_pool():
    """Initializes the database connection pool."""

    # Consider db_pool variable global
    global db_pool
    # Create the pool connection
    db_pool = await asyncpg.create_pool(
        user=settings.pg_db_user,
        password=settings.pg_db_password,
        database=settings.pg_db_database,
        host=settings.pg_db_host,
        port=settings.pg_db_port,
    )
    logger.info("🛢️ Database connection pool created.")

async def close_db_pool():
    """Closes the database connection pool."""

    # Consider db_pool variable global
    global db_pool

    # Close db_pool if it is not null
    if db_pool:
        await db_pool.close()
        logger.info("🛢️Database connection pool closed.")

async def get_db_connection() -> AsyncGenerator[asyncpg.Connection, None]:
    """Dependency that yields a connection from the pool."""
    if db_pool is None:
        logger.info("🛢️ Database connection pool was not initialized.")
        raise ConnectionError("Database pool is not initialized.")
    # Return a connection
    async with db_pool.acquire() as connection:
        yield connection