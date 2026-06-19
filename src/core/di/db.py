from dishka import Provider, Scope, provide
from collections.abc import AsyncIterable
from sqlalchemy.ext.asyncio import AsyncSession, AsyncEngine, create_async_engine, async_sessionmaker

from src.core.config import Settings


class DbProvider(Provider):
    @provide(scope=Scope.APP)
    def engine(self, settings: Settings) -> AsyncEngine:
        return create_async_engine(settings.db_url, echo=True)

    @provide(scope=Scope.APP)
    def session_factory(self, engine: AsyncEngine) -> async_sessionmaker[AsyncSession]:
        return async_sessionmaker(bind=engine, expire_on_commit=False)

    @provide(scope=Scope.REQUEST)
    async def session(self, factory: async_sessionmaker[AsyncSession]) -> AsyncIterable[AsyncSession]:
        async with factory() as session:
            yield session
