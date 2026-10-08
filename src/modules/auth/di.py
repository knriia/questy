from dishka import Provider, Scope, provide
from sqlalchemy.ext.asyncio import AsyncSession

from modules.auth.application.service import AuthService
from modules.auth.infrastructure.password_hasher import Argon2PasswordHasher
from modules.auth.infrastructure.repositories.credential import AuthCredentialRepository
from modules.auth.infrastructure.repositories.refresh_token import RefreshTokenRepository
from modules.auth.infrastructure.repositories.session import AuthSessionRepository
from modules.user.application.service import UserService
from shared.config import Settings
from shared.uow import UoW


class AuthProvider(Provider):
    @provide(scope=Scope.REQUEST)
    async def create_auth_service(
        self,
        user_service: UserService,
        auth_credential_repo: AuthCredentialRepository,
        auth_session_repo: AuthSessionRepository,
        refresh_token_repo: RefreshTokenRepository,
        uow: UoW,
        password_hash: Argon2PasswordHasher,
        settings: Settings,
    ) -> AuthService:
        return AuthService(
            user_service=user_service,
            auth_credential_repo=auth_credential_repo,
            auth_session_repo=auth_session_repo,
            refresh_token_repo=refresh_token_repo,
            uow=uow,
            password_hash=password_hash,
            settings=settings,
        )

    @provide(scope=Scope.REQUEST)
    async def create_auth_session_repository(self, session: AsyncSession) -> AuthSessionRepository:
        return AuthSessionRepository(session=session)

    @provide(scope=Scope.REQUEST)
    async def create_refresh_token_repository(self, session: AsyncSession) -> RefreshTokenRepository:
        return RefreshTokenRepository(session=session)

    @provide(scope=Scope.REQUEST)
    async def create_auth_credential_repository(self, session: AsyncSession) -> AuthCredentialRepository:
        return AuthCredentialRepository(session=session)

    @provide(scope=Scope.APP)
    async def create_hasher(self) -> Argon2PasswordHasher:
        return Argon2PasswordHasher()
