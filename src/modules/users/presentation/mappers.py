from src.modules.users.domain.entities import SavedUserEntity, UserEntity
from src.modules.users.presentation.dto import UserCreateDTO, UserReadDTO


def user_entity_to_dto(user_entity: SavedUserEntity) -> UserReadDTO:
    return UserReadDTO(
        id=user_entity.id,
        nickname=user_entity.nickname,
        username=user_entity.username,
        email=user_entity.email,
        telegram_id=user_entity.telegram_id,
        created_at=user_entity.created_at,
        updated_at=user_entity.updated_at,
    )


def user_dto_to_entity(user_dto: UserCreateDTO) -> UserEntity:
    return UserEntity.create(
        nickname=user_dto.nickname,
        username=user_dto.username,
        email=user_dto.email,
        telegram_id=user_dto.telegram_id,
    )
