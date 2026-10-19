from abc import ABC, abstractmethod
from uuid import UUID

from modules.auth.domain.entities.session import AuthSessionEntity


class IAuthSessionRepository(ABC):
    @abstractmethod
    async def create_auth_session(self, auth_session: AuthSessionEntity) -> None:
        pass

    @abstractmethod
    async def get_auth_session_by_id(self, session_id: UUID) -> AuthSessionEntity | None:
        pass
