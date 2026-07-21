from dataclasses import dataclass, field


@dataclass(kw_only=True, slots=True, frozen=True)
class RegisterUserInput:
    username: str
    timezone: str
    email: str
    password: str = field(repr=False)
