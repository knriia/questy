from dishka.integrations.fastapi import FromDishka, inject
from fastapi import APIRouter

from modules.activity_records.application.service import ActivityRecordService
from modules.activity_records.presentation.dto import ActivityRecordCreateDTO, ActivityRecordReadDTO
from modules.activity_records.presentation.mappers import (
    activity_record_dto_to_entity,
    activity_record_entity_to_dto,
)

activity_record_router = APIRouter(prefix="/activity_records", tags=["activity_records"])


@activity_record_router.post("")
@inject
async def create_activity_record(
    activity_record_dto: ActivityRecordCreateDTO,
    service: FromDishka[ActivityRecordService],
) -> ActivityRecordReadDTO:
    entity = activity_record_dto_to_entity(activity_record_dto=activity_record_dto)
    created_activity = await service.create_activity_record(activity_record=entity)
    return activity_record_entity_to_dto(activity_record_entity=created_activity)
