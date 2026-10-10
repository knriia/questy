from collections.abc import AsyncIterator

from dishka import AsyncContainer, Provider, Scope, make_async_container, provide
from sqlalchemy import pool
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker, create_async_engine

from modules.auth.di import AuthProvider
from modules.user.di import UserProvider
from shared.config import Settings
from shared.iuow import IUoW
from shared.uow import UoW

TEST_ENV_FILE = ".env.test"


class TestSettingsProvider(Provider):
    __test__ = False

    @provide(scope=Scope.APP)
    def settings(self) -> Settings:
        return Settings(_env_file=TEST_ENV_FILE)

    @provide(scope=Scope.REQUEST)
    async def create_uow(self, session: AsyncSession) -> IUoW:
        return UoW(session=session)


class TestDbProvider(Provider):
    __test__ = False

    @provide(scope=Scope.APP)
    def engine(self, settings: Settings) -> AsyncEngine:
        return create_async_engine(settings.db_url, echo=False, poolclass=pool.NullPool)

    @provide(scope=Scope.APP)
    def session_factory(self, engine: AsyncEngine) -> async_sessionmaker[AsyncSession]:
        return async_sessionmaker(bind=engine, expire_on_commit=False)

    @provide(scope=Scope.REQUEST)
    async def session(self, factory: async_sessionmaker[AsyncSession]) -> AsyncIterator[AsyncSession]:
        async with factory() as session:
            yield session


def create_test_container() -> AsyncContainer:
    return make_async_container(
        UserProvider(),
        AuthProvider(),
        TestSettingsProvider(),
        TestDbProvider(),
    )
