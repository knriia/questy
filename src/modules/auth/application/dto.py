import uuid
from dataclasses import dataclass, field
from datetime import datetime

from modules.user.domain.enums import UserStatus


@dataclass(kw_only=True, slots=True, frozen=True)
class UserRegisterCommand:
    username: str
    timezone: str
    email: str
    password: str = field(repr=False)


@dataclass(kw_only=True, slots=True, frozen=True)
class UserRegisterResult:
    user_id: uuid.UUID
    username: str
    email: str
    timezone: str
    status: UserStatus
    created_at: datetime


@dataclass(kw_only=True, slots=True, frozen=True)
class UserAuthCredentialCommand:
    identifier: str
    password: str = field(repr=False)
    ip_address: str
    user_agent: str
    client_name: str

    def __post_init__(self):
        identifier = self.identifier.lower().strip()
        object.__setattr__(self, "identifier", identifier)

    @property
    def identifier_is_email(self) -> bool:
        return "@" in self.identifier


@dataclass(kw_only=True, slots=True, frozen=True)
class UserAuthSessionResult:
    session_id: uuid.UUID
    access_token: str = field(repr=False)
    access_token_expires_at: datetime
    refresh_token: str = field(repr=False)
    refresh_token_expires_at: datetime
    device_id: str = field(repr=False)
    csrf_token: str = field(repr=False)
