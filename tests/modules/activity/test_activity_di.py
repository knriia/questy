from unittest.mock import AsyncMock, Mock

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from modules.activity.application.interfaces.activity import IActivityRepository
from modules.activity.application.services.activity import ActivityService
from modules.activity.di import ActivityProvider
from modules.activity.infrastructure.repositories.activity import ActivityRepository
from shared.iuow import IUoW

pytestmark = [pytest.mark.unit, pytest.mark.asyncio]


async def test_activity_provider_builds_activity_repository_and_service() -> None:
    provider = ActivityProvider()
    session = AsyncMock(spec=AsyncSession)
    uow = Mock(spec=IUoW)

    repository = await provider.activity_repository(session=session)
    service = await provider.activity_service(repository=repository, uow=uow)

    assert isinstance(repository, ActivityRepository)
    assert isinstance(repository, IActivityRepository)
    assert repository.session is session
    assert isinstance(service, ActivityService)
    assert service._repository is repository
    assert service._uow is uow
