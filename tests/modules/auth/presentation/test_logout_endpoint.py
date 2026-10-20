from http.cookies import SimpleCookie
from typing import Any
from uuid import UUID

import pytest
from fastapi import FastAPI

from modules.auth.application.dto import UserAuthCredentialCommand
from tests.fakes.auth_login import AuthLoginContext, add_login_user
from tests.support.asgi import post_json_with_headers

pytestmark = [pytest.mark.asyncio, pytest.mark.integration_no_db]


def auth_header(token: str) -> list[tuple[bytes, bytes]]:
    return [(b"authorization", f"Bearer {token}".encode())]


def cookie_headers(headers: list[tuple[bytes, bytes]]) -> dict[str, Any]:
    cookies: dict[str, Any] = {}
    for name, value in headers:
        if name.lower() == b"set-cookie":
            parsed = SimpleCookie()
            parsed.load(value.decode())
            cookies.update(parsed)
    return cookies


async def create_authenticated_session(context: AuthLoginContext) -> tuple[UUID, str]:
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
    return result.sid, result.access_token


async def test_logout_revokes_current_session_and_clears_auth_cookies(
    auth_login_app: FastAPI,
    auth_login: AuthLoginContext,
) -> None:
    session_id, access_token = await create_authenticated_session(auth_login)

    status, body, headers = await post_json_with_headers(
        auth_login_app,
        "/auth/logout",
        {},
        request_headers=auth_header(access_token),
    )

    assert status == 204
    assert body == {}
    assert auth_login.sessions.sessions[session_id].revoked_at is not None
    tokens = [token for token in auth_login.refresh_tokens.refresh_tokens.values() if token.session_id == session_id]
    assert tokens
    assert all(token.revoked_at == auth_login.sessions.sessions[session_id].revoked_at for token in tokens)
    assert auth_login.uow.commit_count == 2

    cookies = cookie_headers(headers)
    assert set(cookies) == {"refresh_token", "device_id", "csrf_token"}
    assert all(cookie["max-age"] == "0" for cookie in cookies.values())
    assert cookies["refresh_token"]["path"] == "/auth"
    assert cookies["device_id"]["path"] == "/auth"
    assert cookies["csrf_token"]["path"] == "/"


async def test_logout_requires_an_authenticated_session(auth_login_app: FastAPI, auth_login: AuthLoginContext) -> None:
    status, body, headers = await post_json_with_headers(auth_login_app, "/auth/logout", {})

    assert status == 401
    assert body["detail"]["code"] == "user_not_authenticated"
    assert cookie_headers(headers) == {}
    assert auth_login.uow.commit_count == 0
