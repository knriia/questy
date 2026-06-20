from dishka import Provider, Scope, provide
from sqlalchemy.ext.asyncio import AsyncSession

from src.modules.activities.application.service import ActivityService
from src.modules.activities.infrastructure.repository import ActivityRepository


class ActivityProvider(Provider):
    @provide(scope=Scope.REQUEST)
    async def activity_repository(self, session: AsyncSession) -> ActivityRepository:
        return ActivityRepository(session)

    @provide(scope=Scope.REQUEST)
    async def activity_service(self, repository: ActivityRepository) -> ActivityService:
        return ActivityService(repository=repository)
