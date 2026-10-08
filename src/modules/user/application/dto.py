import uuid
from dataclasses import dataclass
from datetime import datetime

from modules.user.domain.enums import UserStatus


@dataclass(kw_only=True, slots=True, frozen=True)
class UserCommand:
    username: str
    timezone: str
    email: str


@dataclass(kw_only=True, slots=True, frozen=True)
class UserResult:
    user_id: uuid.UUID
    username: str
    email: str
    timezone: str
    status: UserStatus
    created_at: datetime
