from abc import ABC, abstractmethod

from modules.auth.domain.entities.session import AuthSessionEntity


class IAuthSessionRepository(ABC):
    @abstractmethod
    async def create_auth_session(self, auth_session: AuthSessionEntity) -> None:
        pass
