from sqlalchemy.ext.asyncio import AsyncSession

from modules.auth.application.interface.refresh_token import IRefreshTokenRepository
from modules.auth.domain.entities.refresh_token import AuthRefreshTokenEntity
from modules.auth.infrastructure.mappers.refresh_token import refresh_token_entity_to_model


class RefreshTokenRepository(IRefreshTokenRepository):
    def __init__(self, session: AsyncSession):
        self._session = session

    async def create_refresh_token(self, refresh_token: AuthRefreshTokenEntity) -> None:
        refresh_token_model = refresh_token_entity_to_model(refresh_token)
        self._session.add(refresh_token_model)
