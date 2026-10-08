import logging

from modules.user.application.dto import UserCommand, UserResult
from modules.user.domain.entities import UserEntity
from modules.user.domain.value_objects import Email, Timezone, Username
from modules.user.infrastructure.repositories import UserRepository
from shared.uow import UoW

logger = logging.getLogger(__name__)


class UserService:
    def __init__(
        self,
        user_repo: UserRepository,
        uow: UoW,
    ):
        self._user_repo = user_repo
        self._uow = uow

    async def create_user(self, user_command: UserCommand) -> UserResult:
        user = UserEntity.create(
            username=Username(user_command.username),
            timezone=Timezone(user_command.timezone),
            email=Email(user_command.email),
        )
        await self._user_repo.create_user(user=user)

        return UserResult(
            user_id=user.id,
            username=user.username.value,
            email=user.email.value,
            timezone=user.timezone.value,
            status=user.status,
            created_at=user.created_at,
        )

    async def get_user_by_username(self, username: str) -> UserEntity | None:
        return await self._user_repo.get_user_by_username(username=username)

    async def get_user_by_email(self, email: str) -> UserEntity | None:
        return await self._user_repo.get_user_by_email(email=email)
