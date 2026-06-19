from dishka import Provider, Scope, provide
from sqlalchemy.ext.asyncio import AsyncSession

from src.modules.users.repository import UserRepository
from src.modules.users.service import UserService


class UserProvider(Provider):
    @provide(scope=Scope.REQUEST)
    async def create_user_repository(self, session: AsyncSession) -> UserRepository:
        return UserRepository(session=session)

    @provide(scope=Scope.REQUEST)
    async def create_user_service(self, user_repository: UserRepository) -> UserService:
        return UserService(repository=user_repository)
