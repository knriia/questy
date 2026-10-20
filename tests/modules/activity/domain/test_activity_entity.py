from uuid import UUID

import pytest

from modules.activity.domain.entities.activity import ActivityEntity
from modules.activity.enums import ActivityStatus, ActivityType

pytestmark = pytest.mark.unit


def test_create_activity_sets_generated_id_owner_and_defaults() -> None:
    user_id = UUID("0194f8b4-2b9a-7d65-a6df-9d4ebd8ba812")
    fields_schema = {"fields": [{"name": "duration", "type": "number"}]}

    activity = ActivityEntity.create(
        user_id=user_id,
        title="Reading",
        activity_type=ActivityType.LEARNING,
        fields_schema=fields_schema,
    )

    assert activity.id.version == 7
    assert activity.user_id == user_id
    assert activity.title == "Reading"
    assert activity.description is None
    assert activity.activity_type is ActivityType.LEARNING
    assert activity.status is ActivityStatus.ACTIVE
    assert activity.fields_schema == fields_schema


def test_create_activity_preserves_optional_description() -> None:
    activity = ActivityEntity.create(
        user_id=UUID("0194f8b4-2b9a-7d65-a6df-9d4ebd8ba812"),
        title="Run",
        activity_type=ActivityType.TRAINING,
        fields_schema={},
        description="Evening run",
    )

    assert activity.description == "Evening run"
