from dishka.integrations.fastapi import FromDishka, inject
from fastapi import APIRouter, status

from modules.users.application.service import UserService
from modules.users.presentation.dto import UserCreateDTO, UserReadDTO
from modules.users.presentation.mappers import api_user_dto_to_application_user_dto, user_entity_to_dto

user_router = APIRouter(prefix="/auth", tags=["users"])


@user_router.post("/register", status_code=status.HTTP_201_CREATED)
@inject
async def create_user(user_dto: UserCreateDTO, service: FromDishka[UserService]) -> UserReadDTO:
    user = api_user_dto_to_application_user_dto(user_dto=user_dto)
    return user_entity_to_dto(user_entity=await service.register_user(user_data=user))
