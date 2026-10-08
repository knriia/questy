from dataclasses import dataclass
from datetime import UTC, datetime
from uuid import UUID, uuid7

from modules.user.domain.enums import UserStatus
from modules.user.domain.value_objects import Email, Timezone, Username


@dataclass(kw_only=True, slots=True)
class UserEntity:
    id: UUID
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
    ) -> UserEntity:
        now = datetime.now(UTC)
        return cls(
            id=uuid7(),
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

    @property
    def is_active(self) -> bool:
        return self.status == UserStatus.ACTIVE and not self.is_deleted
