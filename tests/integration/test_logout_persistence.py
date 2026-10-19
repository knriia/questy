from datetime import UTC, datetime, timedelta

import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from modules.auth.application.service import AuthService
from modules.auth.domain.entities.refresh_token import AuthRefreshTokenEntity
from modules.auth.domain.entities.session import AuthSessionEntity
from modules.auth.infrastructure.models.refresh_token import AuthRefreshTokenModel
from modules.auth.infrastructure.models.session import AuthSessionModel
from modules.auth.infrastructure.password_hasher import Argon2PasswordHasher
from modules.auth.infrastructure.repositories.credential import AuthCredentialRepository
from modules.auth.infrastructure.repositories.refresh_token import AuthRefreshTokenRepository
from modules.auth.infrastructure.repositories.session import AuthSessionRepository
from modules.user.application.service import UserService
from modules.user.domain.entities import UserEntity
from modules.user.domain.value_objects import Email, Timezone, Username
from modules.user.infrastructure.repositories import UserRepository
from shared.config import Settings
from shared.uow import UoW

pytestmark = [pytest.mark.asyncio, pytest.mark.integration_db]


async def test_logout_persists_revoked_session_and_refresh_tokens(
    db_sessions: async_sessionmaker[AsyncSession],
) -> None:
    async with db_sessions() as session:
        uow = UoW(session)
        user = UserEntity.create(
            username=Username("logout_user"),
            email=Email("logout@example.com"),
            timezone=Timezone("UTC"),
        )
        auth_session = AuthSessionEntity.create(
            user_id=user.id,
            device_id_hash="device-hash",
            user_agent="test-agent",
            client_name="web",
            ip_created="192.0.2.1",
            expires_at=datetime.now(UTC) + timedelta(hours=1),
        )
        active_tokens = [
            AuthRefreshTokenEntity.create(
                session_id=auth_session.id,
                secret_hash=f"secret-hash-{index}",
                expires_at=auth_session.expires_at,
            )
            for index in range(2)
        ]
        previously_revoked_token = AuthRefreshTokenEntity.create(
            session_id=auth_session.id,
            secret_hash="previously-revoked-secret-hash",
            expires_at=auth_session.expires_at,
        )
        previous_revocation_time = datetime.now(UTC) - timedelta(minutes=1)
        previously_revoked_token.revoke(previous_revocation_time)
        user_repository = UserRepository(session)
        session_repository = AuthSessionRepository(session)
        refresh_token_repository = AuthRefreshTokenRepository(session)

        async with uow:
            await user_repository.create_user(user)
            await session_repository.create_auth_session(auth_session)
            for token in [*active_tokens, previously_revoked_token]:
                await refresh_token_repository.create_refresh_token(token)
            await uow.commit()

        auth_service = AuthService(
            user_service=UserService(user_repository, uow),
            auth_credential_repo=AuthCredentialRepository(session),
            auth_session_repo=session_repository,
            auth_refresh_token_repo=refresh_token_repository,
            uow=uow,
            password_hash=Argon2PasswordHasher(),
            settings=Settings.model_construct(),
        )
        await auth_service.user_logout(auth_session.id)

    async with db_sessions() as verification_session:
        persisted_session = await verification_session.get(AuthSessionModel, auth_session.id)
        persisted_tokens = list(
            await verification_session.scalars(
                select(AuthRefreshTokenModel).where(AuthRefreshTokenModel.session_id == auth_session.id)
            )
        )

    assert persisted_session is not None and persisted_session.revoked_at is not None
    tokens_by_id = {token.id: token for token in persisted_tokens}
    assert len(tokens_by_id) == 3
    assert all(tokens_by_id[token.id].revoked_at == persisted_session.revoked_at for token in active_tokens)
    assert tokens_by_id[previously_revoked_token.id].revoked_at == previous_revocation_time
