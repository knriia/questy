from dishka import Provider, Scope, provide
from sqlalchemy.ext.asyncio import AsyncSession

from modules.auth.application.interface.credential import IAuthCredentialRepository
from modules.auth.application.interface.refresh_token import IAuthRefreshTokenRepository
from modules.auth.application.interface.session import IAuthSessionRepository
from modules.auth.application.service import AuthService
from modules.auth.infrastructure.password_hasher import Argon2PasswordHasher
from modules.auth.infrastructure.repositories.credential import AuthCredentialRepository
from modules.auth.infrastructure.repositories.refresh_token import AuthRefreshTokenRepository
from modules.auth.infrastructure.repositories.session import AuthSessionRepository
from modules.user.application.service import UserService
from shared.config import Settings
from shared.iuow import IUoW


class AuthProvider(Provider):
    @provide(scope=Scope.REQUEST)
    async def create_auth_service(
        self,
        user_service: UserService,
        auth_credential_repo: IAuthCredentialRepository,
        auth_session_repo: IAuthSessionRepository,
        refresh_token_repo: IAuthRefreshTokenRepository,
        uow: IUoW,
        password_hash: Argon2PasswordHasher,
        settings: Settings,
    ) -> AuthService:
        return AuthService(
            user_service=user_service,
            auth_credential_repo=auth_credential_repo,
            auth_session_repo=auth_session_repo,
            auth_refresh_token_repo=refresh_token_repo,
            uow=uow,
            password_hash=password_hash,
            settings=settings,
        )

    @provide(scope=Scope.REQUEST)
    async def create_auth_session_repository(self, session: AsyncSession) -> IAuthSessionRepository:
        return AuthSessionRepository(session=session)

    @provide(scope=Scope.REQUEST)
    async def create_refresh_token_repository(self, session: AsyncSession) -> IAuthRefreshTokenRepository:
        return AuthRefreshTokenRepository(session=session)

    @provide(scope=Scope.REQUEST)
    async def create_auth_credential_repository(self, session: AsyncSession) -> IAuthCredentialRepository:
        return AuthCredentialRepository(session=session)

    @provide(scope=Scope.APP)
    async def create_hasher(self) -> Argon2PasswordHasher:
        return Argon2PasswordHasher()
