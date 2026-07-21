from modules.users.domain.entities.user_credential import UserCredentialEntity
from modules.users.infrastructure.models.user_credential_model import UserCredentialModel


def user_credential_entity_to_model(user_credential_entity: UserCredentialEntity) -> UserCredentialModel:
    return UserCredentialModel(
        user_id=user_credential_entity.user_id,
        password_hash=user_credential_entity.password_hash,
        created_at=user_credential_entity.created_at,
        password_changed_at=user_credential_entity.password_changed_at,
    )


def user_credential_model_to_entity(user_credential_model: UserCredentialModel) -> UserCredentialEntity:
    return UserCredentialEntity(
        user_id=user_credential_model.user_id,
        password_hash=user_credential_model.password_hash,
        created_at=user_credential_model.created_at,
        password_changed_at=user_credential_model.password_changed_at,
    )
