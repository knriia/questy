import asyncio
import logging
from dataclasses import replace
from datetime import UTC
from unicodedata import normalize

import pytest

from modules.auth.application.dto import UserRegisterCommand
from modules.auth.domain.exceptions import InvalidPasswordError
from modules.user.domain.enums import UserStatus
from modules.user.domain.exceptions import (
    EmailAlreadyExistsError,
    InvalidEmailError,
    InvalidTimezoneError,
    InvalidUsernameError,
    UsernameAlreadyExistsError,
    UserValidationError,
)
from tests.fakes.registration import RegistrationContext, create_registration_context
from tests.fakes.user_repository import FailingUserRepository

pytestmark = pytest.mark.integration_no_db


@pytest.mark.asyncio
async def test_registration_saves_user_and_credentials_and_commits_once(
    registration: RegistrationContext, register_command: UserRegisterCommand, caplog: pytest.LogCaptureFixture
) -> None:
    command = replace(register_command, username=" KnRiia ", email=" KNRIiA@EXAMPLE.COM ", timezone=" Asia/Tomsk ")
    with caplog.at_level(logging.INFO, logger="modules.auth.application.service"):
        result = await registration.service.register_user(command)

    user = registration.users.users[result.user_id]
    credential = registration.credentials.credentials[result.user_id]
    assert len(registration.users.users) == len(registration.credentials.credentials) == 1
    assert result.username == user.username.value == "knriia"
    assert result.email == user.email.value == "knriia@example.com"
    assert result.timezone == user.timezone.value == "Asia/Tomsk"
    assert result.status == user.status == UserStatus.ACTIVE
    assert result.created_at == user.created_at
    assert result.user_id.version == 7
    assert user.email_verified is False
    assert user.deleted_at is None
    assert credential.user_id == user.id
    assert credential.password_hash == registration.hasher.result
    assert credential.password_hash != command.password
    assert credential.created_at == credential.password_changed_at
    assert credential.created_at.tzinfo is UTC
    assert registration.hasher.passwords == [command.password]
    assert registration.uow.enter_count == registration.uow.commit_count == registration.uow.rollback_count == 1
    assert str(result.user_id) in caplog.text
    assert command.password not in caplog.text
    assert credential.password_hash not in caplog.text
    assert command.password not in repr(command)
    assert not hasattr(result, "password")
    assert not hasattr(result, "password_hash")


@pytest.mark.asyncio
@pytest.mark.parametrize("password", ["a" * 15, "a" * 100, "  valid password  ", "e\u0301" * 15])
async def test_registration_hashes_valid_normalized_password(
    registration: RegistrationContext, register_command: UserRegisterCommand, password: str
) -> None:
    await registration.service.register_user(replace(register_command, password=password))
    assert registration.hasher.passwords == [normalize("NFC", password)]


@pytest.mark.asyncio
@pytest.mark.parametrize("password", ["", "a" * 14, "a" * 101, "e\u0301" * 14])
async def test_invalid_password_fails_before_hashing_or_transaction(
    registration: RegistrationContext, register_command: UserRegisterCommand, password: str
) -> None:
    with pytest.raises(InvalidPasswordError):
        await registration.service.register_user(replace(register_command, password=password))
    assert registration.hasher.passwords == []
    assert registration.uow.enter_count == registration.uow.commit_count == registration.uow.rollback_count == 0
    assert registration.users.users == registration.credentials.credentials == {}


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("field", "value", "error_type"),
    [
        ("username", "ab", InvalidUsernameError),
        ("username", "Пользователь", InvalidUsernameError),
        ("username", "Élodie", InvalidUsernameError),
        ("email", "invalid", InvalidEmailError),
        ("email", "a" * 64 + "@" + "b" * 32 + ".com", InvalidEmailError),
        ("email", "İ" + "a" * 60 + "@" + "b" * 34 + ".com", InvalidEmailError),
        ("timezone", "invalid", InvalidTimezoneError),
    ],
)
async def test_invalid_user_data_rolls_back_without_saving_credentials(
    registration: RegistrationContext,
    register_command: UserRegisterCommand,
    field: str,
    value: str,
    error_type: type[UserValidationError],
) -> None:
    with pytest.raises(error_type):
        await registration.service.register_user(replace(register_command, **{field: value}))
    assert registration.users.users == registration.credentials.credentials == {}
    assert registration.uow.enter_count == registration.uow.rollback_count == 1
    assert registration.uow.commit_count == 0


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("username", "email", "error_type"),
    [
        (" KnRiia ", "other@example.com", UsernameAlreadyExistsError),
        ("other_user", " KNRIiA@EXAMPLE.COM ", EmailAlreadyExistsError),
    ],
)
async def test_duplicate_registration_preserves_existing_user_and_credentials(
    registration: RegistrationContext,
    register_command: UserRegisterCommand,
    username: str,
    email: str,
    error_type: type[Exception],
) -> None:
    first = await registration.service.register_user(register_command)
    saved_credential = registration.credentials.credentials[first.user_id]
    with pytest.raises(error_type):
        await registration.service.register_user(replace(register_command, username=username, email=email))
    assert list(registration.users.users) == list(registration.credentials.credentials) == [first.user_id]
    assert registration.credentials.credentials[first.user_id] == saved_credential
    assert registration.uow.commit_count == 1
    assert registration.uow.rollback_count == 2


