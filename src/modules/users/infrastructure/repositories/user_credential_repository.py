from sqlalchemy.ext.asyncio import AsyncSession

from modules.users.domain.entities.user_credential import UserCredentialEntity
from modules.users.infrastructure.mappers.user_credential import user_credential_entity_to_model


class UserCredentialRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_user_credential(self, user_credential: UserCredentialEntity) -> None:
        model = user_credential_entity_to_model(user_credential_entity=user_credential)
        self.session.add(model)
