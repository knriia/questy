from dishka import Provider, Scope, provide
from sqlalchemy.ext.asyncio import AsyncSession

from src.modules.activities.application.services.activity import ActivityService
from src.modules.activities.application.services.schedule import ScheduleService
from src.modules.activities.infrastructure.repositories.activity import ActivityRepository
from src.modules.activities.infrastructure.repositories.schedule import ScheduleRepository


class ActivityProvider(Provider):
    @provide(scope=Scope.REQUEST)
    async def activity_repository(self, session: AsyncSession) -> ActivityRepository:
        return ActivityRepository(session)

    @provide(scope=Scope.REQUEST)
    async def activity_service(self, repository: ActivityRepository) -> ActivityService:
        return ActivityService(repository=repository)


class ScheduleProvider(Provider):
    @provide(scope=Scope.REQUEST)
    async def schedule_repository(self, session: AsyncSession) -> ScheduleRepository:
        return ScheduleRepository(session)

    @provide(scope=Scope.REQUEST)
    async def schedule_service(self, repository: ScheduleRepository) -> ScheduleService:
        return ScheduleService(repository=repository)
