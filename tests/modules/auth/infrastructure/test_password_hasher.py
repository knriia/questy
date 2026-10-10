import pytest

from modules.auth.infrastructure.password_hasher import Argon2PasswordHasher

pytestmark = pytest.mark.unit


@pytest.mark.asyncio
async def test_argon2_hash_is_salted_and_verifies_only_original_password() -> None:
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
async def test_argon2_verifies_password_without_stripping_spaces() -> None:
    hasher = Argon2PasswordHasher()
    password = "  valid password  "
    password_hash = await hasher.hash(password)
    assert await hasher.verify(password, password_hash)
    assert not await hasher.verify(password.strip(), password_hash)
