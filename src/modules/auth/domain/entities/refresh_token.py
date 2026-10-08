from dataclasses import dataclass
from datetime import UTC, datetime
from uuid import UUID, uuid7

from modules.auth.domain.exceptions import InvalidTokenExpirationError


@dataclass(kw_only=True, slots=True)
class AuthRefreshTokenEntity:
    id: UUID
    session_id: UUID
    replaced_by_id: UUID | None
    secret_hash: str
    expires_at: datetime
    used_at: datetime | None
    revoked_at: datetime | None

    @classmethod
    def create(
        cls,
        session_id: UUID,
        secret_hash: str,
        expires_at: datetime,
    ) -> AuthRefreshTokenEntity:
        if expires_at <= datetime.now(UTC):
            raise InvalidTokenExpirationError("Token expiration must be in the future.")

        return cls(
            id=uuid7(),
            session_id=session_id,
            replaced_by_id=None,
            secret_hash=secret_hash,
            expires_at=expires_at,
            used_at=None,
            revoked_at=None,
        )

    def is_expired(self, now: datetime) -> bool:
        return now >= self.expires_at

    @property
    def is_used(self) -> bool:
        return self.used_at is not None

    def is_active(self, now: datetime) -> bool:
        return not self.is_expired(now) and not self.is_used and not self.is_revoked

    def revoke(self, now: datetime) -> None:
        if self.revoked_at is None:
            self.revoked_at = now

    @property
    def is_revoked(self) -> bool:
        return self.revoked_at is not None
