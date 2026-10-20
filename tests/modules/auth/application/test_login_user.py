import hashlib
import hmac
from datetime import UTC
from unicodedata import normalize
from uuid import UUID

import jwt
import pytest

from modules.auth.application.dto import UserAuthCredentialCommand
from modules.auth.domain.exceptions import CredentialsValidationError
from modules.user.domain.enums import UserStatus
from tests.fakes.auth_login import AuthLoginContext, add_login_user

pytestmark = pytest.mark.integration_no_db
DEFAULT_TEST_SECRET = "correct password"


def login_command(identifier: str = "knriia", secret: str = DEFAULT_TEST_SECRET) -> UserAuthCredentialCommand:
    return UserAuthCredentialCommand(
        identifier=identifier,
        password=secret,
        ip_address="203.0.113.10",
        user_agent="test-agent/1.0",
        client_name="web-client",
    )


@pytest.mark.asyncio
@pytest.mark.parametrize("identifier", [" KnRiia ", " KNRIiA@EXAMPLE.COM "])
async def test_login_creates_session_refresh_token_access_token_and_csrf_token(
    auth_login: AuthLoginContext,
    identifier: str,
) -> None:
    user = add_login_user(auth_login)
    auth_login.hasher.results["stored-password-hash"] = True
    password = "e\u0301" * 10

    result = await auth_login.service.auth_user(login_command(identifier=identifier, secret=password))

    normalized_password = normalize("NFC", password)
    assert auth_login.hasher.verify_calls == [(normalized_password, "stored-password-hash")]
    assert auth_login.uow.enter_count == auth_login.uow.commit_count == auth_login.uow.rollback_count == 1
    assert len(auth_login.sessions.sessions) == len(auth_login.refresh_tokens.refresh_tokens) == 1

    session = auth_login.sessions.sessions[result.sid]
    assert session.user_id == user.id
    assert session.user_agent == "test-agent/1.0"
    assert session.client_name == "web-client"
    assert session.ip_created == "203.0.113.10"
    assert session.created_at.tzinfo is UTC
    assert session.last_used_at == session.created_at
    assert session.expires_at == result.refresh_token_expires_at
    assert session.revoked_at is None
    assert (
        session.device_id_hash
        == hmac.new(
            auth_login.settings.DEVICE_ID_HMAC_KEY.encode(), result.device_id.encode(), hashlib.sha256
        ).hexdigest()
    )

    refresh_id, refresh_secret = result.refresh_token.split(".")
    refresh_token = auth_login.refresh_tokens.refresh_tokens[UUID(refresh_id)]
    assert refresh_token.session_id == session.id
    assert refresh_token.expires_at == session.expires_at
    assert (
        refresh_token.secret_hash
        == hmac.new(
            auth_login.settings.REFRESH_TOKEN_HMAC_KEY.encode(), refresh_secret.encode(), hashlib.sha256
        ).hexdigest()
    )
    assert refresh_token.used_at is None
    assert refresh_token.revoked_at is None

    claims = jwt.decode(
        result.access_token,
        auth_login.settings.ACCESS_TOKEN_HMAC_KEY,
        algorithms=["HS256"],
        issuer=auth_login.settings.JWT_ISSUER,
        audience=auth_login.settings.JWT_AUDIENCE,
    )
    assert claims["sub"] == str(user.id)
    assert claims["sid"] == str(session.id)
    assert UUID(claims["jti"]).version == 7
    assert claims["iss"] == auth_login.settings.JWT_ISSUER
    assert claims["aud"] == auth_login.settings.JWT_AUDIENCE
    assert claims["exp"] - claims["iat"] == auth_login.settings.ACCESS_TOKEN_TTL_SECONDS
    assert int(result.access_token_expires_at.timestamp()) == claims["exp"]

    csrf_nonce, csrf_signature = result.csrf_token.split(".")
    assert (
        csrf_signature
        == hmac.new(
            auth_login.settings.CSRF_HMAC_KEY.encode(),
            f"{session.id}.{csrf_nonce}".encode(),
            hashlib.sha256,
        ).hexdigest()
    )


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("identifier", "account_state"),
    [
        ("missing_user", "none"),
        ("bad username", "none"),
        ("invalid-address@", "none"),
        ("knriia", "blocked"),
        ("knriia", "deleted"),
    ],
)
async def test_login_rejects_missing_invalid_and_inactive_users_with_dummy_hash(
    auth_login: AuthLoginContext,
    identifier: str,
    account_state: str,
) -> None:
    if account_state != "none":
        add_login_user(
            auth_login,
            status=UserStatus.BLOCKED if account_state == "blocked" else UserStatus.ACTIVE,
            deleted=account_state == "deleted",
        )

    with pytest.raises(CredentialsValidationError, match="Invalid credentials"):
        await auth_login.service.auth_user(login_command(identifier=identifier))

    assert auth_login.hasher.verify_calls == [("correct password", auth_login.settings.AUTH_DUMMY_PASSWORD_HASH)]
    assert auth_login.uow.enter_count == auth_login.uow.commit_count == 0
    assert auth_login.sessions.sessions == auth_login.refresh_tokens.refresh_tokens == {}


