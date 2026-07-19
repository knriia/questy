from datetime import datetime, timedelta

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from modules.activities.domain.entities.activity_schedule import ActivityScheduleEntity, SavedActivityScheduleEntity
from modules.activities.infrastructure.mappers.activity_schedule import (
    activity_schedule_entity_to_model,
    activity_schedule_model_to_entity,
)
from modules.activities.infrastructure.models.activity_schedule import ActivityScheduleModel


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
        activity_schedule: SavedActivityScheduleEntity,
        now: datetime,
    ) -> SavedActivityScheduleEntity:
        interval_minutes = activity_schedule.interval_minutes
        if interval_minutes is None:
            raise ValueError("Напоминание не является интервальным")

        stmt = (
            update(ActivityScheduleModel)
            .where(ActivityScheduleModel.id == activity_schedule.id)
            .values(
                next_run_at=now + timedelta(minutes=float(interval_minutes)),
                last_run_at=now,
            )
            .returning(ActivityScheduleModel)
        )
        result = await self.session.execute(stmt)
        await self.session.commit()
        activity_model = result.scalar_one()
        return activity_schedule_model_to_entity(activity_schedule_model=activity_model)
