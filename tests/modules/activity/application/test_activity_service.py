from datetime import UTC, datetime
from unittest.mock import AsyncMock
from uuid import UUID

import pytest

from modules.activity.application.services.activity import ActivityService
from modules.activity.domain.entities.activity import ActivityEntity, SavedActivityEntity
from modules.activity.enums import ActivityStatus, ActivityType
from tests.fakes.uow import FakeUoW

pytestmark = [pytest.mark.unit, pytest.mark.asyncio]


class ActivityRepositoryFake:
    def __init__(self, result: SavedActivityEntity | None = None, error: Exception | None = None) -> None:
        self.result = result
        self.error = error
        self.create_activity = AsyncMock(side_effect=self._create_activity)

    async def _create_activity(self, activity: ActivityEntity) -> SavedActivityEntity:
        if self.error is not None:
            raise self.error
        assert self.result is not None
        return self.result


def activity_entity() -> ActivityEntity:
    return ActivityEntity.create(
        user_id=UUID("0194f8b4-2b9a-7d65-a6df-9d4ebd8ba812"),
        title="Reading",
        activity_type=ActivityType.LEARNING,
        fields_schema={},
    )


def saved_activity() -> SavedActivityEntity:
    now = datetime.now(UTC)
    return SavedActivityEntity(
        id=UUID("0194f8b4-2b9a-7d65-a6df-9d4ebd8ba813"),
        user_id=UUID("0194f8b4-2b9a-7d65-a6df-9d4ebd8ba812"),
        title="Reading",
        description=None,
        activity_type=ActivityType.LEARNING,
        status=ActivityStatus.ACTIVE,
        fields_schema={},
        created_at=now,
        updated_at=now,
    )


async def test_create_activity_saves_and_commits_inside_uow() -> None:
    activity = activity_entity()
    saved = saved_activity()
    repository = ActivityRepositoryFake(result=saved)
    uow = FakeUoW()
    service = ActivityService(repository=repository, uow=uow)

    result = await service.create_activity(activity=activity)

    assert result is saved
    repository.create_activity.assert_awaited_once_with(activity=activity)
    assert uow.commit_count == 1
    assert uow.rollback_count == 1


async def test_create_activity_rolls_back_and_propagates_repository_error() -> None:
    error = RuntimeError("storage failed")
    repository = ActivityRepositoryFake(error=error)
    uow = FakeUoW()
    service = ActivityService(repository=repository, uow=uow)

    with pytest.raises(RuntimeError, match="storage failed"):
        await service.create_activity(activity=activity_entity())

    assert uow.commit_count == 0
    assert uow.rollback_count == 1


async def test_create_activity_rolls_back_and_propagates_commit_error() -> None:
    repository = ActivityRepositoryFake(result=saved_activity())
    uow = FakeUoW()
    uow.commit = AsyncMock(side_effect=RuntimeError("commit failed"))  # type: ignore[method-assign]
    service = ActivityService(repository=repository, uow=uow)

    with pytest.raises(RuntimeError, match="commit failed"):
        await service.create_activity(activity=activity_entity())

    repository.create_activity.assert_awaited_once()
    assert uow.rollback_count == 1
