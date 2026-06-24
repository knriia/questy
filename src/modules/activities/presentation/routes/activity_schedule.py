from datetime import datetime

from dishka.integrations.fastapi import FromDishka, inject
from fastapi import APIRouter

from src.modules.activities.application.services.activity_schedule import ActivityScheduleService
from src.modules.activities.domain.entities.activity_schedule import ActivityScheduleEntity
from src.modules.activities.presentation.dto.activity_schedule import ActivityScheduleCreateDTO, ActivityScheduleReadDTO

activity_schedule_router = APIRouter(prefix="/activity_schedules", tags=["activity_schedules"])


@activity_schedule_router.post("")
@inject
async def create_activity_schedule(
    activity_schedule_dto: ActivityScheduleCreateDTO, service: FromDishka[ActivityScheduleService]
) -> ActivityScheduleReadDTO:
    schedule_entity = ActivityScheduleEntity.create(
        activity_id=activity_schedule_dto.activity_id,
        schedule_type=activity_schedule_dto.schedule_type,
        interval_minutes=activity_schedule_dto.interval_minutes,
        next_run_at=activity_schedule_dto.next_run_at,
        timezone=activity_schedule_dto.timezone,
        is_enabled=activity_schedule_dto.is_enabled,
    )
    saved_activity_schedule = await service.create_activity_schedule(activity_schedule=schedule_entity)
    return ActivityScheduleReadDTO(
        id=saved_activity_schedule.id,
        activity_id=saved_activity_schedule.activity_id,
        schedule_type=saved_activity_schedule.schedule_type,
        interval_minutes=saved_activity_schedule.interval_minutes,
        next_run_at=saved_activity_schedule.next_run_at,
        last_run_at=saved_activity_schedule.last_run_at,
        timezone=saved_activity_schedule.timezone,
        is_enabled=saved_activity_schedule.is_enabled,
        created_at=saved_activity_schedule.created_at,
        updated_at=saved_activity_schedule.updated_at,
    )


@activity_schedule_router.get("/due")
@inject
async def get_due_activity_schedules(
    now: datetime, service: FromDishka[ActivityScheduleService]
) -> list[ActivityScheduleReadDTO]:
    activity_schedules = await service.get_due_activity_schedules(now=now)
    return [
        ActivityScheduleReadDTO(
            id=activity_schedule.id,
            activity_id=activity_schedule.activity_id,
            schedule_type=activity_schedule.schedule_type,
            interval_minutes=activity_schedule.interval_minutes,
            next_run_at=activity_schedule.next_run_at,
            last_run_at=activity_schedule.last_run_at,
            timezone=activity_schedule.timezone,
            is_enabled=activity_schedule.is_enabled,
            created_at=activity_schedule.created_at,
            updated_at=activity_schedule.updated_at,
        )
        for activity_schedule in activity_schedules
    ]
