from abc import ABC, abstractmethod
from uuid import UUID

from modules.auth.domain.entities.refresh_token import AuthRefreshTokenEntity


class IAuthRefreshTokenRepository(ABC):
    @abstractmethod
    async def create_refresh_token(self, refresh_token: AuthRefreshTokenEntity) -> None:
        pass

    @abstractmethod
    async def get_auth_refresh_token_by_session_id(self, session_id: UUID) -> list[AuthRefreshTokenEntity]:
        pass

    @abstractmethod
    async def update_auth_refresh_token(self, refresh_token: AuthRefreshTokenEntity) -> None:
        pass
