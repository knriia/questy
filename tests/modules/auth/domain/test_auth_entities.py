from datetime import UTC, datetime, timedelta
from uuid import uuid7

import pytest

from modules.auth.domain.entities.credential import AuthCredentialEntity
from modules.auth.domain.entities.refresh_token import AuthRefreshTokenEntity
from modules.auth.domain.entities.session import AuthSessionEntity
from modules.auth.domain.exceptions import InvalidSessionExpirationError, InvalidTokenExpirationError

pytestmark = pytest.mark.unit


def make_session(expires_at: datetime) -> AuthSessionEntity:
    return AuthSessionEntity.create(
        user_id=uuid7(),
        device_id_hash="device-hash",
        user_agent="test-agent",
        client_name="web",
        ip_created="192.0.2.1",
        expires_at=expires_at,
    )


def make_refresh_token(expires_at: datetime) -> AuthRefreshTokenEntity:
    return AuthRefreshTokenEntity.create(
        session_id=uuid7(),
        secret_hash="secret-hash",
        expires_at=expires_at,
    )


def test_credential_password_change_updates_hash_and_timestamp() -> None:
    credential = AuthCredentialEntity.create(user_id=uuid7(), password_hash="old-hash")
    previous_changed_at = datetime(2000, 1, 1, tzinfo=UTC)
    credential.password_changed_at = previous_changed_at

    credential.change_password("new-hash")

    assert credential.password_hash == "new-hash"
    assert credential.password_changed_at > previous_changed_at


def test_session_expiration_and_revocation_states() -> None:
    now = datetime.now(UTC)
    session = make_session(now + timedelta(hours=1))

    assert not session.is_expired(now)
    assert not session.is_revoked
    assert session.is_active(now)

    session.revoke(now)
    assert session.is_revoked
    assert not session.is_active(now)
    session.revoke(now + timedelta(seconds=1))
    assert session.revoked_at == now

    session.revoked_at = None
    session.expires_at = now
    assert session.is_expired(now)
    assert not session.is_active(now)


def test_session_rejects_expiration_in_the_past() -> None:
    with pytest.raises(InvalidSessionExpirationError):
        make_session(datetime.now(UTC) - timedelta(seconds=1))


def test_refresh_token_expiration_use_and_revocation_states() -> None:
    now = datetime.now(UTC)
    token = make_refresh_token(now + timedelta(hours=1))

    assert not token.is_expired(now)
    assert not token.is_used
    assert not token.is_revoked
    assert token.is_active(now)

    token.revoke(now)
    assert token.is_revoked
    assert not token.is_active(now)
    token.revoke(now + timedelta(seconds=1))
    assert token.revoked_at == now

    token.revoked_at = None
    token.used_at = now
    assert token.is_used
    assert not token.is_active(now)

    token.used_at = None
    token.expires_at = now
    assert token.is_expired(now)
    assert not token.is_active(now)


def test_refresh_token_rejects_expiration_in_the_past() -> None:
    with pytest.raises(InvalidTokenExpirationError):
        make_refresh_token(datetime.now(UTC) - timedelta(seconds=1))
