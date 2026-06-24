from datetime import datetime

from dishka.integrations.fastapi import FromDishka, inject
from fastapi import APIRouter

from src.modules.activities.application.services.activity_schedule import ActivityScheduleService
from src.modules.activities.presentation.dto.activity_schedule import ActivityScheduleCreateDTO, ActivityScheduleReadDTO
from src.modules.activities.presentation.mappers.activity_schedule import (
    activity_schedule_dto_to_entity,
    activity_schedule_entity_to_dto,
)

activity_schedule_router = APIRouter(prefix="/activity_schedules", tags=["activity_schedules"])


@activity_schedule_router.post("")
@inject
async def create_activity_schedule(
    activity_schedule_dto: ActivityScheduleCreateDTO,
    service: FromDishka[ActivityScheduleService],
) -> ActivityScheduleReadDTO:
    schedule_entity = activity_schedule_dto_to_entity(activity_schedule_dto=activity_schedule_dto)
    saved_activity_schedule = await service.create_activity_schedule(activity_schedule=schedule_entity)
    return activity_schedule_entity_to_dto(activity_schedule_entity=saved_activity_schedule)


@activity_schedule_router.get("/due")
@inject
async def get_due_activity_schedules(
    now: datetime,
    service: FromDishka[ActivityScheduleService],
) -> list[ActivityScheduleReadDTO]:
    activity_schedules = await service.get_due_activity_schedules(now=now)
    return [
        activity_schedule_entity_to_dto(activity_schedule_entity=activity_schedule)
        for activity_schedule in activity_schedules
    ]
