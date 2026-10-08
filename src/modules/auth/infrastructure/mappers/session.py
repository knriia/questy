from modules.auth.domain.entities.session import AuthSessionEntity
from modules.auth.infrastructure.models.session import AuthSessionModel


def auth_session_entity_to_model(auth_session_entity: AuthSessionEntity) -> AuthSessionModel:
    return AuthSessionModel(
        id=auth_session_entity.id,
        user_id=auth_session_entity.user_id,
        device_id_hash=auth_session_entity.device_id_hash,
        user_agent=auth_session_entity.user_agent,
        client_name=auth_session_entity.client_name,
        ip_created=auth_session_entity.ip_created,
        last_used_at=auth_session_entity.last_used_at,
        expires_at=auth_session_entity.expires_at,
        revoked_at=auth_session_entity.revoked_at,
        created_at=auth_session_entity.created_at,
    )


def auth_session_model_to_entity(auth_session_model: AuthSessionModel) -> AuthSessionEntity:
    return AuthSessionEntity(
        id=auth_session_model.id,
        user_id=auth_session_model.user_id,
        device_id_hash=auth_session_model.device_id_hash,
        user_agent=auth_session_model.user_agent,
        client_name=auth_session_model.client_name,
        ip_created=auth_session_model.ip_created,
        last_used_at=auth_session_model.last_used_at,
        expires_at=auth_session_model.expires_at,
        revoked_at=auth_session_model.revoked_at,
        created_at=auth_session_model.created_at,
    )
