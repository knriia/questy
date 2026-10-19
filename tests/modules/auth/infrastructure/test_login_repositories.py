from datetime import UTC, datetime, timedelta
from unittest.mock import AsyncMock
from uuid import uuid7

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from modules.auth.domain.entities.refresh_token import AuthRefreshTokenEntity
from modules.auth.domain.entities.session import AuthSessionEntity
from modules.auth.infrastructure.mappers.session import auth_session_entity_to_model
from modules.auth.infrastructure.models.session import AuthSessionModel
from modules.auth.infrastructure.repositories.refresh_token import RefreshTokenRepository
from modules.auth.infrastructure.repositories.session import AuthSessionRepository

pytestmark = pytest.mark.unit


@pytest.mark.asyncio
async def test_auth_session_repository_flushes_new_session() -> None:
    session = AsyncMock(spec=AsyncSession)
    auth_session = AuthSessionEntity.create(
        user_id=uuid7(),
        device_id_hash="device-hash",
        user_agent="test-agent",
        client_name="web",
        ip_created="192.0.2.1",
        expires_at=datetime.now(UTC) + timedelta(hours=1),
    )

    await AuthSessionRepository(session).create_auth_session(auth_session)

    session.add.assert_called_once()
    session.flush.assert_awaited_once_with()


@pytest.mark.asyncio
@pytest.mark.parametrize("found", [True, False])
async def test_auth_session_repository_gets_session_by_id(found: bool) -> None:
    session = AsyncMock(spec=AsyncSession)
    auth_session = AuthSessionEntity.create(
        user_id=uuid7(),
        device_id_hash="device-hash",
        user_agent="test-agent",
        client_name="web",
        ip_created="192.0.2.1",
        expires_at=datetime.now(UTC) + timedelta(hours=1),
    )
    session.get.return_value = auth_session_entity_to_model(auth_session) if found else None

    result = await AuthSessionRepository(session).get_auth_session_by_id(auth_session.id)

    assert result == auth_session if found else result is None
    session.get.assert_awaited_once_with(AuthSessionModel, auth_session.id)


@pytest.mark.asyncio
async def test_refresh_token_repository_flushes_new_token() -> None:
    session = AsyncMock(spec=AsyncSession)
    refresh_token = AuthRefreshTokenEntity.create(
        session_id=uuid7(),
        secret_hash="secret-hash",
        expires_at=datetime.now(UTC) + timedelta(hours=1),
    )

    await RefreshTokenRepository(session).create_refresh_token(refresh_token)

    session.add.assert_called_once()
    session.flush.assert_awaited_once_with()
