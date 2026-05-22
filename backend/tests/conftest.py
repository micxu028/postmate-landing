"""Shared fixtures and test configuration."""
import asyncio
import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from main import app
from database import get_db, async_session as prod_async_session
from models import Base

TEST_DB_URL = "sqlite+aiosqlite:///:memory:"

test_engine = create_async_engine(TEST_DB_URL, echo=False, connect_args={"check_same_thread": False})
TestSession = async_sessionmaker(test_engine, class_=AsyncSession, expire_on_commit=False)


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(autouse=True)
async def setup_db():
    """Create tables before each test, drop after."""
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


async def override_get_db():
    async with TestSession() as session:
        try:
            yield session
        finally:
            await session.close()


@pytest_asyncio.fixture
async def client():
    app.dependency_overrides[get_db] = override_get_db
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def db_session():
    async with TestSession() as session:
        yield session
        await session.rollback()


@pytest_asyncio.fixture
async def registered_user(client):
    """Register and return a user token."""
    resp = await client.post("/api/auth/register", json={
        "email": "test@studio.com",
        "password": "testpass123",
    })
    data = resp.json()
    return {"token": data["token"], "user_id": data["user_id"]}
