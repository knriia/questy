from modules.auth.domain.entities.credential import AuthCredentialEntity
from modules.auth.infrastructure.models.credential import AuthCredentialModel


def auth_credential_entity_to_model(auth_credential_entity: AuthCredentialEntity) -> AuthCredentialModel:
    return AuthCredentialModel(
        user_id=auth_credential_entity.user_id,
        password_hash=auth_credential_entity.password_hash,
        created_at=auth_credential_entity.created_at,
        password_changed_at=auth_credential_entity.password_changed_at,
    )


def auth_credential_model_to_entity(auth_credential_model: AuthCredentialModel) -> AuthCredentialEntity:
    return AuthCredentialEntity(
        user_id=auth_credential_model.user_id,
        password_hash=auth_credential_model.password_hash,
        created_at=auth_credential_model.created_at,
        password_changed_at=auth_credential_model.password_changed_at,
    )
