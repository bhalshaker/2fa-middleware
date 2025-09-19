from fastapi import FastAPI
from contextlib import asynccontextmanager
from typing import AsyncGenerator
from app.dependacy.pg_database import create_db_pool,close_db_pool

@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Manages the database connection pool's lifecycle."""
    await create_db_pool()
    yield
    await close_db_pool()