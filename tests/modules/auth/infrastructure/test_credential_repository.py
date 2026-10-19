from datetime import UTC, datetime
from unittest.mock import AsyncMock
from uuid import uuid7

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from modules.auth.domain.entities.credential import AuthCredentialEntity
from modules.auth.infrastructure.mappers.credential import auth_credential_entity_to_model
from modules.auth.infrastructure.models.credential import AuthCredentialModel
from modules.auth.infrastructure.repositories.credential import AuthCredentialRepository

pytestmark = pytest.mark.unit


def make_credential() -> AuthCredentialEntity:
    now = datetime.now(UTC)
    return AuthCredentialEntity(
        user_id=uuid7(),
        password_hash="password-hash",
        created_at=now,
        password_changed_at=now,
    )


@pytest.mark.asyncio
async def test_auth_credential_repository_adds_new_credential() -> None:
    session = AsyncMock(spec=AsyncSession)
    credential = make_credential()

    await AuthCredentialRepository(session).create_auth_credential(credential)

    model = session.add.call_args.args[0]
    assert isinstance(model, AuthCredentialModel)
    assert model.user_id == credential.user_id
    assert model.password_hash == credential.password_hash
    assert model.created_at == credential.created_at
    assert model.password_changed_at == credential.password_changed_at
    session.add.assert_called_once_with(model)


@pytest.mark.asyncio
@pytest.mark.parametrize("found", [True, False])
async def test_auth_credential_repository_gets_credential_by_user_id(found: bool) -> None:
    session = AsyncMock(spec=AsyncSession)
    credential = make_credential()
    session.get.return_value = auth_credential_entity_to_model(credential) if found else None

    result = await AuthCredentialRepository(session).get_auth_credential_by_user_id(credential.user_id)

    assert result == credential if found else result is None
    session.get.assert_awaited_once_with(AuthCredentialModel, credential.user_id)
