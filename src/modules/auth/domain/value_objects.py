from dataclasses import dataclass, field
from unicodedata import normalize

from modules.auth.domain.exceptions import InvalidPasswordError


@dataclass(frozen=True, slots=True)
class Password:
    value: str = field(repr=False)

    def __post_init__(self):
        normalized = normalize("NFC", self.value)

        if not 15 <= len(normalized) <= 100:
            raise InvalidPasswordError("Password must contain between 15 and 100 characters")

        object.__setattr__(self, "value", normalized)
