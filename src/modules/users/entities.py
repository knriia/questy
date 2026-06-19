import datetime
import uuid
from dataclasses import dataclass

from uuid6 import uuid6


@dataclass
class UserEntity:
    id: uuid.UUID
    username: str
    nickname: str
    email: str
    telegram_id: str | None = None
    created_at: datetime.datetime | None = None
    updated_at: datetime.datetime | None = None

    @classmethod
    def create(
        cls,
        username: str,
        nickname: str,
        email: str,
        telegram_id: str | None = None,
    ) -> "UserEntity":
        return cls(
            id=uuid6(),
            username=username,
            nickname=nickname,
            email=email,
            telegram_id=telegram_id,
        )


class SavedUserEntity(UserEntity):
    created_at: datetime.datetime
    updated_at: datetime.datetime
