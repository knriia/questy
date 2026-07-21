from dishka import Provider, Scope, provide
from sqlalchemy.ext.asyncio import AsyncSession

from modules.users.application.service import UserService
from modules.users.infrastructure.password_hasher import Argon2PasswordHasher
from modules.users.infrastructure.repositories.user_credential_repository import UserCredentialRepository
from modules.users.infrastructure.repositories.user_repository import UserRepository
from shared.uow import UoW


class UserProvider(Provider):
    @provide(scope=Scope.REQUEST)
    async def create_user_repository(self, session: AsyncSession) -> UserRepository:
        return UserRepository(session=session)

    @provide(scope=Scope.REQUEST)
    async def create_user_credential_repository(self, session: AsyncSession) -> UserCredentialRepository:
        return UserCredentialRepository(session=session)

    @provide(scope=Scope.APP)
    async def create_hasher(self) -> Argon2PasswordHasher:
        return Argon2PasswordHasher()

    @provide(scope=Scope.REQUEST)
    async def create_user_service(
        self,
        user_repo: UserRepository,
        user_credential_repo: UserCredentialRepository,
        uow: UoW,
        password_hash: Argon2PasswordHasher,
    ) -> UserService:
        return UserService(
            user_repo=user_repo,
            user_credential_repo=user_credential_repo,
            uow=uow,
            password_hash=password_hash,
        )
