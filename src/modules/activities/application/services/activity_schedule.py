from datetime import datetime

from src.modules.activities.domain.entities.activity_schedule import ActivityScheduleEntity, SavedActivityScheduleEntity
from src.modules.activities.infrastructure.repositories.activity_schedule import ActivityScheduleRepository


class ActivityScheduleService:
    def __init__(self, repository: ActivityScheduleRepository):
        self.repository = repository

    async def create_activity_schedule(self, activity_schedule: ActivityScheduleEntity) -> SavedActivityScheduleEntity:
        return await self.repository.save_activity_schedule(activity_schedule=activity_schedule)

    async def get_due_activity_schedules(self, now: datetime) -> list[SavedActivityScheduleEntity]:
        return await self.repository.get_due_activity_schedules(now=now)
