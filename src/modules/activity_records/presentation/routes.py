from dishka.integrations.fastapi import FromDishka, inject
from fastapi import APIRouter

from src.modules.activity_records.application.service import ActivityRecordService
from src.modules.activity_records.domain.entities import ActivityRecordEntity
from src.modules.activity_records.presentation.dto import ActivityRecordCreateDTO, ActivityRecordReadDTO

activity_record_router = APIRouter(prefix="/activity_records", tags=["activity_records"])


@activity_record_router.post("")
@inject
async def create_activity(
    activity_dto: ActivityRecordCreateDTO, service: FromDishka[ActivityRecordService]
) -> ActivityRecordReadDTO:
    entity = ActivityRecordEntity.create(
        activity_id=activity_dto.activity_id,
        user_id=activity_dto.user_id,
        status=activity_dto.status,
        data=activity_dto.data,
    )
    created_activity = await service.create_activity_record(activity_record=entity)
    return ActivityRecordReadDTO(
        id=created_activity.id,
        activity_id=created_activity.activity_id,
        user_id=created_activity.user_id,
        status=created_activity.status,
        data=created_activity.data,
        created_at=created_activity.created_at,
        updated_at=created_activity.updated_at,
    )