@pytest.mark.asyncio
@pytest.mark.parametrize("stage", ["hash", "enter", "user", "credential", "commit"])
async def test_registration_propagates_failures_without_partial_records_or_success_log(
    register_command: UserRegisterCommand, stage: str, caplog: pytest.LogCaptureFixture
) -> None:
    error = RuntimeError("Registration dependency failed")
    registration = create_registration_context(FailingUserRepository(error) if stage == "user" else None)
    if stage == "hash":
        registration.hasher.error = error
    elif stage == "enter":
        registration.uow.enter_error = error
    elif stage == "credential":
        registration.credentials.error = error
    elif stage == "commit":
        registration.uow.commit_error = error
    with (
        caplog.at_level(logging.INFO, logger="modules.auth.application.service"),
        pytest.raises(RuntimeError) as caught,
    ):
        await registration.service.register_user(register_command)
    assert caught.value is error
    assert registration.users.users == registration.credentials.credentials == {}
    assert registration.uow.commit_count == int(stage == "commit")
    assert registration.uow.rollback_count == int(stage in {"user", "credential", "commit"})
    assert "User registered" not in caplog.text


@pytest.mark.asyncio
async def test_cancelled_registration_rolls_back_user(
    registration: RegistrationContext, register_command: UserRegisterCommand
) -> None:
    registration.credentials.error = asyncio.CancelledError()
    with pytest.raises(asyncio.CancelledError):
        await registration.service.register_user(register_command)
    assert registration.users.users == registration.credentials.credentials == {}
    assert registration.uow.commit_count == 0
    assert registration.uow.rollback_count == 1


@pytest.mark.asyncio
@pytest.mark.parametrize("stage", ["hash", "enter", "credential", "commit"])
async def test_failed_registration_preserves_previously_committed_account(
    registration: RegistrationContext, register_command: UserRegisterCommand, stage: str
) -> None:
    first = await registration.service.register_user(register_command)
    saved_user = registration.users.users[first.user_id]
    saved_credential = registration.credentials.credentials[first.user_id]
    error = RuntimeError("Second registration failed")
    if stage == "hash":
        registration.hasher.error = error
    elif stage == "enter":
        registration.uow.enter_error = error
    elif stage == "credential":
        registration.credentials.error = error
    else:
        registration.uow.commit_error = error
    with pytest.raises(RuntimeError) as caught:
        await registration.service.register_user(
            replace(register_command, username="other_user", email="other@example.com")
        )
    assert caught.value is error
    assert registration.users.users == {first.user_id: saved_user}
    assert registration.credentials.credentials == {first.user_id: saved_credential}


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("email", "normalized"),
    [
        ("a" * 64 + "@" + "b" * 31 + ".com", "a" * 64 + "@" + "b" * 31 + ".com"),
        ("e\u0301" + "a" * 62 + "@" + "b" * 32 + ".com", "é" + "a" * 62 + "@" + "b" * 32 + ".com"),
    ],
    ids=["exactly-100", "unicode-composition-to-100"],
)
async def test_registration_accepts_email_at_normalized_length_limit(
    registration: RegistrationContext,
    register_command: UserRegisterCommand,
    email: str,
    normalized: str,
) -> None:
    result = await registration.service.register_user(replace(register_command, email=email))
    assert len(result.email) == 100
    assert result.email == registration.users.users[result.user_id].email.value == normalized
    assert result.user_id in registration.credentials.credentials
    assert registration.uow.commit_count == 1
