from sqlalchemy.ext.asyncio import AsyncSession

from src.modules.activities.domain.entities.schedule import SavedScheduleEntity, ScheduleEntity
from src.modules.activities.enums import ScheduleType
from src.modules.activities.infrastructure.models.schedule import ScheduleModel


class ScheduleRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def save_schedule(self, schedule: ScheduleEntity) -> SavedScheduleEntity:
        model = ScheduleModel(
            id=schedule.id,
            activity_id=schedule.activity_id,
            schedule_type=schedule.schedule_type,
            interval_minutes=schedule.interval_minutes,
            next_run_at=schedule.next_run_at,
            last_run_at=schedule.last_run_at,
            timezone=schedule.timezone,
            is_enabled=schedule.is_enabled,
        )
        self.session.add(model)
        await self.session.commit()
        await self.session.refresh(model)
        return SavedScheduleEntity(
            id=model.id,
            activity_id=model.activity_id,
            schedule_type=ScheduleType(model.schedule_type),
            interval_minutes=model.interval_minutes,
            next_run_at=model.next_run_at,
            last_run_at=model.last_run_at,
            timezone=model.timezone,
            is_enabled=model.is_enabled,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )
