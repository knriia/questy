import pytest
from alembic.script import ScriptDirectory
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from tests.support.database import alembic_config

pytestmark = [pytest.mark.asyncio, pytest.mark.integration_db]


async def test_test_database_has_all_current_migrations(db_sessions: async_sessionmaker[AsyncSession]) -> None:
    expected_heads = set(ScriptDirectory.from_config(alembic_config()).get_heads())
    async with db_sessions() as session:
        versions = await session.scalars(text("SELECT version_num FROM alembic_version"))
        assert set(versions) == expected_heads


async def test_each_database_test_starts_without_registered_accounts(
    db_sessions: async_sessionmaker[AsyncSession],
) -> None:
    async with db_sessions() as session:
        assert await session.scalar(text("SELECT count(*) FROM users")) == 0
        assert await session.scalar(text("SELECT count(*) FROM auth_credentials")) == 0
