from typing import Annotated

from dishka.integrations.fastapi import FromDishka, inject
from fastapi import APIRouter, Security

from modules.activity.application.services.activity import ActivityService
from modules.activity.presentation.dto.activity import ActivityCreateDTO, ActivityReadDTO
from modules.activity.presentation.mappers.activity import activity_dto_to_entity, activity_entity_to_dto
from modules.auth.security.dependencies import get_current_principal
from modules.auth.security.dto import Principal

activity_router = APIRouter(prefix="/activities", tags=["activities"])


@activity_router.post("/create")
@inject
async def create_activity(
    activity_dto: ActivityCreateDTO,
    service: FromDishka[ActivityService],
    current_principal: Annotated[Principal, Security(get_current_principal)],
) -> ActivityReadDTO:
    entity = activity_dto_to_entity(activity_dto=activity_dto, user_id=current_principal.user_id)
    return activity_entity_to_dto(activity_entity=await service.create_activity(activity=entity))
