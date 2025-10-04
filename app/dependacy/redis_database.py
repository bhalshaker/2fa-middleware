import redis.asyncio as aioredis
from typing import AsyncGenerator
from app.config.settings import settings
import logging

logger = logging.getLogger(__name__)

# Global variable for the connection pool
redis_pool = None

async def create_redis_db_pool():
    """Initializes the Redis connection pool."""
    # Consider redis_pool variable global
    global redis_pool
    # Create the Redis connection pool
    redis_pool = aioredis.from_url(
        settings.redis_url,
        encoding="utf-8",
        decode_responses=True,
        max_connections=settings.redis_max_connections
    )
    logger.info("⛁ Redis connection pool created.")

async def close_redis_db_pool():
    """Closes the Redis connection pool."""
    # Consider redis_pool variable global
    global redis_pool
    # Close the Redis connection pool if it exists
    if redis_pool:
        await redis_pool.aclose()
        logger.info("⛁ Redis connection pool closed.")

async def get_redis_db_client() -> AsyncGenerator[aioredis.Redis, None]:
    """Dependency to get a client from the pool."""
    # Raise an error if the pool is not initialized
    if redis_pool is None:
        raise ConnectionError("Redis pool is not initialized.")
    yield redis_pool