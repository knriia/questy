from http.cookies import SimpleCookie
from typing import Any

import pytest
from fastapi import FastAPI

from tests.fakes.auth_login import AuthLoginContext, add_login_user
from tests.support.asgi import post_json_with_headers

pytestmark = pytest.mark.integration_no_db
DEFAULT_TEST_SECRET = "correct password"


def login_payload(identifier: str = "knriia", secret: str = DEFAULT_TEST_SECRET) -> dict[str, str]:
    return {"identifier": identifier, "password": secret}


def parse_cookies(headers: list[tuple[bytes, bytes]]) -> dict[str, Any]:
    cookies: dict[str, Any] = {}
    for name, value in headers:
        if name.lower() == b"set-cookie":
            parsed = SimpleCookie()
            parsed.load(value.decode())
            cookies.update(parsed)
    return cookies


@pytest.mark.asyncio
async def test_login_returns_access_token_and_sets_session_cookies(
    auth_login_app: FastAPI,
    auth_login: AuthLoginContext,
) -> None:
    add_login_user(auth_login)
    auth_login.hasher.results["stored-password-hash"] = True

    status, body, headers = await post_json_with_headers(
        auth_login_app,
        "/auth/login",
        login_payload(identifier=" KNRIiA@EXAMPLE.COM "),
        request_headers=[(b"user-agent", b"pytest-agent"), (b"x-client-name", b"browser")],
        client=("198.51.100.4", 4567),
    )

    assert status == 200
    assert set(body) == {"access_token", "access_token_expires_at", "csrf_token"}
    assert body["access_token"]
    assert body["access_token_expires_at"]
    assert "refresh_token" not in body
    assert "device_id" not in body
    cookies = parse_cookies(headers)
    assert set(cookies) == {"refresh_token", "device_id", "csrf_token"}
    assert cookies["refresh_token"].value
    assert cookies["refresh_token"]["httponly"]
    assert cookies["refresh_token"]["secure"]
    assert cookies["refresh_token"]["samesite"] == "lax"
    assert cookies["refresh_token"]["path"] == "/auth"
    assert cookies["device_id"]["httponly"]
    assert cookies["device_id"]["secure"]
    assert cookies["device_id"]["path"] == "/auth"
    assert not cookies["csrf_token"]["httponly"]
    assert cookies["csrf_token"]["secure"]
    assert cookies["csrf_token"]["samesite"] == "lax"
    assert cookies["csrf_token"]["path"] == "/"
    max_ages = {int(cookie["max-age"]) for cookie in cookies.values()}
    assert len(max_ages) == 1
    assert next(iter(max_ages)) > 0
    assert cookies["csrf_token"].value == body["csrf_token"]

    session = next(iter(auth_login.sessions.sessions.values()))
    assert session.ip_created == "198.51.100.4"
    assert session.user_agent == "pytest-agent"
    assert session.client_name == "browser"


@pytest.mark.asyncio
async def test_login_uses_unknown_metadata_when_request_has_no_client_or_headers(
    auth_login_app: FastAPI,
    auth_login: AuthLoginContext,
) -> None:
    add_login_user(auth_login)
    auth_login.hasher.results["stored-password-hash"] = True

    status, _, _ = await post_json_with_headers(
        auth_login_app,
        "/auth/login",
        login_payload(),
        client=None,
    )

    assert status == 200
    session = next(iter(auth_login.sessions.sessions.values()))
    assert session.ip_created == "unknown"
    assert session.user_agent == "unknown"
    assert session.client_name == "unknown"


@pytest.mark.asyncio
@pytest.mark.parametrize("field", ["identifier", "password"])
async def test_login_rejects_missing_required_credentials_before_service(
    auth_login_app: FastAPI,
    auth_login: AuthLoginContext,
    field: str,
) -> None:
    payload = login_payload()
    del payload[field]

    status, _, headers = await post_json_with_headers(auth_login_app, "/auth/login", payload)

    assert status == 422
    assert parse_cookies(headers) == {}
    assert auth_login.hasher.verify_calls == []
    assert auth_login.uow.enter_count == 0


@pytest.mark.asyncio
async def test_login_returns_same_401_response_for_invalid_credentials(
    auth_login_app: FastAPI,
    auth_login: AuthLoginContext,
) -> None:
    status, body, headers = await post_json_with_headers(
        auth_login_app,
        "/auth/login",
        login_payload(identifier="not-registered"),
    )

    assert status == 401
    assert body == {"detail": {"code": "invalid_credentials", "message": "Invalid credentials."}}
    assert parse_cookies(headers) == {}
    assert auth_login.uow.enter_count == 0
