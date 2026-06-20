from dishka.integrations.fastapi import FromDishka, inject
from fastapi import APIRouter

from src.modules.activities.application.service import ActivityService
from src.modules.activities.domain.entity import ActivityEntity
from src.modules.activities.presentation.dto import ActivityCreateDTO, ActivityReadDTO

activity_router = APIRouter(prefix="/activities", tags=["activities"])


@activity_router.post("")
@inject
async def create_activity(activity_dto: ActivityCreateDTO, service: FromDishka[ActivityService]) -> ActivityReadDTO:
    entity = ActivityEntity.create(
        user_id=activity_dto.user_id,
        title=activity_dto.title,
        description=activity_dto.description,
        activity_type=activity_dto.activity_type,
    )
    created_activity = await service.create_activity(activity=entity)
    return ActivityReadDTO(
        id=created_activity.id,
        user_id=created_activity.user_id,
        title=created_activity.title,
        description=created_activity.description,
        activity_type=created_activity.activity_type,
        status=created_activity.status,
        created_at=created_activity.created_at,
        updated_at=created_activity.updated_at,
    )
