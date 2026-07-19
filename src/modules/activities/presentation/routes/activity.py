from dishka.integrations.fastapi import FromDishka, inject
from fastapi import APIRouter

from modules.activities.application.services.activity import ActivityService
from modules.activities.presentation.dto.activity import ActivityCreateDTO, ActivityReadDTO
from modules.activities.presentation.mappers.activity import activity_dto_to_entity, activity_entity_to_dto

activity_router = APIRouter(prefix="/activities", tags=["activities"])


@activity_router.post("")
@inject
async def create_activity(activity_dto: ActivityCreateDTO, service: FromDishka[ActivityService]) -> ActivityReadDTO:
    entity = activity_dto_to_entity(activity_dto=activity_dto)
    return activity_entity_to_dto(activity_entity=await service.create_activity(activity=entity))
