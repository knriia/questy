from dataclasses import dataclass, field
from unicodedata import normalize
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from email_validator import EmailNotValidError, validate_email

from modules.users.domain.exceptions import (
    InvalidEmailError,
    InvalidPasswordError,
    InvalidTimezoneError,
    InvalidUsernameError,
)


@dataclass(frozen=True, slots=True)
class Username:
    value: str

    def __post_init__(self):
        normalized = self.value.strip().lower()
        if not 3 <= len(normalized) <= 30:
            raise InvalidUsernameError("Username must contain between 3 and 30 characters")

        if not normalized.replace("_", "").isalnum():
            raise InvalidUsernameError("Username may contain only letters, numbers, and underscores")

        if not normalized[0].isalpha():
            raise InvalidUsernameError("Username must start with a letter")

        object.__setattr__(self, "value", normalized)


@dataclass(frozen=True, slots=True)
class Email:
    value: str

    def __post_init__(self):
        try:
            result = validate_email(self.value.strip(), check_deliverability=False)

        except EmailNotValidError as error:
            raise InvalidEmailError("Email has invalid format") from error

        object.__setattr__(self, "value", result.normalized.lower())


@dataclass(frozen=True, slots=True)
class Timezone:
    value: str

    def __post_init__(self):
        normalized = self.value.strip()
        try:
            ZoneInfo(normalized)
        except (ZoneInfoNotFoundError, ValueError) as error:
            raise InvalidTimezoneError("Unknown timezone") from error

        object.__setattr__(self, "value", normalized)


@dataclass(frozen=True, slots=True)
class Password:
    value: str = field(repr=False)

    def __post_init__(self):
        normalized = normalize("NFC", self.value)

        if not 15 <= len(normalized) <= 100:
            raise InvalidPasswordError("Password must contain between 15 and 100 characters")

        object.__setattr__(self, "value", normalized)
