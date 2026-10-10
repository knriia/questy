import pytest

from modules.user.domain.exceptions import InvalidEmailError, InvalidTimezoneError, InvalidUsernameError
from modules.user.domain.value_objects import Email, Timezone, Username

pytestmark = pytest.mark.unit


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        (" abc ", "abc"),
        (" " + "A" * 30 + " ", "a" * 30),
        ("User_12", "user_12"),
    ],
)
def test_username_accepts_and_normalizes_valid_values(raw: str, expected: str) -> None:
    assert Username(raw).value == expected


@pytest.mark.parametrize(
    "raw",
    [
        " ",
        "\t\n",
        " ab ",
        " " + "a" * 31 + " ",
        "user name",
        "user.name",
        "user🙂",
        "Пользователь",
        "Élodie",
        "user١٢",
        "ｕｓｅｒ",
    ],
)
def test_username_rejects_invalid_values(raw: str) -> None:
    with pytest.raises(InvalidUsernameError):
        Username(raw)


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        (" USER+TAG@EXAMPLE.COM ", "user+tag@example.com"),
        ("user@mail.example.com", "user@mail.example.com"),
        ("user@bücher.de", "user@bücher.de"),
    ],
)
def test_email_accepts_and_normalizes_valid_values(raw: str, expected: str) -> None:
    assert Email(raw).value == expected


@pytest.mark.parametrize("raw", [" ", "\t\n", "@example.com", "user name@example.com", "user@@example.com"])
def test_email_rejects_invalid_values(raw: str) -> None:
    with pytest.raises(InvalidEmailError):
        Email(raw)


@pytest.mark.parametrize("length", [99, 100])
def test_email_accepts_values_up_to_storage_limit(length: int) -> None:
    raw = "a" * 64 + "@" + "b" * (length - 69) + ".com"
    assert len(raw) == length
    assert Email(raw).value == raw


@pytest.mark.parametrize("length", [101, 109])
def test_email_rejects_values_exceeding_storage_limit(length: int) -> None:
    raw = "a" * 64 + "@" + "b" * (length - 69) + ".com"
    with pytest.raises(InvalidEmailError, match="Email must contain no more than 100 characters"):
        Email(raw)


def test_email_checks_length_after_unicode_composition() -> None:
    raw = "e\u0301" + "a" * 62 + "@" + "b" * 32 + ".com"
    assert len(raw) == 101
    normalized = Email(raw).value
    assert normalized == "é" + "a" * 62 + "@" + "b" * 32 + ".com"
    assert len(normalized) == 100


def test_email_checks_length_after_lowercase_expansion() -> None:
    raw = "İ" + "a" * 60 + "@" + "b" * 34 + ".com"
    assert len(raw) == 100
    assert len(raw.lower()) == 101
    with pytest.raises(InvalidEmailError, match="Email must contain no more than 100 characters"):
        Email(raw)


@pytest.mark.parametrize("raw", ["UTC", " Europe/Berlin ", "Asia/Tomsk"])
def test_timezone_accepts_valid_values(raw: str) -> None:
    assert Timezone(raw).value == raw.strip()


@pytest.mark.parametrize("raw", [" ", "\t\n", "utc", "/usr/share/zoneinfo/UTC", "Asia/../UTC"])
def test_timezone_rejects_invalid_values(raw: str) -> None:
    with pytest.raises(InvalidTimezoneError):
        Timezone(raw)
