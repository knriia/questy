from src.modules.users.entities import SavedUserEntity, UserEntity
from src.modules.users.repository import UserRepository


class UserService:
    def __init__(self, repository: UserRepository):
        self.repository = repository

    async def create_user(self, user: UserEntity) -> SavedUserEntity:
        return await self.repository.save_user(user)
