from typing import Annotated

from dishka import FromDishka
from dishka.integrations.fastapi import inject
from fastapi import APIRouter, Security

from modules.auth.security.dependencies import get_current_principal
from modules.auth.security.dto import Principal
from modules.user.application.service import UserService
from modules.user.domain.exceptions import UserNotFoundError
from modules.user.presentation.dto import UserMeResponse

user_router = APIRouter(prefix="/users", tags=["users"])


@user_router.get("/me")
@inject
async def get_me(
    user_service: FromDishka[UserService], current_principal: Annotated[Principal, Security(get_current_principal)]
) -> UserMeResponse:
    user_entity = await user_service.get_user_by_id(user_id=current_principal.user_id)
    if user_entity is None:
        raise UserNotFoundError

    return UserMeResponse(
        id=user_entity.id,
        username=user_entity.username.value,
        timezone=user_entity.timezone.value,
        email=user_entity.email.value,
    )
