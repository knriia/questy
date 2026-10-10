from dataclasses import replace
from datetime import UTC
from uuid import UUID

import pytest

from modules.user.application.dto import UserCommand
from modules.user.application.service import UserService
from modules.user.domain.enums import UserStatus
from modules.user.domain.exceptions import (
    EmailAlreadyExistsError,
    InvalidEmailError,
    InvalidTimezoneError,
    InvalidUsernameError,
    UsernameAlreadyExistsError,
    UserValidationError,
)
from tests.fakes.uow import FakeUoW
from tests.fakes.user_repository import FailingUserRepository, InMemoryUserRepository

pytestmark = pytest.mark.unit


@pytest.fixture
def command() -> UserCommand:
    return UserCommand(username="knriia", email="knriia@example.com", timezone="Asia/Tomsk")


@pytest.mark.asyncio
async def test_create_user_normalizes_data_and_returns_saved_user(
    service: UserService,
    user_repo: InMemoryUserRepository,
    uow: FakeUoW,
) -> None:
    result = await service.create_user(
        UserCommand(username=" KnRiia_1 ", email=" KNRIiA@EXAMPLE.COM ", timezone=" Asia/Tomsk "),
    )

    assert len(user_repo.users) == 1
    saved_user = user_repo.users[result.user_id]

    assert saved_user.username.value == result.username == "knriia_1"
    assert saved_user.email.value == result.email == "knriia@example.com"
    assert saved_user.timezone.value == result.timezone == "Asia/Tomsk"
    assert isinstance(result.user_id, UUID)
    assert saved_user.id == result.user_id
    assert saved_user.status == result.status == UserStatus.ACTIVE
    assert saved_user.email_verified is False
    assert saved_user.deleted_at is None
    assert saved_user.created_at == saved_user.updated_at == result.created_at
    assert result.created_at.tzinfo is UTC

    assert uow.commit_count == 0
    assert uow.rollback_count == 0


@pytest.mark.asyncio
@pytest.mark.parametrize("username", ["abc", "a" * 30], ids=["minimum-length", "maximum-length"])
async def test_create_user_accepts_username_length_boundaries(
    service: UserService,
    command: UserCommand,
    username: str,
) -> None:
    result = await service.create_user(replace(command, username=username))

    assert result.username == username


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("field", "value", "error_type"),
    [
        pytest.param("username", "", InvalidUsernameError, id="empty-username"),
        pytest.param("username", " \t\n", InvalidUsernameError, id="whitespace-username"),
        pytest.param("username", "ab", InvalidUsernameError, id="short-username"),
        pytest.param("username", "a" * 31, InvalidUsernameError, id="long-username"),
        pytest.param("username", "1user", InvalidUsernameError, id="username-starts-with-digit"),
        pytest.param("username", "_user", InvalidUsernameError, id="username-starts-with-underscore"),
        pytest.param("username", "user-name", InvalidUsernameError, id="invalid-username-character"),
        pytest.param("email", "", InvalidEmailError, id="empty-email"),
        pytest.param("email", " \t\n", InvalidEmailError, id="whitespace-email"),
        pytest.param("email", "not-an-email", InvalidEmailError, id="invalid-email"),
        pytest.param("email", "user@", InvalidEmailError, id="email-without-domain"),
        pytest.param("timezone", "", InvalidTimezoneError, id="empty-timezone"),
        pytest.param("timezone", " \t\n", InvalidTimezoneError, id="whitespace-timezone"),
        pytest.param("timezone", "Tomsk", InvalidTimezoneError, id="unknown-timezone"),
        pytest.param("timezone", "../Tomsk", InvalidTimezoneError, id="invalid-timezone-path"),
    ],
)
async def test_create_user_rejects_invalid_data_before_saving(
    service: UserService,
    user_repo: InMemoryUserRepository,
    command: UserCommand,
    field: str,
    value: str,
    error_type: type[UserValidationError],
) -> None:
    with pytest.raises(error_type):
        await service.create_user(replace(command, **{field: value}))

    assert user_repo.users == {}


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("field", "value", "error_type"),
    [
        pytest.param("email", "another@example.com", UsernameAlreadyExistsError, id="duplicate-username"),
        pytest.param("username", "another_user", EmailAlreadyExistsError, id="duplicate-email"),
    ],
)
async def test_create_user_propagates_duplicate_errors(
    service: UserService,
    user_repo: InMemoryUserRepository,
    uow: FakeUoW,
    command: UserCommand,
    field: str,
    value: str,
    error_type: type[Exception],
) -> None:
    first = await service.create_user(command)

    with pytest.raises(error_type):
        await service.create_user(replace(command, **{field: value}))

    assert list(user_repo.users) == [first.user_id]
    assert uow.commit_count == 0
    assert uow.rollback_count == 0


@pytest.mark.asyncio
async def test_create_user_propagates_save_errors(uow: FakeUoW, command: UserCommand) -> None:
    error = RuntimeError("Storage write failed")
    user_repo = FailingUserRepository(error)
    service = UserService(user_repo=user_repo, uow=uow)

    with pytest.raises(RuntimeError) as caught:
        await service.create_user(command)

    assert caught.value is error
    assert user_repo.users == {}
    assert uow.commit_count == 0
    assert uow.rollback_count == 0


@pytest.mark.asyncio
async def test_create_user_assigns_distinct_ids(
    service: UserService,
    command: UserCommand,
) -> None:
    first = await service.create_user(command)
    second = await service.create_user(replace(command, username="another_user", email="another@example.com"))

    assert first.user_id != second.user_id


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("username", "email", "error_type"),
    [
        (" KnRiia ", "other@example.com", UsernameAlreadyExistsError),
        ("other_user", " KNRIiA@EXAMPLE.COM ", EmailAlreadyExistsError),
    ],
)
async def test_create_user_rejects_duplicates_after_normalization(
    service: UserService,
    user_repo: InMemoryUserRepository,
    command: UserCommand,
    username: str,
    email: str,
    error_type: type[Exception],
) -> None:
    first = await service.create_user(command)
    with pytest.raises(error_type):
        await service.create_user(replace(command, username=username, email=email))
    assert list(user_repo.users) == [first.user_id]


@pytest.mark.asyncio
async def test_create_user_assigns_uuid7(service: UserService, command: UserCommand) -> None:
    result = await service.create_user(command)
    assert result.user_id.version == 7
