from modules.auth.domain.entities.refresh_token import AuthRefreshTokenEntity
from modules.auth.infrastructure.models.refresh_token import AuthRefreshTokenModel


def refresh_token_entity_to_model(refresh_token_entity: AuthRefreshTokenEntity) -> AuthRefreshTokenModel:
    return AuthRefreshTokenModel(
        id=refresh_token_entity.id,
        session_id=refresh_token_entity.session_id,
        replaced_by_id=refresh_token_entity.replaced_by_id,
        secret_hash=refresh_token_entity.secret_hash,
        expires_at=refresh_token_entity.expires_at,
        used_at=refresh_token_entity.used_at,
        revoked_at=refresh_token_entity.revoked_at,
    )


def refresh_token_model_to_entity(refresh_token_model: AuthRefreshTokenModel) -> AuthRefreshTokenEntity:
    return AuthRefreshTokenEntity(
        id=refresh_token_model.id,
        session_id=refresh_token_model.session_id,
        replaced_by_id=refresh_token_model.replaced_by_id,
        secret_hash=refresh_token_model.secret_hash,
        expires_at=refresh_token_model.expires_at,
        used_at=refresh_token_model.used_at,
        revoked_at=refresh_token_model.revoked_at,
    )
