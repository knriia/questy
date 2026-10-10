from uuid import UUID

from modules.auth.application.interface.credential import IAuthCredentialRepository
from modules.auth.application.interface.refresh_token import IRefreshTokenRepository
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


class ForbiddenRefreshTokenRepository(IRefreshTokenRepository):
    async def create_refresh_token(self, refresh_token: AuthRefreshTokenEntity) -> None:
        raise AssertionError("Registration must not create a refresh token")
