from http.cookies import SimpleCookie
from typing import Any

import pytest
from fastapi import FastAPI

from modules.auth.application.dto import UserAuthCredentialCommand
from tests.fakes.auth_login import AuthLoginContext, add_login_user
from tests.support.asgi import post_json_with_headers

pytestmark = pytest.mark.integration_no_db


def parse_cookies(headers: list[tuple[bytes, bytes]]) -> dict[str, Any]:
    cookies: dict[str, Any] = {}
    for name, value in headers:
        if name.lower() == b"set-cookie":
            parsed = SimpleCookie()
            parsed.load(value.decode())
            cookies.update(parsed)
    return cookies


@pytest.mark.asyncio
async def test_refresh_endpoint_rotates_auth_cookies(
    auth_login_app: FastAPI,
    auth_login: AuthLoginContext,
) -> None:
    user = add_login_user(auth_login)
    auth_login.hasher.results["stored-password-hash"] = True
    initial = await auth_login.service.auth_user(
        UserAuthCredentialCommand(
            identifier=user.username.value,
            password="correct password",
            ip_address="192.0.2.1",
            user_agent="pytest-agent",
            client_name="pytest",
        )
    )

    status, body, headers = await post_json_with_headers(
        auth_login_app,
        "/auth/refresh",
        {},
        request_headers=[
            (
                b"cookie",
                (
                    f"refresh_token={initial.refresh_token}; device_id={initial.device_id}; "
                    f"csrf_token={initial.csrf_token}"
                ).encode(),
            ),
            (b"csrf_token", initial.csrf_token.encode()),
        ],
    )

    assert status == 200
    assert set(body) == {"access_token", "access_token_expires_at", "csrf_token"}
    assert body["access_token"]
    assert body["csrf_token"]
    assert body["csrf_token"] != initial.csrf_token
    cookies = parse_cookies(headers)
    assert set(cookies) == {"refresh_token", "device_id", "csrf_token"}
    assert cookies["refresh_token"].value != initial.refresh_token
    assert cookies["device_id"].value != initial.device_id
    assert cookies["csrf_token"].value == body["csrf_token"]


@pytest.mark.asyncio
async def test_refresh_endpoint_rejects_missing_header(
    auth_login_app: FastAPI,
    auth_login: AuthLoginContext,
) -> None:
    status, body, headers = await post_json_with_headers(auth_login_app, "/auth/refresh", {})

    assert status == 422
    assert body["detail"][0]["loc"] == ["header", "csrf_token"]
    assert parse_cookies(headers) == {}
    assert auth_login.uow.enter_count == 0


@pytest.mark.asyncio
async def test_refresh_endpoint_rejects_missing_cookies(
    auth_login_app: FastAPI,
    auth_login: AuthLoginContext,
) -> None:
    status, body, headers = await post_json_with_headers(
        auth_login_app,
        "/auth/refresh",
        {},
        request_headers=[(b"csrf_token", b"present-header")],
    )

    assert status == 401
    assert body["detail"]["code"] == "user_not_authenticated"
    assert parse_cookies(headers) == {}
    assert auth_login.uow.enter_count == 0


def test_refresh_csrf_header_is_documented_in_openapi(auth_login_app: FastAPI) -> None:
    operation = auth_login_app.openapi()["paths"]["/auth/refresh"]["post"]

    assert {parameter["name"] for parameter in operation["parameters"] if parameter["in"] == "header"} == {"csrf_token"}
    assert next(parameter for parameter in operation["parameters"] if parameter["name"] == "csrf_token")["required"]
