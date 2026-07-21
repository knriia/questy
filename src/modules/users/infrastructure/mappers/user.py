from modules.users.domain.entities.user import UserEntity
from modules.users.domain.enums import UserStatus
from modules.users.domain.value_objects import Email, Timezone, Username
from modules.users.infrastructure.models.user_model import UserModel


def user_entity_to_model(user: UserEntity) -> UserModel:
    return UserModel(
        id=user.id,
        username=user.username.value,
        timezone=user.timezone.value,
        status=user.status,
        email=user.email.value,
        email_verified=user.email_verified,
        created_at=user.created_at,
        updated_at=user.updated_at,
        deleted_at=user.deleted_at,
    )


def user_model_to_entity(user_model: UserModel) -> UserEntity:
    return UserEntity(
        id=user_model.id,
        username=Username(user_model.username),
        timezone=Timezone(user_model.timezone),
        status=UserStatus(user_model.status),
        email=Email(user_model.email),
        email_verified=user_model.email_verified,
        created_at=user_model.created_at,
        updated_at=user_model.updated_at,
        deleted_at=user_model.deleted_at,
    )
