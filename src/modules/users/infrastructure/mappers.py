from src.modules.users.domain.entities import SavedUserEntity, UserEntity
from src.modules.users.infrastructure.models import UserModel


def user_entity_to_model(user_entity: UserEntity) -> UserModel:
    return UserModel(
        id=user_entity.id,
        username=user_entity.username,
        nickname=user_entity.nickname,
        email=user_entity.email,
        telegram_id=user_entity.telegram_id,
    )


def user_model_to_entity(user_model: UserModel) -> SavedUserEntity:
    return SavedUserEntity(
        id=user_model.id,
        username=user_model.username,
        nickname=user_model.nickname,
        email=user_model.email,
        telegram_id=user_model.telegram_id,
        created_at=user_model.created_at,
        updated_at=user_model.updated_at,
    )
