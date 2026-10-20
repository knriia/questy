from uuid import UUID

from modules.auth.application.interface.credential import IAuthCredentialRepository
from modules.auth.application.interface.refresh_token import IAuthRefreshTokenRepository
from modules.auth.application.interface.session import IAuthSessionRepository
from modules.auth.domain.entities.credential import AuthCredentialEntity
from modules.auth.domain.entities.refresh_token import AuthRefreshTokenEntity
from modules.auth.domain.entities.session import AuthSessionEntity


class InMemoryCredentialRepository(IAuthCredentialRepository):
    def __init__(self) -> None:
        self.credentials: dict[UUID, AuthCredentialEntity] = {}
        self.error: BaseException | None = None

    async def create_auth_credential(self, auth_credential: AuthCredentialEntity) -> None:
        if self.error is not None:
            raise self.error
        if auth_credential.user_id in self.credentials:
            raise RuntimeError("Credentials already exist")
        self.credentials[auth_credential.user_id] = auth_credential

    async def get_auth_credential_by_user_id(self, user_id: UUID) -> AuthCredentialEntity | None:
        return self.credentials.get(user_id)


class ForbiddenSessionRepository(IAuthSessionRepository):
    async def create_auth_session(self, auth_session: AuthSessionEntity) -> None:
        raise AssertionError("Registration must not create a session")

    async def get_auth_session_by_id(self, sid: UUID) -> AuthSessionEntity | None:
        raise AssertionError("Registration must not retrieve a session")

    async def update_auth_session(self, auth_session: AuthSessionEntity) -> None:
        raise AssertionError("Registration must not update a session")


class ForbiddenRefreshTokenRepository(IAuthRefreshTokenRepository):
    async def create_refresh_token(self, refresh_token: AuthRefreshTokenEntity) -> None:
        raise AssertionError("Registration must not create a refresh token")

    async def get_auth_refresh_token_by_session_id(self, sid: UUID) -> list[AuthRefreshTokenEntity]:
        raise AssertionError("Registration must not retrieve refresh tokens")

    async def update_auth_refresh_token(self, refresh_token: AuthRefreshTokenEntity) -> None:
        raise AssertionError("Registration must not update a refresh token")

    async def get_auth_refresh_token_by_token_id(self, token_id: UUID) -> AuthRefreshTokenEntity | None:
        raise AssertionError("Registration must not retrieve a refresh token by token id")


class InMemorySessionRepository(IAuthSessionRepository):
    def __init__(self) -> None:
        self.sessions: dict[UUID, AuthSessionEntity] = {}
        self.error: BaseException | None = None

    async def create_auth_session(self, auth_session: AuthSessionEntity) -> None:
        if self.error is not None:
            raise self.error
        self.sessions[auth_session.id] = auth_session

    async def get_auth_session_by_id(self, sid: UUID) -> AuthSessionEntity | None:
        return self.sessions.get(sid)

    async def update_auth_session(self, auth_session: AuthSessionEntity) -> None:
        if self.error is not None:
            raise self.error
        self.sessions[auth_session.id] = auth_session


class InMemoryRefreshTokenRepository(IAuthRefreshTokenRepository):
    def __init__(self) -> None:
        self.refresh_tokens: dict[UUID, AuthRefreshTokenEntity] = {}
        self.error: BaseException | None = None

    async def create_refresh_token(self, refresh_token: AuthRefreshTokenEntity) -> None:
        if self.error is not None:
            raise self.error
        self.refresh_tokens[refresh_token.id] = refresh_token

    async def get_auth_refresh_token_by_session_id(self, sid: UUID) -> list[AuthRefreshTokenEntity]:
        return [token for token in self.refresh_tokens.values() if token.session_id == sid and token.revoked_at is None]

    async def get_auth_refresh_token_by_token_id(self, token_id: UUID) -> AuthRefreshTokenEntity | None:
        return self.refresh_tokens.get(token_id)

    async def update_auth_refresh_token(self, refresh_token: AuthRefreshTokenEntity) -> None:
        if self.error is not None:
            raise self.error
        self.refresh_tokens[refresh_token.id] = refresh_token
