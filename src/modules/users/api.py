from dishka.integrations.fastapi import FromDishka, inject
from fastapi import APIRouter

from src.modules.users.dto import UserCreateDTO, UserReadDTO
from src.modules.users.entities import UserEntity
from src.modules.users.service import UserService

user_router = APIRouter(prefix="/users", tags=["users"])


@user_router.post("")
@inject
async def create_user(user_dto: UserCreateDTO, service: FromDishka[UserService]) -> UserReadDTO:
    user = UserEntity.create(
        nickname=user_dto.nickname,
        username=user_dto.username,
        email=user_dto.email,
        telegram_id=user_dto.telegram_id,
    )
    created_user = await service.create_user(user=user)
    return UserReadDTO(
        id=created_user.id,
        nickname=created_user.nickname,
        username=created_user.username,
        email=created_user.email,
        telegram_id=created_user.telegram_id,
        created_at=created_user.created_at,
        updated_at=created_user.updated_at,
    )
