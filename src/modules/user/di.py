from dishka import Provider, Scope, provide
from sqlalchemy.ext.asyncio import AsyncSession

from modules.user.application.interface import IUserRepository
from modules.user.application.service import UserService
from modules.user.infrastructure.repositories import UserRepository
from shared.iuow import IUoW


class UserProvider(Provider):
    @provide(scope=Scope.REQUEST)
    async def create_user_repository(self, session: AsyncSession) -> IUserRepository:
        return UserRepository(session=session)

    @provide(scope=Scope.REQUEST)
    async def create_user_service(
        self,
        user_repo: IUserRepository,
        uow: IUoW,
    ) -> UserService:
        return UserService(
            user_repo=user_repo,
            uow=uow,
        )
