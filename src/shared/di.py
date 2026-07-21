from dishka import Provider, Scope, provide
from sqlalchemy.ext.asyncio import AsyncSession

from shared.config import Settings
from shared.uow import UoW


class SettingsProvider(Provider):
    @provide(scope=Scope.APP)
    def settings(self) -> Settings:
        return Settings()

    @provide(scope=Scope.REQUEST)
    async def create_uow(self, session: AsyncSession) -> UoW:
        return UoW(session=session)
