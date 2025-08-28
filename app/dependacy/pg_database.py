from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from app.config.settings import Settings

#Generate database URL from configuration
db_url=Settings.db_url
# Create an asynchronous engine and configurre pool size
engine = create_async_engine(db_url, pool_size=Settings.db_pool_size, max_overflow=Settings.db_max_overflow)  # Adjust pool size as needed
# Create an asynchronous session factory using async_sessionmaker
SessionLocal = async_sessionmaker(bind=engine, expire_on_commit=False)

async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Yields a database session as a dependency.
    """
    async with SessionLocal() as session:
        yield session