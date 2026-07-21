from modules.users.application.dto import RegisterUserInput
from modules.users.domain.entities.user import UserEntity
from modules.users.presentation.dto import UserCreateDTO, UserReadDTO


def user_entity_to_dto(user_entity: UserEntity) -> UserReadDTO:
    return UserReadDTO(
        id=user_entity.id,
        username=user_entity.username.value,
        timezone=user_entity.timezone.value,
        status=user_entity.status,
        email=user_entity.email.value,
        email_verified=user_entity.email_verified,
        created_at=user_entity.created_at,
        updated_at=user_entity.updated_at,
        deleted_at=user_entity.deleted_at,
    )


def api_user_dto_to_application_user_dto(user_dto: UserCreateDTO) -> RegisterUserInput:
    return RegisterUserInput(
        username=user_dto.username,
        timezone=user_dto.timezone,
        email=user_dto.email,
        password=user_dto.password,
    )
