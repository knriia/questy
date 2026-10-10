from uuid import uuid7

import pytest

from modules.auth.domain.entities.credential import AuthCredentialEntity
from modules.auth.infrastructure.mappers.credential import (
    auth_credential_entity_to_model,
    auth_credential_model_to_entity,
)

pytestmark = pytest.mark.unit


def test_new_credential_mapping_preserves_every_field() -> None:
    credential = AuthCredentialEntity.create(user_id=uuid7(), password_hash="test-password-hash")
    model = auth_credential_entity_to_model(credential)
    assert model.user_id == credential.user_id
    assert model.password_hash == credential.password_hash
    assert model.created_at == credential.created_at
    assert model.password_changed_at == credential.password_changed_at
    assert auth_credential_model_to_entity(model) == credential
