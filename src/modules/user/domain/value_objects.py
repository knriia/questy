from dataclasses import dataclass
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from email_validator import EmailNotValidError, validate_email

from modules.user.domain.exceptions import InvalidEmailError, InvalidTimezoneError, InvalidUsernameError


@dataclass(frozen=True, slots=True)
class Username:
    value: str

    def __post_init__(self):
        normalized = self.value.strip().lower()
        if not 3 <= len(normalized) <= 30:
            raise InvalidUsernameError("Username must contain between 3 and 30 characters")

        without_underscores = normalized.replace("_", "")
        if not without_underscores.isalnum() or not without_underscores.isascii():
            raise InvalidUsernameError("Username may contain only letters, numbers, and underscores")

        if not normalized[0].isalpha():
            raise InvalidUsernameError("Username must start with a letter")

        object.__setattr__(self, "value", normalized)


@dataclass(frozen=True, slots=True)
class Email:
    value: str

    def __post_init__(self):
        try:
            validate_result = validate_email(self.value.strip(), check_deliverability=False)

        except EmailNotValidError as error:
            raise InvalidEmailError("Email has invalid format") from error

        normalized_result = validate_result.normalized.lower()
        if len(normalized_result) > 100:
            raise InvalidEmailError("Email must contain no more than 100 characters")

        object.__setattr__(self, "value", normalized_result)


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
