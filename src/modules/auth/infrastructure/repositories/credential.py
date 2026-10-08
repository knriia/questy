from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from modules.auth.domain.entities.credential import AuthCredentialEntity
from modules.auth.infrastructure.mappers.credential import (
    auth_credential_entity_to_model,
    auth_credential_model_to_entity,
)
from modules.auth.infrastructure.models.credential import AuthCredentialModel


class AuthCredentialRepository:
    def __init__(self, session: AsyncSession):
        self._session = session

    async def create_auth_credential(self, auth_credential: AuthCredentialEntity) -> None:
        model = auth_credential_entity_to_model(auth_credential_entity=auth_credential)
        self._session.add(model)

    async def get_auth_credential_by_user_id(self, user_id: UUID) -> AuthCredentialEntity | None:
        result = await self._session.get(AuthCredentialModel, user_id)
        return auth_credential_model_to_entity(auth_credential_model=result) if result else None
