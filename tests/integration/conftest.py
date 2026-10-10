from collections.abc import AsyncIterator

import pytest
import pytest_asyncio
from asyncpg import PostgresError
from dishka import AsyncContainer
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker

from shared.config import Settings
from tests.di import create_test_container
from tests.support.database import temporary_database


@pytest_asyncio.fixture(scope="session", loop_scope="session")
async def test_container() -> AsyncIterator[AsyncContainer]:
    container = create_test_container()
    try:
        settings = await container.get(Settings)
        connection_error = None
        try:
            async with temporary_database(settings):
                engine = await container.get(AsyncEngine)
                try:
                    yield container
                finally:
                    await engine.dispose()
        except (PostgresError, SQLAlchemyError, OSError) as error:
            connection_error = type(error).__name__
        if connection_error is not None:
            pytest.fail(
                f"Test database initialization failed ({connection_error}); check .env.test and PostgreSQL role access",
                pytrace=False,
            )
    finally:
        await container.close()


@pytest_asyncio.fixture
async def db_sessions(test_container: AsyncContainer) -> async_sessionmaker[AsyncSession]:
    sessions = await test_container.get(async_sessionmaker[AsyncSession])
    async with sessions() as session:
        await session.execute(text("TRUNCATE TABLE public.users RESTART IDENTITY CASCADE"))
        await session.commit()
    return sessions
