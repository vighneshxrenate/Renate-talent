"""Shared fixtures for the test suite.

Uses an in-memory SQLite async engine so tests are fast and don't need
a running PostgreSQL instance.  Where PostgreSQL-specific features are
required (gen_random_uuid), we patch with Python-side defaults.
"""

import asyncio
import uuid
from typing import AsyncGenerator
from unittest.mock import AsyncMock, patch

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy import event
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.models.base import Base
from app.models.college import College
from app.models.industry import Industry


# ---------------------------------------------------------------------------
# Engine / session for tests (SQLite async)
# ---------------------------------------------------------------------------
TEST_DB_URL = "sqlite+aiosqlite:///file::memory:?cache=shared&uri=true"

engine = create_async_engine(TEST_DB_URL, echo=False)
TestSession = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


@event.listens_for(engine.sync_engine, "connect")
def _enable_foreign_keys(dbapi_conn, _):
    """SQLite needs this pragma to enforce FK constraints."""
    cursor = dbapi_conn.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------
@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(autouse=True)
async def setup_db():
    """Create all tables before each test, drop after."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    async with TestSession() as session:
        yield session


@pytest_asyncio.fixture
async def seed_data(db_session: AsyncSession):
    """Insert a college and an industry, return their IDs."""
    college = College(id=uuid.uuid4(), name="Test College", slug="test-college")
    industry = Industry(id=uuid.uuid4(), name="Test Industry", slug="test-industry")
    db_session.add_all([college, industry])
    await db_session.commit()
    return {"college_id": str(college.id), "industry_id": str(industry.id)}


@pytest_asyncio.fixture
async def client(db_session: AsyncSession, seed_data) -> AsyncGenerator[AsyncClient, None]:
    """AsyncClient wired to the FastAPI app with the test DB session."""
    from app.database import get_db
    from app.main import app

    async def _override_db():
        yield db_session

    app.dependency_overrides[get_db] = _override_db

    # Patch storage service to avoid real filesystem writes during tests
    mock_upload = AsyncMock(return_value="test/path/resume.pdf")
    mock_delete = AsyncMock()

    with (
        patch("app.routers.submissions.storage_service.upload_resume", mock_upload),
        patch("app.routers.submissions.storage_service.delete_resume", mock_delete),
    ):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as ac:
            ac._seed = seed_data  # type: ignore[attr-defined]
            yield ac

    app.dependency_overrides.clear()
