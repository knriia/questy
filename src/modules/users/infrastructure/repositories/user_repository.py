from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from modules.users.domain.entities.user import UserEntity
from modules.users.domain.exceptions import EmailAlreadyExistsError, UsernameAlreadyExistsError
from modules.users.infrastructure.mappers.user import user_entity_to_model


class UserRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_user(self, user: UserEntity) -> None:
        model = user_entity_to_model(user=user)
        self.session.add(model)

        try:
            await self.session.flush()
        except IntegrityError as error:
            constraint_name = self._get_constraint_name(error=error)
            if constraint_name == "uq_users_email_not_deleted":
                raise EmailAlreadyExistsError() from error

            if constraint_name == "uq_users_username_not_deleted":
                raise UsernameAlreadyExistsError() from error

            raise

    @staticmethod
    def _get_constraint_name(error: BaseException) -> str | None:
        current: BaseException | None = error

        while current is not None:
            constraint_name = getattr(current, "constraint_name", None)

            if isinstance(constraint_name, str):
                return constraint_name

            current = current.__cause__

        return None
