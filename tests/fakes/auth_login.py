from dataclasses import dataclass
from datetime import UTC, datetime
from types import TracebackType
from typing import Self
from uuid import UUID

from modules.auth.application.service import AuthService
from modules.auth.domain.entities.credential import AuthCredentialEntity
from modules.auth.domain.entities.refresh_token import AuthRefreshTokenEntity
from modules.auth.domain.entities.session import AuthSessionEntity
from modules.auth.infrastructure.password_hasher import Argon2PasswordHasher
from modules.user.application.service import UserService
from modules.user.domain.entities import UserEntity
from modules.user.domain.enums import UserStatus
from modules.user.domain.value_objects import Email, Timezone, Username
from shared.config import Settings
from tests.fakes.auth_repository import (
    InMemoryCredentialRepository,
    InMemoryRefreshTokenRepository,
    InMemorySessionRepository,
)
from tests.fakes.uow import FakeUoW
from tests.fakes.user_repository import InMemoryUserRepository


class RecordingLoginPasswordHasher(Argon2PasswordHasher):
    def __init__(self) -> None:
        self.verify_calls: list[tuple[str, str]] = []
        self.results: dict[str, bool] = {}
        self.error: BaseException | None = None

    async def verify(self, password: str, password_hash: str) -> bool:
        self.verify_calls.append((password, password_hash))
        if self.error is not None:
            raise self.error
        return self.results.get(password_hash, False)

    async def hash(self, password: str) -> str:
        raise AssertionError("Login must not hash passwords")


class LoginUoW(FakeUoW):
    def __init__(
        self,
        sessions: InMemorySessionRepository,
        refresh_tokens: InMemoryRefreshTokenRepository,
    ) -> None:
        super().__init__()
        self.sessions = sessions
        self.refresh_tokens = refresh_tokens
        self.enter_count = 0
        self.enter_error: BaseException | None = None
        self.commit_error: BaseException | None = None
        self._sessions_before: dict[UUID, AuthSessionEntity] = {}
        self._refresh_tokens_before: dict[UUID, AuthRefreshTokenEntity] = {}
        self._committed = False

    async def __aenter__(self) -> Self:
        self.enter_count += 1
        if self.enter_error is not None:
            raise self.enter_error
        self._sessions_before = self.sessions.sessions.copy()
        self._refresh_tokens_before = self.refresh_tokens.refresh_tokens.copy()
        self._committed = False
        return self

    async def commit(self) -> None:
        self.commit_count += 1
        if self.commit_error is not None:
            raise self.commit_error
        self._committed = True

    async def rollback(self) -> None:
        self.rollback_count += 1
        if not self._committed:
            self.sessions.sessions.clear()
            self.sessions.sessions.update(self._sessions_before)
            self.refresh_tokens.refresh_tokens.clear()
            self.refresh_tokens.refresh_tokens.update(self._refresh_tokens_before)

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        await self.rollback()


@dataclass
class AuthLoginContext:
    service: AuthService
    users: InMemoryUserRepository
    credentials: InMemoryCredentialRepository
    sessions: InMemorySessionRepository
    refresh_tokens: InMemoryRefreshTokenRepository
    uow: LoginUoW
    hasher: RecordingLoginPasswordHasher
    settings: Settings


def create_auth_login_context() -> AuthLoginContext:
    users = InMemoryUserRepository()
    credentials = InMemoryCredentialRepository()
    sessions = InMemorySessionRepository()
    refresh_tokens = InMemoryRefreshTokenRepository()
    uow = LoginUoW(sessions=sessions, refresh_tokens=refresh_tokens)
    hasher = RecordingLoginPasswordHasher()
    settings = Settings.model_construct(
        DEVICE_ID_HMAC_KEY="device-key-for-tests-0123456789abcdef",
        AUTH_SESSION_TTL_SECONDS=86_400,
        ACCESS_TOKEN_TTL_SECONDS=900,
        REFRESH_TOKEN_HMAC_KEY="refresh-key-for-tests-0123456789abcdef",
        ACCESS_TOKEN_HMAC_KEY="access-key-for-tests-0123456789abcdef",
        CSRF_HMAC_KEY="csrf-key-for-tests-0123456789abcdef",
        JWT_ISSUER="questy-test",
        JWT_AUDIENCE="questy-test",
        AUTH_DUMMY_PASSWORD_HASH="$argon2id$dummy-test-hash",
    )
    service = AuthService(
        user_service=UserService(user_repo=users, uow=uow),
        auth_credential_repo=credentials,
        auth_session_repo=sessions,
        auth_refresh_token_repo=refresh_tokens,
        uow=uow,
        password_hash=hasher,
        settings=settings,
    )
    return AuthLoginContext(service, users, credentials, sessions, refresh_tokens, uow, hasher, settings)


def add_login_user(
    context: AuthLoginContext,
    *,
    username: str = "knriia",
    email: str = "knriia@example.com",
    status: UserStatus = UserStatus.ACTIVE,
    deleted: bool = False,
    with_credential: bool = True,
    credential_hash: str = "stored-password-hash",
) -> UserEntity:
    user = UserEntity.create(username=Username(username), timezone=Timezone("Asia/Tomsk"), email=Email(email))
    user.status = status
    if deleted:
        user.deleted_at = datetime.now(UTC)
    context.users.users[user.id] = user
    if with_credential:
        context.credentials.credentials[user.id] = AuthCredentialEntity.create(
            user_id=user.id,
            password_hash=credential_hash,
        )
    return user
