from sqlalchemy.ext.asyncio import AsyncSession

from src.modules.activities.domain.entities.activity_schedule import ActivityScheduleEntity, SavedActivityScheduleEntity
from src.modules.activities.enums import ActivityScheduleType
from src.modules.activities.infrastructure.models.activity_schedule import ActivityScheduleModel


class ActivityScheduleRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def save_activity_schedule(self, activity_schedule: ActivityScheduleEntity) -> SavedActivityScheduleEntity:
        model = ActivityScheduleModel(
            id=activity_schedule.id,
            activity_id=activity_schedule.activity_id,
            schedule_type=activity_schedule.schedule_type,
            interval_minutes=activity_schedule.interval_minutes,
            next_run_at=activity_schedule.next_run_at,
            last_run_at=activity_schedule.last_run_at,
            timezone=activity_schedule.timezone,
            is_enabled=activity_schedule.is_enabled,
        )
        self.session.add(model)
        await self.session.commit()
        await self.session.refresh(model)
        return SavedActivityScheduleEntity(
            id=model.id,
            activity_id=model.activity_id,
            schedule_type=ActivityScheduleType(model.schedule_type),
            interval_minutes=model.interval_minutes,
            next_run_at=model.next_run_at,
            last_run_at=model.last_run_at,
            timezone=model.timezone,
            is_enabled=model.is_enabled,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )
