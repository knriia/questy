from sqlalchemy import func, select, text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from modules.auth.application.service import AuthService
from modules.auth.domain.entities.credential import AuthCredentialEntity
from modules.auth.infrastructure.models.credential import AuthCredentialModel
from modules.auth.infrastructure.password_hasher import Argon2PasswordHasher
from modules.auth.infrastructure.repositories.credential import AuthCredentialRepository
from modules.user.application.service import UserService
from modules.user.infrastructure.models import UserModel
from modules.user.infrastructure.repositories import UserRepository
from shared.config import Settings
from shared.uow import UoW
from tests.fakes.auth_repository import ForbiddenRefreshTokenRepository, ForbiddenSessionRepository
from tests.fakes.registration import RecordingPasswordHasher


def service(
    session: AsyncSession,
    credential_repo: AuthCredentialRepository | None = None,
    hasher: Argon2PasswordHasher | None = None,
) -> AuthService:
    uow = UoW(session)
    return AuthService(
        user_service=UserService(UserRepository(session), uow),
        auth_credential_repo=credential_repo if credential_repo is not None else AuthCredentialRepository(session),
        auth_session_repo=ForbiddenSessionRepository(),
        refresh_token_repo=ForbiddenRefreshTokenRepository(),
        uow=uow,
        password_hash=hasher if hasher is not None else RecordingPasswordHasher(),
        settings=Settings.model_construct(),
    )


async def counts(db_sessions: async_sessionmaker[AsyncSession]) -> tuple[int, int]:
    async with db_sessions() as session:
        users = await session.scalar(select(func.count()).select_from(UserModel))
        credentials = await session.scalar(select(func.count()).select_from(AuthCredentialModel))
        assert users is not None and credentials is not None
        return users, credentials


class RejectingCredentialRepository(AuthCredentialRepository):
    async def create_auth_credential(self, auth_credential: AuthCredentialEntity) -> None:
        raise RuntimeError("Credential storage failed")


class InvalidCredentialRepository(AuthCredentialRepository):
    async def create_auth_credential(self, auth_credential: AuthCredentialEntity) -> None:
        self._session.add(
            AuthCredentialModel(
                user_id=auth_credential.user_id,
                password_hash=None,
                created_at=auth_credential.created_at,
                password_changed_at=auth_credential.password_changed_at,
            )
        )


class DatabaseErrorCredentialRepository(AuthCredentialRepository):
    async def create_auth_credential(self, auth_credential: AuthCredentialEntity) -> None:
        await self._session.execute(text("SELECT CAST('invalid' AS INTEGER)"))
