from dataclasses import asdict
from typing import Any

import pytest
from fastapi import FastAPI

from modules.auth.application.dto import UserRegisterCommand
from tests.fakes.registration import RegistrationContext
from tests.support.asgi import post_json

pytestmark = pytest.mark.integration_no_db


@pytest.mark.asyncio
async def test_register_returns_201_normalized_public_user(
    registration_app: FastAPI, registration: RegistrationContext, register_command: UserRegisterCommand
) -> None:
    payload = asdict(register_command) | {"username": " KnRiia ", "email": " KNRIiA@EXAMPLE.COM "}
    status, body = await post_json(registration_app, "/auth/register", payload)
    assert status == 201
    assert set(body) == {"id", "username", "email", "timezone", "status", "created_at"}
    assert body["username"] == "knriia"
    assert body["email"] == "knriia@example.com"
    assert body["timezone"] == register_command.timezone
    assert body["status"] == "active"
    assert body["id"] == str(next(iter(registration.users.users)))
    assert "password" not in body
    assert "password_hash" not in body
    assert registration.uow.commit_count == 1


@pytest.mark.asyncio
@pytest.mark.parametrize("field", ["username", "email", "timezone", "password"])
async def test_register_rejects_missing_required_field_before_service(
    registration_app: FastAPI, registration: RegistrationContext, register_command: UserRegisterCommand, field: str
) -> None:
    payload = asdict(register_command)
    del payload[field]
    status, _ = await post_json(registration_app, "/auth/register", payload)
    assert status == 422
    assert registration.uow.enter_count == 0
    assert registration.hasher.passwords == []


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("username", "ab"),
        ("username", "a" * 31),
        ("email", "a" * 64 + "@" + "b" * 40 + ".com"),
        ("email", "e\u0301" + "a" * 62 + "@" + "b" * 32 + ".com"),
        ("timezone", "ab"),
        ("timezone", "a" * 101),
        ("password", "a" * 14),
        ("password", "a" * 101),
        ("password", None),
        ("username", 123),
    ],
)
async def test_register_rejects_invalid_request_before_service(
    registration_app: FastAPI,
    registration: RegistrationContext,
    register_command: UserRegisterCommand,
    field: str,
    value: Any,
) -> None:
    status, _ = await post_json(registration_app, "/auth/register", asdict(register_command) | {field: value})
    assert status == 422
    assert registration.uow.enter_count == 0
    assert registration.hasher.passwords == []


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("field", "value", "code"),
    [
        ("username", "user-name", "invalid_username"),
        ("username", "Пользователь", "invalid_username"),
        ("username", "Élodie", "invalid_username"),
        ("email", "invalid", "invalid_email"),
        ("email", "İ" + "a" * 60 + "@" + "b" * 34 + ".com", "invalid_email"),
        ("timezone", "Unknown/Zone", "invalid_timezone"),
        ("password", "e\u0301" * 14, "invalid_password"),
    ],
)
async def test_register_returns_domain_validation_error(
    registration_app: FastAPI,
    registration: RegistrationContext,
    register_command: UserRegisterCommand,
    field: str,
    value: str,
    code: str,
) -> None:
    status, body = await post_json(registration_app, "/auth/register", asdict(register_command) | {field: value})
    assert status == 422
    assert body["detail"]["code"] == code
    assert registration.users.users == registration.credentials.credentials == {}


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("username", "email", "code"),
    [
        (" KnRiia ", "other@example.com", "username_already_exists"),
        ("other_user", " KNRIiA@EXAMPLE.COM ", "email_already_exists"),
    ],
)
async def test_register_returns_409_for_duplicate_without_partial_records(
    registration_app: FastAPI,
    registration: RegistrationContext,
    register_command: UserRegisterCommand,
    username: str,
    email: str,
    code: str,
) -> None:
    first_status, _ = await post_json(registration_app, "/auth/register", asdict(register_command))
    assert first_status == 201
    status, body = await post_json(
        registration_app, "/auth/register", asdict(register_command) | {"username": username, "email": email}
    )
    assert status == 409
    assert body["detail"]["code"] == code
    assert len(registration.users.users) == len(registration.credentials.credentials) == 1
    assert registration.uow.commit_count == 1
