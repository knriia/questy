from collections.abc import AsyncIterator

import pytest
import pytest_asyncio
from dishka import Provider, Scope, make_async_container, provide
from dishka.integrations.fastapi import setup_dishka
from fastapi import FastAPI

from modules.auth.application.service import AuthService
from modules.auth.presentation.exception_handlers import setup_auth_exception_handlers
from modules.user.application.service import UserService
from modules.user.presentation.exception_handlers import setup_user_exception_handlers
from modules.user.presentation.routes import user_router
from shared.config import Settings
from tests.fakes.auth_login import AuthLoginContext, create_auth_login_context


class UserMeProvider(Provider):
    def __init__(self, context: AuthLoginContext) -> None:
        super().__init__()
        self.context = context

    @provide(scope=Scope.APP)
    def settings(self) -> Settings:
        return self.context.settings

    @provide(scope=Scope.REQUEST)
    def auth_service(self) -> AuthService:
        return self.context.service

    @provide(scope=Scope.REQUEST)
    def user_service(self) -> UserService:
        return UserService(user_repo=self.context.users, uow=self.context.uow)


@pytest.fixture
def user_me_context() -> AuthLoginContext:
    return create_auth_login_context()


@pytest_asyncio.fixture
async def user_me_app(user_me_context: AuthLoginContext) -> AsyncIterator[FastAPI]:
    app = FastAPI()
    app.include_router(user_router)
    setup_user_exception_handlers(app)
    setup_auth_exception_handlers(app)
    container = make_async_container(UserMeProvider(user_me_context))
    setup_dishka(container, app)
    try:
        yield app
    finally:
        await container.close()
