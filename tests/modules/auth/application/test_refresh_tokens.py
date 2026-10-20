from datetime import UTC, datetime, timedelta
from uuid import UUID, uuid7

import pytest

from modules.auth.domain.entities.refresh_token import AuthRefreshTokenEntity
from modules.auth.domain.entities.session import AuthSessionEntity
from modules.auth.domain.exceptions import UnauthenticatedError
from tests.fakes.auth_login import AuthLoginContext

pytestmark = pytest.mark.integration_no_db


def add_refresh_credentials(
    context: AuthLoginContext,
) -> tuple[AuthSessionEntity, AuthRefreshTokenEntity, str, str, str]:
    now = datetime.now(UTC)
    device_id = "current-device-id"
    session = AuthSessionEntity.create(
        user_id=uuid7(),
        device_id_hash=context.service._create_device_id_hash(device_id),
        user_agent="pytest-agent",
        client_name="pytest",
        ip_created="192.0.2.10",
        expires_at=now + timedelta(hours=1),
    )
    refresh_secret = "current-refresh-secret"
    refresh_token = AuthRefreshTokenEntity.create(
        session_id=session.id,
        secret_hash=context.service._create_secret_hash_refresh_token(refresh_secret),
        expires_at=session.expires_at,
    )
    context.sessions.sessions[session.id] = session
    context.refresh_tokens.refresh_tokens[refresh_token.id] = refresh_token
    csrf_token = context.service._create_csrf_token(session.id, "csrf-nonce")
    return session, refresh_token, f"{refresh_token.id}.{refresh_secret}", device_id, csrf_token


@pytest.mark.asyncio
async def test_refresh_rotates_tokens_and_session_device(auth_login: AuthLoginContext) -> None:
    session, old_token, presented_token, device_id, csrf_token = add_refresh_credentials(auth_login)

    result = await auth_login.service.update_refresh_and_access_tokens(
        refresh_token=presented_token,
        device_id=device_id,
        csrf_token=csrf_token,
        csrf_token_from_header=csrf_token,
    )

    new_token_id, new_secret = result.refresh_token.split(".")
    new_token = auth_login.refresh_tokens.refresh_tokens[UUID(new_token_id)]
    assert old_token.revoked_at is not None
    assert new_token.session_id == session.id
    assert new_token.secret_hash == auth_login.service._create_secret_hash_refresh_token(new_secret)
    assert new_token.expires_at == result.refresh_token_expires_at == session.expires_at
    assert session.device_id_hash == auth_login.service._create_device_id_hash(result.device_id)
    assert result.sid == session.id
    assert result.access_token
    assert result.access_token_expires_at > datetime.now(UTC)
    assert auth_login.service._comp_csrf_tokens(result.csrf_token, result.csrf_token, session.id)
    assert auth_login.uow.enter_count == auth_login.uow.commit_count == auth_login.uow.rollback_count == 1
    assert len(auth_login.refresh_tokens.refresh_tokens) == 2


@pytest.mark.asyncio
@pytest.mark.parametrize("presented_token", ["", "not-a-token", "id.secret.extra"])
async def test_refresh_rejects_token_with_invalid_shape(
    auth_login: AuthLoginContext,
    presented_token: str,
) -> None:
    with pytest.raises(UnauthenticatedError):
        await auth_login.service.update_refresh_and_access_tokens(
            refresh_token=presented_token,
            device_id="device",
            csrf_token="csrf",
            csrf_token_from_header="csrf",
        )

    assert auth_login.uow.enter_count == 0


@pytest.mark.asyncio
async def test_refresh_rejects_token_with_invalid_uuid(auth_login: AuthLoginContext) -> None:
    with pytest.raises(UnauthenticatedError):
        await auth_login.service.update_refresh_and_access_tokens(
            refresh_token="not-a-uuid.secret",
            device_id="device",
            csrf_token="csrf",
            csrf_token_from_header="csrf",
        )

    assert auth_login.uow.enter_count == 0


@pytest.mark.asyncio
async def test_refresh_rejects_unknown_token(auth_login: AuthLoginContext) -> None:
    with pytest.raises(UnauthenticatedError):
        await auth_login.service.update_refresh_and_access_tokens(
            refresh_token=f"{uuid7()}.secret",
            device_id="device",
            csrf_token="csrf",
            csrf_token_from_header="csrf",
        )

    assert auth_login.uow.enter_count == 0


@pytest.mark.asyncio
async def test_refresh_rejects_wrong_secret(auth_login: AuthLoginContext) -> None:
    _, token, _, device_id, csrf_token = add_refresh_credentials(auth_login)

    with pytest.raises(UnauthenticatedError):
        await auth_login.service.update_refresh_and_access_tokens(
            refresh_token=f"{token.id}.wrong-secret",
            device_id=device_id,
            csrf_token=csrf_token,
            csrf_token_from_header=csrf_token,
        )

    assert auth_login.uow.enter_count == 0


@pytest.mark.asyncio
@pytest.mark.parametrize("inactive_state", ["expired", "revoked", "used"])
async def test_refresh_rejects_inactive_refresh_token(
    auth_login: AuthLoginContext,
    inactive_state: str,
) -> None:
    _, token, presented_token, device_id, csrf_token = add_refresh_credentials(auth_login)
    if inactive_state == "expired":
        token.expires_at = datetime.now(UTC) - timedelta(seconds=1)
    elif inactive_state == "revoked":
        token.revoke(datetime.now(UTC))
    else:
        token.used_at = datetime.now(UTC)

    with pytest.raises(UnauthenticatedError):
        await auth_login.service.update_refresh_and_access_tokens(
            refresh_token=presented_token,
            device_id=device_id,
            csrf_token=csrf_token,
            csrf_token_from_header=csrf_token,
        )

    assert auth_login.uow.enter_count == 0


@pytest.mark.asyncio
@pytest.mark.parametrize("csrf_failure", ["header_mismatch", "malformed", "invalid_signature"])
async def test_refresh_rejects_invalid_csrf_token(
    auth_login: AuthLoginContext,
    csrf_failure: str,
) -> None:
    _, _, presented_token, device_id, valid_csrf = add_refresh_credentials(auth_login)
    if csrf_failure == "header_mismatch":
        csrf_cookie, csrf_header = valid_csrf, "different"
    elif csrf_failure == "malformed":
        csrf_cookie = csrf_header = ""
    else:
        csrf_cookie = csrf_header = "nonce." + "0" * 64

    with pytest.raises(UnauthenticatedError):
        await auth_login.service.update_refresh_and_access_tokens(
            refresh_token=presented_token,
            device_id=device_id,
            csrf_token=csrf_cookie,
            csrf_token_from_header=csrf_header,
        )

    assert auth_login.uow.enter_count == 0


@pytest.mark.asyncio
@pytest.mark.parametrize("session_state", ["missing", "inactive", "wrong_device"])
async def test_refresh_rejects_missing_or_invalid_session(
    auth_login: AuthLoginContext,
    session_state: str,
) -> None:
    session, _, presented_token, device_id, csrf_token = add_refresh_credentials(auth_login)
    if session_state == "missing":
        del auth_login.sessions.sessions[session.id]
    elif session_state == "inactive":
        session.revoke(datetime.now(UTC))
    else:
        device_id = "different-device-id"

    with pytest.raises(UnauthenticatedError):
        await auth_login.service.update_refresh_and_access_tokens(
            refresh_token=presented_token,
            device_id=device_id,
            csrf_token=csrf_token,
            csrf_token_from_header=csrf_token,
        )

    assert auth_login.uow.enter_count == 0
