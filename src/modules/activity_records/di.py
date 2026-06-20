from dishka import Provider, Scope, provide
from sqlalchemy.ext.asyncio import AsyncSession

from src.modules.activity_records.application.service import ActivityRecordService
from src.modules.activity_records.infrastructure.repository import ActivityRecordRepository


class ActivityRecordProvider(Provider):
    @provide(scope=Scope.REQUEST)
    async def activity_repository(self, session: AsyncSession) -> ActivityRecordRepository:
        return ActivityRecordRepository(session)

    @provide(scope=Scope.REQUEST)
    async def activity_service(self, repository: ActivityRecordRepository) -> ActivityRecordService:
        return ActivityRecordService(repository=repository)
