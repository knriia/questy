from dataclasses import dataclass
from datetime import UTC, datetime
from uuid import UUID, uuid7

from modules.auth.domain.exceptions import InvalidSessionExpirationError


@dataclass(kw_only=True, slots=True)
class AuthSessionEntity:
    id: UUID
    user_id: UUID
    device_id_hash: str
    user_agent: str
    client_name: str
    ip_created: str
    last_used_at: datetime
    expires_at: datetime
    revoked_at: datetime | None
    created_at: datetime

    @classmethod
    def create(
        cls,
        user_id: UUID,
        device_id_hash: str,
        user_agent: str,
        client_name: str,
        ip_created: str,
        expires_at: datetime,
    ) -> AuthSessionEntity:
        now = datetime.now(UTC)
        if expires_at <= now:
            raise InvalidSessionExpirationError("Session expiration must be in the future.")

        return cls(
            id=uuid7(),
            user_id=user_id,
            device_id_hash=device_id_hash,
            user_agent=user_agent,
            client_name=client_name,
            ip_created=ip_created,
            last_used_at=now,
            expires_at=expires_at,
            revoked_at=None,
            created_at=now,
        )

    def is_expired(self, now: datetime) -> bool:
        return self.expires_at <= now

    @property
    def is_revoked(self) -> bool:
        return self.revoked_at is not None

    def is_active(self, now: datetime) -> bool:
        return not self.is_expired(now) and not self.is_revoked

    def revoke(self, now: datetime) -> None:
        if self.revoked_at is None:
            self.revoked_at = now
