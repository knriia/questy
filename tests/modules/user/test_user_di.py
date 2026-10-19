from unittest.mock import AsyncMock, Mock

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from modules.user.application.interface import IUserRepository
from modules.user.application.service import UserService
from modules.user.di import UserProvider
from modules.user.infrastructure.repositories import UserRepository
from shared.iuow import IUoW

pytestmark = pytest.mark.unit


@pytest.mark.asyncio
async def test_user_provider_builds_service_and_repository() -> None:
    provider = UserProvider()
    session = AsyncMock(spec=AsyncSession)
    user_repository = Mock(spec=IUserRepository)
    uow = Mock(spec=IUoW)

    service = await provider.create_user_service(user_repo=user_repository, uow=uow)

    assert isinstance(service, UserService)
    assert service._user_repo is user_repository
    assert service._uow is uow
    assert isinstance(await provider.create_user_repository(session), UserRepository)
