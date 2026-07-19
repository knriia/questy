from dishka.integrations.fastapi import FromDishka, inject
from fastapi import APIRouter

from modules.users.application.service import UserService
from modules.users.presentation.dto import UserCreateDTO, UserReadDTO
from modules.users.presentation.mappers import user_dto_to_entity, user_entity_to_dto

user_router = APIRouter(prefix="/users", tags=["users"])


@user_router.post("")
@inject
async def create_user(user_dto: UserCreateDTO, service: FromDishka[UserService]) -> UserReadDTO:
    user = user_dto_to_entity(user_dto=user_dto)
    return user_entity_to_dto(user_entity=await service.create_user(user=user))
