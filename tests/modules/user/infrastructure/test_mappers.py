from dataclasses import replace
from datetime import UTC, datetime

import pytest

from modules.user.domain.entities import UserEntity
from modules.user.domain.enums import UserStatus
from modules.user.domain.value_objects import Email, Timezone, Username
from modules.user.infrastructure.mappers import user_entity_to_model, user_model_to_entity

pytestmark = pytest.mark.unit


@pytest.mark.parametrize("deleted", [False, True])
@pytest.mark.parametrize("status", list(UserStatus))
def test_user_mapping_round_trip_preserves_every_field(status: UserStatus, deleted: bool) -> None:
    user = UserEntity.create(username=Username("test_user"), email=Email("test@example.com"), timezone=Timezone("UTC"))
    user = replace(
        user,
        status=status,
        email_verified=True,
        updated_at=datetime(2026, 1, 1, tzinfo=UTC),
        deleted_at=datetime(2026, 1, 2, tzinfo=UTC) if deleted else None,
    )
    model = user_entity_to_model(user)
    assert model.id == user.id
    assert model.username == user.username.value
    assert model.email == user.email.value
    assert model.timezone == user.timezone.value
    assert model.status == user.status
    assert model.email_verified == user.email_verified
    assert model.created_at == user.created_at
    assert model.updated_at == user.updated_at
    assert model.deleted_at == user.deleted_at
    assert user_model_to_entity(model) == user
