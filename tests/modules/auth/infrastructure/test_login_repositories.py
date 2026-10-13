from datetime import UTC, datetime, timedelta
from unittest.mock import AsyncMock
from uuid import uuid7

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from modules.auth.domain.entities.refresh_token import AuthRefreshTokenEntity
from modules.auth.domain.entities.session import AuthSessionEntity
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
