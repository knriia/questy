import asyncio
from dataclasses import replace
from datetime import UTC, datetime
from uuid import uuid7

import pytest
from sqlalchemy.exc import DBAPIError, IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from modules.auth.application.dto import UserRegisterCommand
from modules.auth.domain.entities.credential import AuthCredentialEntity
from modules.auth.infrastructure.models.credential import AuthCredentialModel
from modules.auth.infrastructure.password_hasher import Argon2PasswordHasher
from modules.auth.infrastructure.repositories.credential import AuthCredentialRepository
from modules.user.domain.entities import UserEntity
from modules.user.domain.enums import UserStatus
from modules.user.domain.exceptions import (
    EmailAlreadyExistsError,
    InvalidEmailError,
    InvalidUsernameError,
    UsernameAlreadyExistsError,
)
from modules.user.domain.value_objects import Email, Timezone, Username
from modules.user.infrastructure.models import UserModel
from modules.user.infrastructure.repositories import UserRepository
from shared.uow import UoW
from tests.support.registration_db import (
    DatabaseErrorCredentialRepository,
    InvalidCredentialRepository,
    RejectingCredentialRepository,
    counts,
    service,
)

pytestmark = [pytest.mark.asyncio, pytest.mark.integration_db]


def command() -> UserRegisterCommand:
    return UserRegisterCommand(
        username="test_user", email="test@example.com", timezone="UTC", password="valid password phrase"
    )


async def test_registration_persists_user_and_real_password_hash(db_sessions: async_sessionmaker[AsyncSession]) -> None:
    data = replace(command(), username=" Test_User ", email=" TEST@EXAMPLE.COM ", timezone=" UTC ")
    hasher = Argon2PasswordHasher()
    async with db_sessions() as session:
        auth = service(session, hasher=hasher)
        result = await auth.register_user(data)
    async with db_sessions() as session:
        user = await UserRepository(session).get_user_by_email(result.email)
        credential = await AuthCredentialRepository(session).get_auth_credential_by_user_id(result.user_id)
        assert user is not None and credential is not None
        assert user.id == result.user_id
        assert user.username.value == result.username == "test_user"
        assert user.email.value == result.email == "test@example.com"
        assert user.timezone.value == result.timezone == "UTC"
        assert user.status == result.status == UserStatus.ACTIVE
        assert user.created_at == result.created_at == user.updated_at
        assert user.email_verified is False and user.deleted_at is None
        assert credential.created_at == credential.password_changed_at
        assert credential.created_at.tzinfo is not None
        assert await hasher.verify(data.password, credential.password_hash)
        assert not await hasher.verify("wrong password", credential.password_hash)
        assert await UserRepository(session).get_user_by_username(result.username) == user
    assert await counts(db_sessions) == (1, 1)


@pytest.mark.parametrize(
    ("username", "email", "error_type"),
    [
        (" TEST_USER ", "other@example.com", UsernameAlreadyExistsError),
        ("other_user", " TEST@EXAMPLE.COM ", EmailAlreadyExistsError),
    ],
)
async def test_duplicate_registration_returns_domain_error_and_preserves_records(
    db_sessions: async_sessionmaker[AsyncSession], username: str, email: str, error_type: type[Exception]
) -> None:
    async with db_sessions() as session:
        first = await service(session).register_user(command())
    async with db_sessions() as session:
        with pytest.raises(error_type):
            await service(session).register_user(replace(command(), username=username, email=email))
    assert await counts(db_sessions) == (1, 1)
    async with db_sessions() as session:
        assert await session.get(AuthCredentialModel, first.user_id) is not None


@pytest.mark.parametrize("collision", ["email", "username"])
async def test_concurrent_registration_saves_only_one_complete_account(
    db_sessions: async_sessionmaker[AsyncSession], collision: str
) -> None:
    ready = asyncio.Event()
    entered = 0

    async def register(index: int) -> object:
        nonlocal entered
        data = replace(
            command(),
            username="same_user" if collision == "username" else f"user_{index}",
            email="same@example.com" if collision == "email" else f"user{index}@example.com",
        )
        async with db_sessions() as session:
            entered += 1
            if entered == 2:
                ready.set()
            await ready.wait()
            return await service(session).register_user(data)

    results = await asyncio.wait_for(asyncio.gather(register(1), register(2), return_exceptions=True), timeout=15)
    error_type = EmailAlreadyExistsError if collision == "email" else UsernameAlreadyExistsError
    assert sum(isinstance(result, error_type) for result in results) == 1
    assert sum(not isinstance(result, BaseException) for result in results) == 1
    assert await counts(db_sessions) == (1, 1)


@pytest.mark.parametrize("failure", ["credential", "commit"])
async def test_registration_rolls_back_both_records_on_storage_failure(
    db_sessions: async_sessionmaker[AsyncSession], failure: str
) -> None:
    async with db_sessions() as session:
        repo = (
            RejectingCredentialRepository(session) if failure == "credential" else InvalidCredentialRepository(session)
        )
        error_type = RuntimeError if failure == "credential" else IntegrityError
        with pytest.raises(error_type):
            await service(session, repo).register_user(command())
        await service(session).register_user(replace(command(), username="next_user", email="next@example.com"))
    assert await counts(db_sessions) == (1, 1)
    async with db_sessions() as session:
        assert await UserRepository(session).get_user_by_email(command().email) is None


