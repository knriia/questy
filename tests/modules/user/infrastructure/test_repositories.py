from unittest.mock import AsyncMock

import pytest
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from modules.user.domain.entities import UserEntity
from modules.user.domain.exceptions import EmailAlreadyExistsError, UsernameAlreadyExistsError
from modules.user.domain.value_objects import Email, Timezone, Username
from modules.user.infrastructure.mappers import user_entity_to_model
from modules.user.infrastructure.models import UserModel
from modules.user.infrastructure.repositories import UserRepository

pytestmark = pytest.mark.unit


class ConstraintError(Exception):
    def __init__(self, constraint_name: str) -> None:
        super().__init__(constraint_name)
        self.constraint_name = constraint_name


def make_user() -> UserEntity:
    return UserEntity.create(username=Username("test_user"), email=Email("test@example.com"), timezone=Timezone("UTC"))


@pytest.mark.asyncio
async def test_user_repository_creates_user_and_flushes() -> None:
    session = AsyncMock(spec=AsyncSession)
    user = make_user()

    await UserRepository(session).create_user(user)

    model = session.add.call_args.args[0]
    assert isinstance(model, UserModel)
    assert model.id == user.id
    assert model.username == user.username.value
    assert model.email == user.email.value
    assert model.timezone == user.timezone.value
    session.add.assert_called_once_with(model)
    session.flush.assert_awaited_once_with()


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("constraint_name", "error_type"),
    [
        ("uq_users_email_not_deleted", EmailAlreadyExistsError),
        ("uq_users_username_not_deleted", UsernameAlreadyExistsError),
    ],
)
async def test_user_repository_maps_unique_constraint_errors(
    constraint_name: str,
    error_type: type[Exception],
) -> None:
    session = AsyncMock(spec=AsyncSession)
    error = IntegrityError("insert user", {}, Exception("constraint violation"))
    error.__cause__ = ConstraintError(constraint_name)
    session.flush.side_effect = error

    with pytest.raises(error_type) as caught:
        await UserRepository(session).create_user(make_user())

    assert caught.value.__cause__ is error
    session.flush.assert_awaited_once_with()


@pytest.mark.asyncio
async def test_user_repository_reraises_unrecognized_integrity_error() -> None:
    session = AsyncMock(spec=AsyncSession)
    error = IntegrityError("insert user", {}, Exception("unrelated constraint"))
    session.flush.side_effect = error

    with pytest.raises(IntegrityError) as caught:
        await UserRepository(session).create_user(make_user())

    assert caught.value is error


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("method_name", "column", "value"),
    [
        ("get_user_by_email", "email", "test@example.com"),
        ("get_user_by_username", "username", "test_user"),
    ],
)
@pytest.mark.parametrize("found", [True, False])
async def test_user_repository_gets_user_by_email_or_username(
    method_name: str,
    column: str,
    value: str,
    found: bool,
) -> None:
    session = AsyncMock(spec=AsyncSession)
    user = make_user()
    session.scalar.return_value = user_entity_to_model(user) if found else None

    result = await getattr(UserRepository(session), method_name)(value)

    assert result == user if found else result is None
    statement = session.scalar.await_args.args[0]
    assert f"users.{column} =" in str(statement)
    assert value in statement.compile().params.values()


@pytest.mark.asyncio
@pytest.mark.parametrize("found", [True, False])
async def test_user_repository_gets_user_by_id(found: bool) -> None:
    session = AsyncMock(spec=AsyncSession)
    user = make_user()
    session.get.return_value = user_entity_to_model(user) if found else None

    result = await UserRepository(session).get_user_by_id(user.id)

    assert result == user if found else result is None
    session.get.assert_awaited_once_with(UserModel, user.id)
