from dishka import Provider, Scope, provide
from sqlalchemy.ext.asyncio import AsyncSession

from src.modules.activities.application.services.activity import ActivityService
from src.modules.activities.application.services.activity_schedule import ActivityScheduleService
from src.modules.activities.application.services.activity_schedule_dispatcher import (
    ActivityNotificationTaskSender,
    ActivityScheduleDispatcher,
)
from src.modules.activities.infrastructure.repositories.activity import ActivityRepository
from src.modules.activities.infrastructure.repositories.activity_schedule import ActivityScheduleRepository
from src.modules.activities.presentation.tasks import send_activity_notification


class ActivityProvider(Provider):
    @provide(scope=Scope.REQUEST)
    async def activity_repository(self, session: AsyncSession) -> ActivityRepository:
        return ActivityRepository(session)

    @provide(scope=Scope.REQUEST)
    async def activity_service(self, repository: ActivityRepository) -> ActivityService:
        return ActivityService(repository=repository)


class ActivityScheduleProvider(Provider):
    @provide(scope=Scope.REQUEST)
    async def activity_schedule_repository(self, session: AsyncSession) -> ActivityScheduleRepository:
        return ActivityScheduleRepository(session)

    @provide(scope=Scope.REQUEST)
    async def activity_schedule_service(self, repository: ActivityScheduleRepository) -> ActivityScheduleService:
        return ActivityScheduleService(repository=repository)

    @provide(scope=Scope.APP)
    async def activity_schedule_task_sender(
        self,
    ) -> ActivityNotificationTaskSender:
        return ActivityNotificationTaskSender(enqueue=send_activity_notification.kiq)

    @provide(scope=Scope.REQUEST)
    async def activity_schedule_dispatcher(
        self,
        activity_schedule_service: ActivityScheduleService,
        activity_schedule_task_sender: ActivityNotificationTaskSender,
    ) -> ActivityScheduleDispatcher:
        return ActivityScheduleDispatcher(
            service=activity_schedule_service,
            task_sender=activity_schedule_task_sender,
        )