@pytest.mark.parametrize("exit_mode", ["no_commit", "exception", "explicit_rollback"])
async def test_uow_does_not_persist_uncommitted_user(
    db_sessions: async_sessionmaker[AsyncSession], exit_mode: str
) -> None:
    async with db_sessions() as session:
        uow = UoW(session)
        user = UserEntity.create(
            username=Username("test_user"), email=Email("test@example.com"), timezone=Timezone("UTC")
        )
        try:
            async with uow:
                await UserRepository(session).create_user(user)
                if exit_mode == "exception":
                    raise RuntimeError("Caller failed")
                if exit_mode == "explicit_rollback":
                    await uow.rollback()
        except RuntimeError:
            assert exit_mode == "exception"
    assert await counts(db_sessions) == (0, 0)


@pytest.mark.parametrize("status", list(UserStatus))
async def test_deleted_user_identifiers_can_be_reused(
    db_sessions: async_sessionmaker[AsyncSession], status: UserStatus
) -> None:
    async with db_sessions() as session:
        first = await service(session).register_user(command())
        user = await session.get(UserModel, first.user_id)
        user.deleted_at = datetime.now(UTC)
        user.status = status
        await session.commit()
        second = await service(session).register_user(command())
    assert first.user_id != second.user_id
    assert await counts(db_sessions) == (2, 2)


@pytest.mark.parametrize("status", list(UserStatus))
async def test_not_deleted_user_identifiers_remain_reserved(
    db_sessions: async_sessionmaker[AsyncSession], status: UserStatus
) -> None:
    async with db_sessions() as session:
        first = await service(session).register_user(command())
        user = await session.get(UserModel, first.user_id)
        user.status = status
        await session.commit()
        with pytest.raises(EmailAlreadyExistsError):
            await service(session).register_user(replace(command(), username="other_user"))
    assert await counts(db_sessions) == (1, 1)


async def test_unrelated_database_error_is_propagated_and_rolled_back(
    db_sessions: async_sessionmaker[AsyncSession],
) -> None:
    async with db_sessions() as session:
        with pytest.raises(DBAPIError) as caught:
            await service(session, DatabaseErrorCredentialRepository(session)).register_user(command())
        assert not isinstance(caught.value, (EmailAlreadyExistsError, UsernameAlreadyExistsError))
    assert await counts(db_sessions) == (0, 0)


@pytest.mark.parametrize(
    ("field", "value", "error_type"),
    [
        ("username", "Пользователь", InvalidUsernameError),
        ("email", "a" * 64 + "@" + "b" * 32 + ".com", InvalidEmailError),
    ],
)
async def test_registration_rejects_invalid_user_values_without_database_records(
    db_sessions: async_sessionmaker[AsyncSession],
    field: str,
    value: str,
    error_type: type[Exception],
) -> None:
    async with db_sessions() as session:
        with pytest.raises(error_type):
            await service(session).register_user(replace(command(), **{field: value}))
    assert await counts(db_sessions) == (0, 0)


async def test_credential_foreign_key_prevents_orphan_records(db_sessions: async_sessionmaker[AsyncSession]) -> None:
    async with db_sessions() as session:
        with pytest.raises(IntegrityError):
            async with UoW(session) as uow:
                await AuthCredentialRepository(session).create_auth_credential(
                    AuthCredentialEntity.create(user_id=uuid7(), password_hash="test-hash")
                )
                await uow.commit()
    assert await counts(db_sessions) == (0, 0)


@pytest.mark.parametrize(
    ("field", "error_type"), [("username", UsernameAlreadyExistsError), ("email", EmailAlreadyExistsError)]
)
async def test_database_uniqueness_is_case_insensitive_without_service_normalization(
    db_sessions: async_sessionmaker[AsyncSession], field: str, error_type: type[Exception]
) -> None:
    async with db_sessions() as session:
        first = await service(session).register_user(command())
        stored = await session.get(UserModel, first.user_id)
        assert stored is not None
        setattr(stored, field, getattr(stored, field).upper())
        await session.commit()
        new_data = (
            replace(command(), username="other_user")
            if field == "email"
            else replace(command(), email="other@example.com")
        )
        with pytest.raises(error_type):
            await service(session).register_user(new_data)
    assert await counts(db_sessions) == (1, 1)


async def test_unrelated_integrity_error_is_not_reported_as_email_or_username_conflict(
    db_sessions: async_sessionmaker[AsyncSession],
) -> None:
    async with db_sessions() as session:
        first = await service(session).register_user(command())
    async with db_sessions() as session:
        user = UserEntity.create(
            username=Username("other_user"), email=Email("other@example.com"), timezone=Timezone("UTC")
        )
        user = replace(user, id=first.user_id)
        with pytest.raises(IntegrityError):
            async with UoW(session):
                await UserRepository(session).create_user(user)
    assert await counts(db_sessions) == (1, 1)


@pytest.mark.parametrize(
    ("email", "normalized"),
    [
        ("a" * 64 + "@" + "b" * 31 + ".com", "a" * 64 + "@" + "b" * 31 + ".com"),
        ("e\u0301" + "a" * 62 + "@" + "b" * 32 + ".com", "é" + "a" * 62 + "@" + "b" * 32 + ".com"),
    ],
    ids=["exactly-100", "unicode-composition-to-100"],
)
async def test_registration_persists_email_at_normalized_length_limit(
    db_sessions: async_sessionmaker[AsyncSession],
    email: str,
    normalized: str,
) -> None:
    async with db_sessions() as session:
        result = await service(session).register_user(replace(command(), email=email))
    async with db_sessions() as session:
        stored = await session.get(UserModel, result.user_id)
        assert stored is not None
        assert len(stored.email) == 100
        assert stored.email == result.email == normalized
    assert await counts(db_sessions) == (1, 1)