@pytest.mark.asyncio
async def test_login_uses_dummy_hash_when_active_user_has_no_credential(auth_login: AuthLoginContext) -> None:
    add_login_user(auth_login, with_credential=False)

    with pytest.raises(CredentialsValidationError, match="Invalid credentials"):
        await auth_login.service.auth_user(login_command())

    assert auth_login.hasher.verify_calls == [("correct password", auth_login.settings.AUTH_DUMMY_PASSWORD_HASH)]
    assert auth_login.uow.enter_count == 0


@pytest.mark.asyncio
async def test_login_rejects_wrong_password_using_the_account_hash(auth_login: AuthLoginContext) -> None:
    add_login_user(auth_login)

    with pytest.raises(CredentialsValidationError, match="Invalid credentials"):
        await auth_login.service.auth_user(login_command())

    assert auth_login.hasher.verify_calls == [("correct password", "stored-password-hash")]
    assert auth_login.uow.enter_count == 0
    assert auth_login.sessions.sessions == auth_login.refresh_tokens.refresh_tokens == {}


@pytest.mark.asyncio
async def test_login_normalizes_before_rejecting_password_over_limit(auth_login: AuthLoginContext) -> None:
    with pytest.raises(CredentialsValidationError, match="Invalid credentials"):
        await auth_login.service.auth_user(login_command(secret="x" * 101))

    assert auth_login.hasher.verify_calls == []
    assert auth_login.uow.enter_count == 0


@pytest.mark.asyncio
async def test_login_propagates_password_hasher_errors_without_starting_transaction(
    auth_login: AuthLoginContext,
) -> None:
    add_login_user(auth_login)
    error = RuntimeError("password verifier unavailable")
    auth_login.hasher.error = error

    with pytest.raises(RuntimeError) as caught:
        await auth_login.service.auth_user(login_command())

    assert caught.value is error
    assert auth_login.uow.enter_count == 0
    assert auth_login.sessions.sessions == auth_login.refresh_tokens.refresh_tokens == {}


@pytest.mark.asyncio
@pytest.mark.parametrize("failure_stage", ["enter", "session", "refresh", "commit"])
async def test_login_does_not_leave_partial_session_records_when_persistence_fails(
    auth_login: AuthLoginContext,
    failure_stage: str,
) -> None:
    add_login_user(auth_login)
    auth_login.hasher.results["stored-password-hash"] = True
    error = RuntimeError("session persistence failed")
    if failure_stage == "enter":
        auth_login.uow.enter_error = error
    elif failure_stage == "session":
        auth_login.sessions.error = error
    elif failure_stage == "refresh":
        auth_login.refresh_tokens.error = error
    else:
        auth_login.uow.commit_error = error

    with pytest.raises(RuntimeError) as caught:
        await auth_login.service.auth_user(login_command())

    assert caught.value is error
    assert auth_login.sessions.sessions == auth_login.refresh_tokens.refresh_tokens == {}
    assert auth_login.uow.enter_count == 1
    assert auth_login.uow.commit_count == int(failure_stage == "commit")
    assert auth_login.uow.rollback_count == int(failure_stage != "enter")
