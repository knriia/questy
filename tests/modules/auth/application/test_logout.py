from datetime import UTC, datetime, timedelta
from uuid import UUID, uuid7

import pytest

from modules.auth.domain.entities.refresh_token import AuthRefreshTokenEntity
from modules.auth.domain.entities.session import AuthSessionEntity
from modules.auth.domain.exceptions import UnauthenticatedError
from tests.fakes.auth_login import AuthLoginContext

pytestmark = pytest.mark.unit


def create_session(context: AuthLoginContext) -> AuthSessionEntity:
    session = AuthSessionEntity.create(
        user_id=uuid7(),
        device_id_hash="device-hash",
        user_agent="test-agent",
        client_name="web",
        ip_created="192.0.2.1",
        expires_at=datetime.now(UTC) + timedelta(hours=1),
    )
    context.sessions.sessions[session.id] = session
    return session


@pytest.mark.asyncio
async def test_logout_rejects_missing_session_without_starting_transaction(auth_login: AuthLoginContext) -> None:
    with pytest.raises(UnauthenticatedError):
        await auth_login.service.user_logout(uuid7())

    assert auth_login.uow.enter_count == 0
    assert auth_login.uow.commit_count == 0


@pytest.mark.asyncio
@pytest.mark.parametrize(("active_token_count", "already_revoked_token_count"), [(0, 0), (0, 1), (2, 1)])
async def test_logout_revokes_session_and_all_refresh_tokens(
    auth_login: AuthLoginContext,
    active_token_count: int,
    already_revoked_token_count: int,
) -> None:
    session = create_session(auth_login)
    token_count = active_token_count + already_revoked_token_count
    tokens = [
        AuthRefreshTokenEntity.create(
            session_id=session.id,
            secret_hash=f"secret-hash-{index}",
            expires_at=session.expires_at,
        )
        for index in range(token_count)
    ]
    previous_revocation_times: dict[UUID, datetime] = {}
    for token in tokens[active_token_count:]:
        revoked_at = datetime.now(UTC) - timedelta(minutes=1)
        token.revoke(revoked_at)
        previous_revocation_times[token.id] = revoked_at
    auth_login.refresh_tokens.refresh_tokens.update({token.id: token for token in tokens})

    await auth_login.service.user_logout(session.id)

    assert session.revoked_at is not None
    assert all(token.revoked_at == session.revoked_at for token in tokens[:active_token_count])
    assert all(token.revoked_at == previous_revocation_times[token.id] for token in tokens[active_token_count:])
    assert auth_login.uow.enter_count == 1
    assert auth_login.uow.commit_count == 1
    assert auth_login.uow.rollback_count == 1
