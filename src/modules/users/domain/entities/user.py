import uuid
from dataclasses import dataclass
from datetime import UTC, datetime

from uuid6 import uuid6

from modules.users.domain.enums import UserStatus
from modules.users.domain.value_objects import Email, Timezone, Username


@dataclass(kw_only=True, slots=True)
class UserEntity:
    id: uuid.UUID
    username: Username
    timezone: Timezone
    status: UserStatus
    email: Email
    email_verified: bool
    created_at: datetime
    updated_at: datetime
    deleted_at: datetime | None

    @classmethod
    def create(
        cls,
        username: Username,
        timezone: Timezone,
        email: Email,
    ) -> "UserEntity":
        now = datetime.now(UTC)
        return cls(
            id=uuid6(),
            username=username,
            timezone=timezone,
            status=UserStatus.ACTIVE,
            email=email,
            email_verified=False,
            created_at=now,
            updated_at=now,
            deleted_at=None,
        )

    @property
    def is_deleted(self) -> bool:
        return self.deleted_at is not None
