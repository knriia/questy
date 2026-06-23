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
    saved_schedule = await service.create_activity_schedule(activity_schedule=schedule_entity)
    return ActivityScheduleReadDTO(
        id=saved_schedule.id,
        activity_id=saved_schedule.activity_id,
        schedule_type=saved_schedule.schedule_type,
        interval_minutes=saved_schedule.interval_minutes,
        next_run_at=saved_schedule.next_run_at,
        last_run_at=saved_schedule.last_run_at,
        timezone=saved_schedule.timezone,
        is_enabled=saved_schedule.is_enabled,
        created_at=saved_schedule.created_at,
        updated_at=saved_schedule.updated_at,
    )
