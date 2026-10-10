from abc import ABC, abstractmethod
from uuid import UUID

from modules.auth.domain.entities.credential import AuthCredentialEntity


class IAuthCredentialRepository(ABC):
    @abstractmethod
    async def create_auth_credential(self, auth_credential: AuthCredentialEntity) -> None:
        pass

    @abstractmethod
    async def get_auth_credential_by_user_id(self, user_id: UUID) -> AuthCredentialEntity | None:
        pass
