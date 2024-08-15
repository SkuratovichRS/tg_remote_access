import asyncio
import uuid
from typing import Type
from unittest.mock import AsyncMock, Mock

import asyncpg
import fakeredis
import pytest
import pytest_asyncio
from asyncpg import Pool
from starlette.testclient import TestClient

from app.factory import Factory
from app.settings import Settings
from app.storages.db_postgres import Db


@pytest.fixture(scope="session")
def loop():
    return asyncio.get_event_loop()


@pytest.fixture(scope="session")
def settings() -> Type[Settings]:
    Settings.DB_NAME = f"{Settings.DB_NAME}_{uuid.uuid4().hex}"
    return Settings


@pytest.fixture(scope="session")
def factory(settings) -> Factory:
    return Factory(settings)


@pytest_asyncio.fixture(scope="session", autouse=True)
async def init_db(settings: Type[Settings]) -> Pool:
    conn = await asyncpg.connect(
        user=settings.DB_USER,
        password=settings.DB_PASSWORD,
        host=settings.DB_HOST,
        port=settings.DB_PORT,
    )
    await conn.execute(f"CREATE DATABASE {settings.DB_NAME} OWNER {settings.DB_USER}")

    print(f"test database {settings.DB_NAME} created")
    pool = await asyncpg.create_pool(
        database=settings.DB_NAME,
        user=settings.DB_USER,
        password=settings.DB_PASSWORD,
        host=settings.DB_HOST,
        port=settings.DB_PORT,
    )
    await Db(pool).create_tables()
    yield
    await pool.close()
    await conn.execute(f'DROP DATABASE "{settings.DB_NAME}"')


@pytest_asyncio.fixture()
async def session_pool(settings: Type[Settings]) -> Pool:
    pool = await asyncpg.create_pool(
        database=settings.DB_NAME,
        user=settings.DB_USER,
        password=settings.DB_PASSWORD,
        host=settings.DB_HOST,
        port=settings.DB_PORT,
    )
    yield pool
    async with pool.acquire() as session:
        await session.execute("TRUNCATE TABLE commands;")
    await pool.close()


@pytest_asyncio.fixture()
def redis_client():
    redis = fakeredis.FakeStrictRedis()
    yield redis
    redis.flushall()


@pytest.fixture()
def app_client(factory):
    app = factory._create_app()
    app_client = TestClient(app)
    yield app_client
