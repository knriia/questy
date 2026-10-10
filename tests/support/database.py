from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from pathlib import Path

from alembic import command
from alembic.config import Config
from sqlalchemy import pool, text
from sqlalchemy.engine import URL, Connection, make_url
from sqlalchemy.ext.asyncio import create_async_engine

from shared.config import Settings

PROJECT_ROOT = Path(__file__).resolve().parents[2]


def alembic_config() -> Config:
    return Config(str(PROJECT_ROOT / "alembic.ini"))


async def upgrade_database(url: URL) -> None:
    engine = create_async_engine(url, poolclass=pool.NullPool)

    def upgrade(connection: Connection) -> None:
        config = alembic_config()
        config.attributes["connection"] = connection
        command.upgrade(config, "head")

    try:
        async with engine.begin() as connection:
            await connection.run_sync(upgrade)
    finally:
        await engine.dispose()


@asynccontextmanager
async def temporary_database(settings: Settings) -> AsyncIterator[None]:
    database_name = settings.DB_NAME
    test_url = make_url(settings.db_url)
    admin_url = test_url.set(database="postgres")
    admin_engine = create_async_engine(admin_url, isolation_level="AUTOCOMMIT", poolclass=pool.NullPool)
    quoted_name = admin_engine.dialect.identifier_preparer.quote_identifier(database_name)
    created = False
    try:
        async with admin_engine.connect() as connection:
            await connection.execute(text(f"CREATE DATABASE {quoted_name} TEMPLATE template0"))
        created = True
        await upgrade_database(test_url)
        yield
    finally:
        try:
            if created:
                async with admin_engine.connect() as connection:
                    await connection.execute(text(f"DROP DATABASE {quoted_name} WITH (FORCE)"))
        finally:
            await admin_engine.dispose()
