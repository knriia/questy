from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from modules.user.application.interface import IUserRepository
from modules.user.domain.entities import UserEntity
from modules.user.domain.exceptions import EmailAlreadyExistsError, UsernameAlreadyExistsError
from modules.user.infrastructure.mappers import user_entity_to_model, user_model_to_entity
from modules.user.infrastructure.models import UserModel


class UserRepository(IUserRepository):
    def __init__(self, session: AsyncSession):
        self._session = session

    async def create_user(self, user: UserEntity) -> None:
        model = user_entity_to_model(user=user)
        self._session.add(model)

        try:
            await self._session.flush()
        except IntegrityError as error:
            constraint_name = self._get_constraint_name(error=error)
            if constraint_name == "uq_users_email_not_deleted":
                raise EmailAlreadyExistsError() from error

            if constraint_name == "uq_users_username_not_deleted":
                raise UsernameAlreadyExistsError() from error

            raise

    async def get_user_by_email(self, email: str) -> UserEntity | None:
        stmt = select(UserModel).where(UserModel.email == email)
        result = await self._session.scalar(stmt)
        return user_model_to_entity(user_model=result) if result else None

    async def get_user_by_username(self, username: str) -> UserEntity | None:
        stmt = select(UserModel).where(UserModel.username == username)
        result = await self._session.scalar(stmt)
        return user_model_to_entity(user_model=result) if result else None

    @staticmethod
    def _get_constraint_name(error: BaseException) -> str | None:
        current: BaseException | None = error

        while current is not None:
            constraint_name = getattr(current, "constraint_name", None)

            if isinstance(constraint_name, str):
                return constraint_name

            current = current.__cause__

        return None
