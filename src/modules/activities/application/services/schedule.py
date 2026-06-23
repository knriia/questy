from src.modules.activities.domain.entities.schedule import SavedScheduleEntity, ScheduleEntity
from src.modules.activities.infrastructure.repositories.schedule import ScheduleRepository


class ScheduleService:
    def __init__(self, repository: ScheduleRepository):
        self.repository = repository

    async def create_schedule(self, schedule: ScheduleEntity) -> SavedScheduleEntity:
        return await self.repository.save_schedule(schedule=schedule)
