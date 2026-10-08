from dishka import Provider, Scope, provide
from sqlalchemy.ext.asyncio import AsyncSession

from modules.user.application.service import UserService
from modules.user.infrastructure.repositories import UserRepository
from shared.uow import UoW


class UserProvider(Provider):
    @provide(scope=Scope.REQUEST)
    async def create_user_repository(self, session: AsyncSession) -> UserRepository:
        return UserRepository(session=session)

    @provide(scope=Scope.REQUEST)
    async def create_user_service(
        self,
        user_repo: UserRepository,
        uow: UoW,
    ) -> UserService:
        return UserService(
            user_repo=user_repo,
            uow=uow,
        )
