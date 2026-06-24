from datetime import datetime, timedelta
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.modules.activities.domain.entities.activity_schedule import ActivityScheduleEntity, SavedActivityScheduleEntity
from src.modules.activities.infrastructure.mappers.activity_schedule import (
    activity_schedule_entity_to_model,
    activity_schedule_model_to_entity,
)
from src.modules.activities.infrastructure.models.activity_schedule import ActivityScheduleModel


class ActivityScheduleRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def save_activity_schedule(self, activity_schedule: ActivityScheduleEntity) -> SavedActivityScheduleEntity:
        model = activity_schedule_entity_to_model(activity_schedule_entity=activity_schedule)
        self.session.add(model)
        await self.session.commit()
        await self.session.refresh(model)
        return activity_schedule_model_to_entity(activity_schedule_model=model)

    async def get_due_activity_schedules(self, now: datetime) -> list[SavedActivityScheduleEntity]:
        result = await self.session.execute(
            select(ActivityScheduleModel).where(
                ActivityScheduleModel.is_enabled.is_(True), ActivityScheduleModel.next_run_at <= now
            )
        )
        models = result.scalars().all()
        return [activity_schedule_model_to_entity(activity_schedule_model=model) for model in models]

    async def update_next_run_activity_schedule(
        self,
        activity_schedule_id: UUID,
        now: datetime,
    ) -> SavedActivityScheduleEntity:
        activity_schedule = await self.session.get(ActivityScheduleModel, activity_schedule_id)
        if not activity_schedule:
            raise ValueError("Напоминание не найдено")

        interval_minutes = activity_schedule.interval_minutes
        if interval_minutes is None:
            raise ValueError("Напоминание не является интервальным")

        activity_schedule.next_run_at = timedelta(minutes=float(interval_minutes)) + now
        activity_schedule.last_run_at = now
        self.session.add(activity_schedule)
        await self.session.commit()
        await self.session.refresh(activity_schedule)
        return activity_schedule_model_to_entity(activity_schedule_model=activity_schedule)
