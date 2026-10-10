from dataclasses import dataclass
from types import TracebackType
from typing import Self

from modules.auth.application.service import AuthService
from modules.auth.infrastructure.password_hasher import Argon2PasswordHasher
from modules.user.application.service import UserService
from shared.config import Settings
from tests.fakes.auth_repository import (
    ForbiddenRefreshTokenRepository,
    ForbiddenSessionRepository,
    InMemoryCredentialRepository,
)
from tests.fakes.uow import FakeUoW
from tests.fakes.user_repository import InMemoryUserRepository


class RecordingPasswordHasher(Argon2PasswordHasher):
    def __init__(self) -> None:
        self.passwords: list[str] = []
        self.error: BaseException | None = None
        self.result = "test-password-hash"

    async def hash(self, password: str) -> str:
        self.passwords.append(password)
        if self.error is not None:
            raise self.error
        return self.result

    async def verify(self, password: str, password_hash: str) -> bool:
        raise AssertionError("Registration must not verify an existing password")


class RegistrationUoW(FakeUoW):
    def __init__(self, users: InMemoryUserRepository, credentials: InMemoryCredentialRepository) -> None:
        super().__init__()
        self.users = users
        self.credentials = credentials
        self.enter_count = 0
        self.commit_error: BaseException | None = None
        self.enter_error: BaseException | None = None
        self._saved_users = users.users.copy()
        self._saved_credentials = credentials.credentials.copy()

    async def __aenter__(self) -> Self:
        self.enter_count += 1
        if self.enter_error is not None:
            raise self.enter_error
        self._saved_users = self.users.users.copy()
        self._saved_credentials = self.credentials.credentials.copy()
        return self

    async def commit(self) -> None:
        await super().commit()
        if self.commit_error is not None:
            raise self.commit_error
        self._saved_users = self.users.users.copy()
        self._saved_credentials = self.credentials.credentials.copy()

    async def rollback(self) -> None:
        await super().rollback()
        self.users.users.clear()
        self.users.users.update(self._saved_users)
        self.credentials.credentials.clear()
        self.credentials.credentials.update(self._saved_credentials)

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        await self.rollback()


@dataclass
class RegistrationContext:
    service: AuthService
    users: InMemoryUserRepository
    credentials: InMemoryCredentialRepository
    uow: RegistrationUoW
    hasher: RecordingPasswordHasher


def create_registration_context(users: InMemoryUserRepository | None = None) -> RegistrationContext:
    users = users if users is not None else InMemoryUserRepository()
    credentials = InMemoryCredentialRepository()
    uow = RegistrationUoW(users, credentials)
    hasher = RecordingPasswordHasher()
    service = AuthService(
        user_service=UserService(user_repo=users, uow=uow),
        auth_credential_repo=credentials,
        auth_session_repo=ForbiddenSessionRepository(),
        refresh_token_repo=ForbiddenRefreshTokenRepository(),
        uow=uow,
        password_hash=hasher,
        settings=Settings.model_construct(),
    )
    return RegistrationContext(service, users, credentials, uow, hasher)
