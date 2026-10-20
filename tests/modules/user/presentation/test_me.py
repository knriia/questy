from datetime import UTC, datetime, timedelta
from uuid import UUID, uuid7

import pytest
from fastapi import FastAPI

from modules.auth.application.dto import UserAuthCredentialCommand
from modules.user.domain.entities import UserEntity
from tests.fakes.auth_login import AuthLoginContext, add_login_user
from tests.support.asgi import get_json_with_headers

pytestmark = [pytest.mark.asyncio, pytest.mark.integration_no_db]


async def login_user(context: AuthLoginContext) -> tuple[UserEntity, str, UUID]:
    user = add_login_user(context)
    context.hasher.results["stored-password-hash"] = True
    result = await context.service.auth_user(
        UserAuthCredentialCommand(
            identifier=user.username.value,
            password="correct password",
            ip_address="192.0.2.1",
            user_agent="pytest-agent",
            client_name="pytest",
        )
    )
    return user, result.access_token, result.sid


def auth_header(token: str) -> list[tuple[bytes, bytes]]:
    return [(b"authorization", f"Bearer {token}".encode())]


@pytest.mark.asyncio
async def test_get_me_returns_profile_for_authenticated_user(
    user_me_app: FastAPI,
    user_me_context: AuthLoginContext,
) -> None:
    user, token, _ = await login_user(user_me_context)

    status, body, _ = await get_json_with_headers(user_me_app, "/users/me", request_headers=auth_header(token))

    assert status == 200
    assert body == {
        "id": str(user.id),
        "username": user.username.value,
        "timezone": user.timezone.value,
        "email": user.email.value,
    }


@pytest.mark.asyncio
async def test_get_me_rejects_missing_bearer_token(user_me_app: FastAPI) -> None:
    status, body, headers = await get_json_with_headers(user_me_app, "/users/me")

    assert status == 401
    assert body["detail"]["code"] == "user_not_authenticated"
    assert dict(headers)[b"www-authenticate"] == b"Bearer"


@pytest.mark.asyncio
async def test_get_me_rejects_malformed_bearer_token(user_me_app: FastAPI) -> None:
    status, body, headers = await get_json_with_headers(
        user_me_app,
        "/users/me",
        request_headers=auth_header("not-a-jwt"),
    )

    assert status == 401
    assert body["detail"]["code"] == "user_not_authenticated"
    assert body["detail"]["message"] == "Invalid access token"
    assert dict(headers)[b"www-authenticate"] == b"Bearer"


@pytest.mark.asyncio
async def test_get_me_rejects_token_when_session_is_missing(
    user_me_app: FastAPI,
    user_me_context: AuthLoginContext,
) -> None:
    _, token, session_id = await login_user(user_me_context)
    del user_me_context.sessions.sessions[session_id]

    status, body, _ = await get_json_with_headers(user_me_app, "/users/me", request_headers=auth_header(token))

    assert status == 401
    assert body["detail"]["code"] == "user_not_authenticated"


@pytest.mark.asyncio
@pytest.mark.parametrize("session_state", ["expired", "revoked"])
async def test_get_me_rejects_expired_or_revoked_session(
    user_me_app: FastAPI,
    user_me_context: AuthLoginContext,
    session_state: str,
) -> None:
    _, token, session_id = await login_user(user_me_context)
    session = user_me_context.sessions.sessions[session_id]
    if session_state == "expired":
        session.expires_at = datetime.now(UTC) - timedelta(seconds=1)
    else:
        session.revoked_at = datetime.now(UTC)

    status, body, _ = await get_json_with_headers(user_me_app, "/users/me", request_headers=auth_header(token))

    assert status == 401
    assert body["detail"]["code"] == "user_not_authenticated"


@pytest.mark.asyncio
async def test_get_me_rejects_token_when_session_user_does_not_match_subject(
    user_me_app: FastAPI,
    user_me_context: AuthLoginContext,
) -> None:
    _, token, session_id = await login_user(user_me_context)
    user_me_context.sessions.sessions[session_id].user_id = uuid7()

    status, body, _ = await get_json_with_headers(user_me_app, "/users/me", request_headers=auth_header(token))

    assert status == 401
    assert body["detail"]["code"] == "user_not_authenticated"


@pytest.mark.asyncio
async def test_get_me_returns_not_found_when_principal_user_is_missing(
    user_me_app: FastAPI,
    user_me_context: AuthLoginContext,
) -> None:
    user, token, _ = await login_user(user_me_context)
    del user_me_context.users.users[user.id]

    status, body, _ = await get_json_with_headers(user_me_app, "/users/me", request_headers=auth_header(token))

    assert status == 404
    assert body["detail"]["code"] == "user_not_found"
