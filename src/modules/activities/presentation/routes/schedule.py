from dishka.integrations.fastapi import FromDishka, inject
from fastapi import APIRouter

from src.modules.activities.application.services.schedule import ScheduleService
from src.modules.activities.domain.entities.schedule import ScheduleEntity
from src.modules.activities.presentation.dto.schedule import ScheduleCreateDTO, ScheduleReadDTO

schedule_router = APIRouter(prefix="/schedules", tags=["schedules"])


@schedule_router.post("")
@inject
async def create_schedule(schedule_dto: ScheduleCreateDTO, service: FromDishka[ScheduleService]) -> ScheduleReadDTO:
    schedule_entity = ScheduleEntity.create(
        activity_id=schedule_dto.activity_id,
        schedule_type=schedule_dto.schedule_type,
        interval_minutes=schedule_dto.interval_minutes,
        next_run_at=schedule_dto.next_run_at,
        timezone=schedule_dto.timezone,
        is_enabled=schedule_dto.is_enabled,
    )
    saved_schedule = await service.create_schedule(schedule=schedule_entity)
    return ScheduleReadDTO(
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
