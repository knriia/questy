from abc import ABC, abstractmethod

from modules.user.domain.entities import UserEntity


class IUserRepository(ABC):
    @abstractmethod
    async def create_user(self, user: UserEntity) -> None:
        pass

    @abstractmethod
    async def get_user_by_email(self, email: str) -> UserEntity | None:
        pass

    @abstractmethod
    async def get_user_by_username(self, username: str) -> UserEntity | None:
        pass
