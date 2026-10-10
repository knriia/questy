import pytest

from modules.auth.domain.exceptions import InvalidPasswordError
from modules.auth.domain.value_objects import Password

pytestmark = pytest.mark.unit


@pytest.mark.parametrize("raw", ["a" * 15, "a" * 100, " " * 15, "  valid password  "])
def test_password_preserves_valid_characters_and_spaces(raw: str) -> None:
    assert Password(raw).value == raw
    assert raw not in repr(Password(raw))


@pytest.mark.parametrize("raw", ["", "a" * 14, "a" * 101, "e\u0301" * 14])
def test_password_rejects_invalid_normalized_length(raw: str) -> None:
    with pytest.raises(InvalidPasswordError):
        Password(raw)


@pytest.mark.parametrize("length", [15, 100])
def test_password_normalizes_unicode_before_checking_length(length: int) -> None:
    assert Password("e\u0301" * length).value == "é" * length
