from collections.abc import Callable

import pytest
from argon2.exceptions import VerificationError

from modules.auth.infrastructure import password_hasher as password_hasher_module
from modules.auth.infrastructure.password_hasher import Argon2PasswordHasher

pytestmark = pytest.mark.unit


async def inline_to_thread(function: Callable[..., object], *args: object) -> object:
    return function(*args)


@pytest.mark.asyncio
async def test_argon2_hash_is_salted_and_verifies_only_original_password(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(password_hasher_module.asyncio, "to_thread", inline_to_thread)
    hasher = Argon2PasswordHasher()
    password = "valid password phrase"
    first = await hasher.hash(password)
    second = await hasher.hash(password)
    assert first.startswith("$argon2id$")
    assert first != second
    assert first != password
    assert await hasher.verify(password, first)
    assert not await hasher.verify("different password", first)


@pytest.mark.asyncio
async def test_argon2_verifies_password_without_stripping_spaces(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(password_hasher_module.asyncio, "to_thread", inline_to_thread)
    hasher = Argon2PasswordHasher()
    password = "  valid password  "
    password_hash = await hasher.hash(password)
    assert await hasher.verify(password, password_hash)
    assert not await hasher.verify(password.strip(), password_hash)


@pytest.mark.asyncio
async def test_password_hasher_delegates_work_and_converts_verification_errors(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    class StubHasher:
        def hash(self, password: str) -> str:
            return f"encoded:{password}"

        def verify(self, password_hash: str, password: str) -> bool:
            if password_hash == "malformed":
                raise VerificationError("invalid password hash")
            return password_hash == f"encoded:{password}"

    stub_hasher = StubHasher()
    monkeypatch.setattr(password_hasher_module, "PasswordHasher", lambda: stub_hasher)
    monkeypatch.setattr(password_hasher_module.asyncio, "to_thread", inline_to_thread)
    hasher = Argon2PasswordHasher()

    assert await hasher.hash("valid password") == "encoded:valid password"
    assert await hasher.verify("valid password", "encoded:valid password") is True
    assert await hasher.verify("wrong password", "encoded:valid password") is False
    assert await hasher.verify("valid password", "malformed") is False
