from datetime import UTC, datetime, timedelta
from unittest.mock import AsyncMock, Mock
from uuid import uuid7

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from modules.auth.domain.entities.refresh_token import AuthRefreshTokenEntity
from modules.auth.domain.entities.session import AuthSessionEntity
from modules.auth.infrastructure.mappers.refresh_token import refresh_token_entity_to_model
from modules.auth.infrastructure.mappers.session import auth_session_entity_to_model
from modules.auth.infrastructure.models.refresh_token import AuthRefreshTokenModel
from modules.auth.infrastructure.models.session import AuthSessionModel
from modules.auth.infrastructure.repositories.refresh_token import AuthRefreshTokenRepository
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
async def test_auth_session_repository_merges_updated_session() -> None:
    session = AsyncMock(spec=AsyncSession)
    auth_session = AuthSessionEntity.create(
        user_id=uuid7(),
        device_id_hash="device-hash",
        user_agent="test-agent",
        client_name="web",
        ip_created="192.0.2.1",
        expires_at=datetime.now(UTC) + timedelta(hours=1),
    )
    auth_session.revoke(datetime.now(UTC))

    await AuthSessionRepository(session).update_auth_session(auth_session)

    session.merge.assert_awaited_once()
    merged_model = session.merge.await_args.args[0]
    assert merged_model.id == auth_session.id
    assert merged_model.revoked_at == auth_session.revoked_at
    assert merged_model.expires_at == auth_session.expires_at
    assert merged_model.device_id_hash == auth_session.device_id_hash
    session.flush.assert_awaited_once_with()


@pytest.mark.asyncio
async def test_refresh_token_repository_flushes_new_token() -> None:
    session = AsyncMock(spec=AsyncSession)
    refresh_token = AuthRefreshTokenEntity.create(
        session_id=uuid7(),
        secret_hash="secret-hash",
        expires_at=datetime.now(UTC) + timedelta(hours=1),
    )

    await AuthRefreshTokenRepository(session).create_refresh_token(refresh_token)

    session.add.assert_called_once()
    session.flush.assert_awaited_once_with()


@pytest.mark.asyncio
@pytest.mark.parametrize("token_count", [0, 2])
async def test_refresh_token_repository_gets_tokens_by_session_id(token_count: int) -> None:
    session = AsyncMock(spec=AsyncSession)
    session_id = uuid7()
    tokens = [
        AuthRefreshTokenEntity.create(
            session_id=session_id,
            secret_hash=f"secret-hash-{index}",
            expires_at=datetime.now(UTC) + timedelta(hours=1),
        )
        for index in range(token_count)
    ]
    models = [refresh_token_entity_to_model(token) for token in tokens]
    result = Mock()
    result.scalars.return_value.all.return_value = models
    session.execute.return_value = result

    result_tokens = await AuthRefreshTokenRepository(session).get_auth_refresh_token_by_session_id(session_id)

    assert result_tokens == tokens
    statement = session.execute.await_args.args[0]
    assert "auth_refresh_tokens.session_id =" in str(statement)
    assert "auth_refresh_tokens.revoked_at IS NULL" in str(statement)
    assert session_id in statement.compile().params.values()


@pytest.mark.asyncio
async def test_refresh_token_repository_updates_revocation_time() -> None:
    session = AsyncMock(spec=AsyncSession)
    refresh_token = AuthRefreshTokenEntity.create(
        session_id=uuid7(),
        secret_hash="secret-hash",
        expires_at=datetime.now(UTC) + timedelta(hours=1),
    )
    refresh_token.revoke(datetime.now(UTC))

    await AuthRefreshTokenRepository(session).update_auth_refresh_token(refresh_token)

    statement = session.execute.await_args.args[0]
    assert str(statement) == (
        "UPDATE auth_refresh_tokens SET revoked_at=:revoked_at "
        "WHERE auth_refresh_tokens.id = :id_1 AND auth_refresh_tokens.revoked_at IS NULL"
    )
    assert refresh_token.id in statement.compile().params.values()
    assert refresh_token.revoked_at in statement.compile().params.values()
    session.flush.assert_awaited_once_with()


@pytest.mark.asyncio
@pytest.mark.parametrize("found", [True, False])
async def test_refresh_token_repository_gets_token_by_id(found: bool) -> None:
    session = AsyncMock(spec=AsyncSession)
    token = AuthRefreshTokenEntity.create(
        session_id=uuid7(),
        secret_hash="secret-hash",
        expires_at=datetime.now(UTC) + timedelta(hours=1),
    )
    session.get.return_value = refresh_token_entity_to_model(token) if found else None

    result = await AuthRefreshTokenRepository(session).get_auth_refresh_token_by_token_id(token.id)

    assert result == token if found else result is None
    session.get.assert_awaited_once_with(AuthRefreshTokenModel, token.id)
