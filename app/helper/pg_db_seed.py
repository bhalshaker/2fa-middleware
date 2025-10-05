from app.model.user_profile import Base
import logging
from app.config.settings import settings
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("Seed Database")

db_url=f"postgresql+asyncpg://{settings.pg_db_user}:{settings.pg_db_password}@{settings.pg_db_host}:{settings.pg_db_port}/{settings.pg_db_database}"
engine = create_async_engine(db_url, pool_size=settings.pg_db_pool_max_size)

async def recreate_db(engine,Base):
    # Drop and recreate tables to ensure a clean slate
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

async def main():
    logger.info("Recreating database... 🫕")
    # Recreate the database schema
    try:
      await recreate_db(engine, Base)
      logger.info("Database recreated successfully ... 🍜")
      logger.info("Creating admin user based on configuration... 🧑‍💻")
    except Exception as e:
      logger.error(f"An error occurred while seeding the database: {e}")


# Run the async main function
if __name__ == "__main__":
    asyncio.run(main())