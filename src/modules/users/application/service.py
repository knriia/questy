import logging

from modules.users.application.dto import RegisterUserInput
from modules.users.domain.entities.user import UserEntity
from modules.users.domain.entities.user_credential import UserCredentialEntity
from modules.users.domain.value_objects import Email, Password, Timezone, Username
from modules.users.infrastructure.password_hasher import Argon2PasswordHasher
from modules.users.infrastructure.repositories.user_credential_repository import UserCredentialRepository
from modules.users.infrastructure.repositories.user_repository import UserRepository
from shared.uow import UoW

logger = logging.getLogger(__name__)


class UserService:
    def __init__(
        self,
        user_repo: UserRepository,
        user_credential_repo: UserCredentialRepository,
        uow: UoW,
        password_hash: Argon2PasswordHasher,
    ):
        self._user_repo = user_repo
        self._user_credential_repo = user_credential_repo
        self._uow = uow
        self._password_hash = password_hash

    async def register_user(self, user_data: RegisterUserInput) -> UserEntity:
        user = UserEntity.create(
            username=Username(user_data.username),
            timezone=Timezone(user_data.timezone),
            email=Email(user_data.email),
        )
        password = Password(user_data.password)
        password_hash = await self._password_hash.hash(password.value)
        user_credential = UserCredentialEntity.create(user_id=user.id, password_hash=password_hash)
        async with self._uow:
            await self._user_repo.create_user(user=user)
            await self._user_credential_repo.create_user_credential(user_credential=user_credential)
            await self._uow.commit()

        logger.info("User registered: user_id=%s", user.id)
        return user
