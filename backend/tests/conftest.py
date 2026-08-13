import pytest
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.database import engine
from app.db.session import get_db as db_get_db
from app.modules.auth.dependencies import get_db as auth_get_db
from app.main import app


@pytest.fixture
async def db_connection():
    """Create a connection and begin a transaction that will be rolled back."""
    # Dispose old pool connections to ensure fresh ones bound to the current event loop
    await engine.dispose()
    async with engine.connect() as conn:
        transaction = await conn.begin()
        yield conn
        await transaction.rollback()
    await engine.dispose()


@pytest.fixture
async def db_session(db_connection):
    """Yield a session bound to the transaction, using savepoints for commit calls."""
    session = AsyncSession(
        bind=db_connection,
        expire_on_commit=False,
        join_transaction_mode="create_savepoint",
    )
    yield session
    await session.close()


@pytest.fixture
async def client(db_session):
    """Async HTTP client overriding get_db to use the test db session."""
    # Backup existing overrides from other tests (e.g. unit tests)
    backup = app.dependency_overrides.copy()
    app.dependency_overrides.clear()

    async def override_get_db():
        yield db_session

    app.dependency_overrides[db_get_db] = override_get_db
    app.dependency_overrides[auth_get_db] = override_get_db

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        yield ac

    # Restore original overrides
    app.dependency_overrides = backup
