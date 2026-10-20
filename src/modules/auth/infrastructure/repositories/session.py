from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from modules.auth.application.interface.session import IAuthSessionRepository
from modules.auth.domain.entities.session import AuthSessionEntity
from modules.auth.infrastructure.mappers.session import auth_session_entity_to_model, auth_session_model_to_entity
from modules.auth.infrastructure.models import AuthSessionModel


class AuthSessionRepository(IAuthSessionRepository):
    def __init__(self, session: AsyncSession):
        self._session = session

    async def create_auth_session(self, auth_session: AuthSessionEntity) -> None:
        auth_session_model = auth_session_entity_to_model(auth_session_entity=auth_session)
        self._session.add(auth_session_model)
        await self._session.flush()

    async def get_auth_session_by_id(self, sid: UUID) -> AuthSessionEntity | None:
        result = await self._session.get(AuthSessionModel, sid)
        return auth_session_model_to_entity(auth_session_model=result) if result else None

    async def update_auth_session(self, auth_session: AuthSessionEntity) -> None:
        model = auth_session_entity_to_model(auth_session_entity=auth_session)
        await self._session.merge(model)
        await self._session.flush()
