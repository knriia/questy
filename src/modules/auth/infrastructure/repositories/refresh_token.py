from uuid import UUID

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from modules.auth.application.interface.refresh_token import IAuthRefreshTokenRepository
from modules.auth.domain.entities.refresh_token import AuthRefreshTokenEntity
from modules.auth.infrastructure.mappers.refresh_token import (
    refresh_token_entity_to_model,
    refresh_token_model_to_entity,
)
from modules.auth.infrastructure.models import AuthRefreshTokenModel


class AuthRefreshTokenRepository(IAuthRefreshTokenRepository):
    def __init__(self, session: AsyncSession):
        self._session = session

    async def create_refresh_token(self, refresh_token: AuthRefreshTokenEntity) -> None:
        refresh_token_model = refresh_token_entity_to_model(refresh_token)
        self._session.add(refresh_token_model)
        await self._session.flush()

    async def get_auth_refresh_token_by_session_id(self, sid: UUID) -> list[AuthRefreshTokenEntity]:
        result = await self._session.execute(
            select(AuthRefreshTokenModel).where(
                AuthRefreshTokenModel.session_id == sid, AuthRefreshTokenModel.revoked_at.is_(None)
            )
        )
        models = result.scalars().all()
        return [refresh_token_model_to_entity(refresh_token_model=model) for model in models]

    async def update_auth_refresh_token(self, refresh_token: AuthRefreshTokenEntity) -> None:
        await self._session.execute(
            update(AuthRefreshTokenModel)
            .where(AuthRefreshTokenModel.id == refresh_token.id, AuthRefreshTokenModel.revoked_at.is_(None))
            .values(revoked_at=refresh_token.revoked_at)
        )
        await self._session.flush()

    async def get_auth_refresh_token_by_token_id(self, token_id: UUID) -> AuthRefreshTokenEntity | None:
        result = await self._session.get(AuthRefreshTokenModel, token_id)
        return refresh_token_model_to_entity(refresh_token_model=result) if result else None
