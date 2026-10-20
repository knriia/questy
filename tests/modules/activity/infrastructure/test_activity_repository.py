from datetime import UTC, datetime
from unittest.mock import AsyncMock, Mock
from uuid import UUID

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from modules.activity.domain.entities.activity import ActivityEntity, SavedActivityEntity
from modules.activity.enums import ActivityType
from modules.activity.infrastructure.models.activity import ActivityModel
from modules.activity.infrastructure.repositories.activity import ActivityRepository

pytestmark = [pytest.mark.unit, pytest.mark.asyncio]


async def test_create_activity_adds_model_flushes_and_returns_saved_entity(monkeypatch: pytest.MonkeyPatch) -> None:
    activity = ActivityEntity.create(
        user_id=UUID("0194f8b4-2b9a-7d65-a6df-9d4ebd8ba812"),
        title="Reading",
        activity_type=ActivityType.LEARNING,
        fields_schema={"fields": []},
    )
    now = datetime.now(UTC)
    saved = SavedActivityEntity(
        id=activity.id,
        user_id=activity.user_id,
        title=activity.title,
        description=activity.description,
        activity_type=activity.activity_type,
        status=activity.status,
        fields_schema=activity.fields_schema,
        created_at=now,
        updated_at=now,
    )
    session = AsyncMock(spec=AsyncSession)
    model_to_entity = Mock(return_value=saved)
    monkeypatch.setattr(
        "modules.activity.infrastructure.repositories.activity.activity_model_to_entity",
        model_to_entity,
    )
    repository = ActivityRepository(session=session)

    result = await repository.create_activity(activity=activity)

    assert isinstance(session.add.call_args.args[0], ActivityModel)
    model = session.add.call_args.args[0]
    assert model.id == activity.id
    assert model.user_id == activity.user_id
    assert model.title == activity.title
    session.flush.assert_awaited_once_with()
    model_to_entity.assert_called_once_with(activity_model=model)
    assert result is saved
    session.commit.assert_not_awaited()
    session.refresh.assert_not_awaited()
