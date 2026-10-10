from uuid import UUID

from modules.user.application.interface import IUserRepository
from modules.user.domain.entities import UserEntity
from modules.user.domain.exceptions import EmailAlreadyExistsError, UsernameAlreadyExistsError


class InMemoryUserRepository(IUserRepository):
    def __init__(self) -> None:
        self.users: dict[UUID, UserEntity] = {}

    async def create_user(self, user: UserEntity) -> None:
        for saved_user in self.users.values():
            if saved_user.is_deleted:
                continue
            if saved_user.email == user.email:
                raise EmailAlreadyExistsError()
            if saved_user.username == user.username:
                raise UsernameAlreadyExistsError()
        self.users[user.id] = user

    async def get_user_by_email(self, email: str) -> UserEntity | None:
        return next((user for user in self.users.values() if user.email.value == email), None)

    async def get_user_by_username(self, username: str) -> UserEntity | None:
        return next((user for user in self.users.values() if user.username.value == username), None)


class FailingUserRepository(InMemoryUserRepository):
    def __init__(self, error: Exception) -> None:
        super().__init__()
        self.error = error

    async def create_user(self, user: UserEntity) -> None:
        raise self.error
