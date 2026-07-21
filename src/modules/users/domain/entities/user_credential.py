import uuid
from dataclasses import dataclass
from datetime import UTC, datetime


@dataclass(kw_only=True, slots=True)
class UserCredentialEntity:
    user_id: uuid.UUID
    password_hash: str
    created_at: datetime
    password_changed_at: datetime

    @classmethod
    def create(
        cls,
        user_id: uuid.UUID,
        password_hash: str,
    ) -> "UserCredentialEntity":
        now = datetime.now(UTC)
        return cls(
            user_id=user_id,
            password_hash=password_hash,
            created_at=now,
            password_changed_at=now,
        )

    def change_password(self, password_hash: str) -> None:
        self.password_hash = password_hash
        self.password_changed_at = datetime.now(UTC)
