from abc import ABC, abstractmethod

from modules.auth.domain.entities.refresh_token import AuthRefreshTokenEntity


class IRefreshTokenRepository(ABC):
    @abstractmethod
    async def create_refresh_token(self, refresh_token: AuthRefreshTokenEntity) -> None:
        pass
