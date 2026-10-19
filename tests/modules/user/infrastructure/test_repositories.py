from unittest.mock import AsyncMock

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from modules.user.domain.entities import UserEntity
from modules.user.domain.value_objects import Email, Timezone, Username
from modules.user.infrastructure.mappers import user_entity_to_model
from modules.user.infrastructure.models import UserModel
from modules.user.infrastructure.repositories import UserRepository

pytestmark = pytest.mark.unit


@pytest.mark.asyncio
@pytest.mark.parametrize("found", [True, False])
async def test_user_repository_gets_user_by_id(found: bool) -> None:
    session = AsyncMock(spec=AsyncSession)
    user = UserEntity.create(username=Username("test_user"), email=Email("test@example.com"), timezone=Timezone("UTC"))
    session.get.return_value = user_entity_to_model(user) if found else None

    result = await UserRepository(session).get_user_by_id(user.id)

    assert result == user if found else result is None
    session.get.assert_awaited_once_with(UserModel, user.id)
