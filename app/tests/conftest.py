import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.pool import StaticPool
from httpx import ASGITransport, AsyncClient
from app.main import app
import app.dependacy.pg_database as pg_database
import app.dependacy.redis_database as redis_database
from sqlalchemy.ext.asyncio import AsyncSession as _AsyncSession  # for typing below
from app.dependacy.pg_database import get_pg_db_connection
from app.dependacy.redis_database import get_redis_db_client
from app.model.user_profile import Base

# Simple in-memory "fake" redis client for tests (implements used async methods)
class RedisFake:
    def __init__(self):
        self._store = {}

    async def get(self, key):
        return self._store.get(key)

    async def set(self, key, value, ex=None):
        # store value as string for parity with redis.decode_responses=True
        self._store[key] = value
        return True

    async def delete(self, key):
        return self._store.pop(key, None) is not None

    async def aclose(self):
        # no-op
        return None

@pytest_asyncio.fixture(scope="function")
async def db_engine():
    """Create a fresh in-memory database engine for each test."""
    test_database_url = f"sqlite+aiosqlite:///:memory:"
    engine = create_async_engine(
        test_database_url,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool
    )

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield engine

    await engine.dispose()

@pytest_asyncio.fixture(scope="function")
async def db_session(db_engine):
    """Create a fresh database session for each test."""
    TestSessionLocal = async_sessionmaker(db_engine, class_=AsyncSession, expire_on_commit=False)
    async with TestSessionLocal() as session:
        try:
            yield session
        finally:
            await session.rollback()
            await session.close()

@pytest_asyncio.fixture(scope="function")
async def client(db_session):
    """Get a TestClient with the database and redis dependency overrides."""

    

    # Patch create/close pool functions so FastAPI startup (lifespan) does not attempt prod connections
    async def _placeholder_create_pg_db_pool():
        # set the module globals to use our in-memory engine/session maker
        pg_database._engine = db_session.get_bind()  # underlying engine attached to session
        pg_database._async_session_maker = async_sessionmaker(pg_database._engine, expire_on_commit=False, class_=_AsyncSession)

    async def _placeholder_close_pg_db_pool():
        # keep cleanup minimal; engine will be disposed by db_engine fixture
        pg_database._engine = None
        pg_database._async_session_maker = None

    async def _placeholder_create_redis_db_pool():
        redis_database.redis_pool = RedisFake()

    async def _placeholder_close_redis_db_pool():
        if getattr(redis_database, "redis_pool", None):
            # call aclose if present
            try:
                await redis_database.redis_pool.aclose()
            except Exception:
                pass
            redis_database.redis_pool = None

    # apply monkeypatch by replacing functions on module
    pg_database.create_pg_db_pool = _placeholder_create_pg_db_pool
    pg_database.close_pg_db_pool = _placeholder_close_pg_db_pool
    redis_database.create_redis_db_pool = _placeholder_create_redis_db_pool
    redis_database.close_redis_db_pool = _placeholder_close_redis_db_pool

    # Override the dependency functions used in routes to yield our test objects
    async def override_get_pg_db_connection():
        try:
            yield db_session
        finally:
            pass

    async def override_get_redis_db_client():
        # ensure the fake redis pool exists
        if getattr(redis_database, "redis_pool", None) is None:
            await _placeholder_create_redis_db_pool()
        yield redis_database.redis_pool

    app.dependency_overrides[get_pg_db_connection] = override_get_pg_db_connection
    app.dependency_overrides[get_redis_db_client] = override_get_redis_db_client

    # Create test client (this will run lifespan but create_* functions are no-ops patched above)
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as test_client:
        yield test_client

    # cleanup overrides
    app.dependency_overrides = {}
    # ensure we call close hooks to clear fake pools if needed
    await _placeholder_close_redis_db_pool()
    await _placeholder_close_pg_db_pool()

@pytest.fixture(scope="session")
def anyio_backend():
    """Return the anyio backend to use."""
    return "asyncio"