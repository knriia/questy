import pytest
from dishka import AsyncContainer
from dishka.integrations.fastapi import setup_dishka
from fastapi import FastAPI
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from modules.auth.presentation.routes import auth_router
from tests.support.asgi import post_json
from tests.support.registration_db import counts

pytestmark = [pytest.mark.asyncio, pytest.mark.integration_db]


async def test_production_di_registers_complete_account_through_http(
    db_sessions: async_sessionmaker[AsyncSession],
    test_container: AsyncContainer,
) -> None:
    app = FastAPI()
    app.include_router(auth_router)
    setup_dishka(test_container, app)
    status, body = await post_json(
        app,
        "/auth/register",
        {
            "username": "test_user",
            "email": "test@example.com",
            "timezone": "UTC",
            "password": "valid password phrase",
        },
    )
    assert status == 201
    assert body["username"] == "test_user"
    assert await counts(db_sessions) == (1, 1)
