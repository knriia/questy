from datetime import UTC, datetime
from uuid import UUID

import pytest

from modules.activity.domain.entities.activity import ActivityEntity, SavedActivityEntity
from modules.activity.enums import ActivityStatus, ActivityType
from modules.activity.infrastructure.mappers.activity import activity_entity_to_model, activity_model_to_entity
from modules.activity.infrastructure.models.activity import ActivityModel

pytestmark = pytest.mark.unit


def test_activity_entity_to_model_copies_domain_fields() -> None:
    activity = ActivityEntity.create(
        user_id=UUID("0194f8b4-2b9a-7d65-a6df-9d4ebd8ba812"),
        title="Run",
        activity_type=ActivityType.TRAINING,
        fields_schema={"fields": []},
        description="Morning run",
    )

    model = activity_entity_to_model(activity_entity=activity)

    assert isinstance(model, ActivityModel)
    assert model.id == activity.id
    assert model.user_id == activity.user_id
    assert model.title == activity.title
    assert model.description == activity.description
    assert model.activity_type == activity.activity_type
    assert model.status == activity.status
    assert model.fields_schema == activity.fields_schema


def test_activity_model_to_entity_restores_domain_enums_and_timestamps() -> None:
    now = datetime.now(UTC)
    model = ActivityModel(
        id=UUID("0194f8b4-2b9a-7d65-a6df-9d4ebd8ba813"),
        user_id=UUID("0194f8b4-2b9a-7d65-a6df-9d4ebd8ba812"),
        title="Run",
        description="Morning run",
        activity_type=ActivityType.TRAINING.value,
        status=ActivityStatus.ARCHIVED.value,
        fields_schema={"fields": []},
        created_at=now,
        updated_at=now,
    )

    entity = activity_model_to_entity(activity_model=model)

    assert isinstance(entity, SavedActivityEntity)
    assert entity.id == model.id
    assert entity.user_id == model.user_id
    assert entity.title == model.title
    assert entity.description == model.description
    assert entity.activity_type is ActivityType.TRAINING
    assert entity.status is ActivityStatus.ARCHIVED
    assert entity.fields_schema == model.fields_schema
    assert entity.created_at == now
    assert entity.updated_at == now
