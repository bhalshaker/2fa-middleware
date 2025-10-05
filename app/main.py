from fastapi import FastAPI
from contextlib import asynccontextmanager
from typing import AsyncGenerator
from app.dependacy.pg_database import create_pg_db_pool,close_pg_db_pool
from app.dependacy.redis_database import close_redis_db_pool,create_redis_db_pool
from app.helper.metrics import MetricsMiddleware, metrics_app
import logging

logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Manages the databasees connection pool's lifecycle."""
    # Connect to PostgreSQL and Redis
    try:
        await create_pg_db_pool()
        await create_redis_db_pool()
        logger.info("All database connections successfully created.")
        yield  # The application serves requests here
    except Exception as e:
        print(f"Failed to connect to one or more databases: {e}")
        # Optionally, you can handle shutdown here if startup fails
        await close_pg_db_pool()
        await close_redis_db_pool()
        raise  # Re-raise the exception to stop the app from starting
    finally:
        # Disconnect from PostgreSQL and Redis on shutdown
        logger.info("Application shutdown initiated...")
        await close_pg_db_pool()
        await close_redis_db_pool()
        logger.info("All database connections successfully closed.")

app = FastAPI(
    title="2FA-MIDDLEWARE Application",
    lifespan=lifespan
)

app.add_middleware(MetricsMiddleware)
app.mount("/metrics", metrics_app)