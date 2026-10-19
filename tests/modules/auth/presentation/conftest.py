from collections.abc import AsyncIterator

import pytest_asyncio
from dishka import Provider, Scope, make_async_container, provide
from dishka.integrations.fastapi import setup_dishka
from fastapi import FastAPI

from modules.auth.application.service import AuthService
from modules.auth.presentation.exception_handlers import setup_auth_exception_handlers
from modules.auth.presentation.routes import auth_router
from modules.user.presentation.exception_handlers import setup_user_exception_handlers
from shared.config import Settings
from tests.fakes.auth_login import AuthLoginContext
from tests.fakes.registration import RegistrationContext


class RegistrationProvider(Provider):
    def __init__(self, registration: RegistrationContext) -> None:
        super().__init__()
        self.registration = registration

    @provide(scope=Scope.REQUEST)
    def auth_service(self) -> AuthService:
        return self.registration.service


class AuthLoginProvider(Provider):
    def __init__(self, auth_login: AuthLoginContext) -> None:
        super().__init__()
        self.auth_login = auth_login

    @provide(scope=Scope.REQUEST)
    def auth_service(self) -> AuthService:
        return self.auth_login.service

    @provide(scope=Scope.APP)
    def settings(self) -> Settings:
        return self.auth_login.settings


@pytest_asyncio.fixture
async def registration_app(registration: RegistrationContext) -> AsyncIterator[FastAPI]:
    app = FastAPI()
    app.include_router(auth_router)
    setup_auth_exception_handlers(app)
    setup_user_exception_handlers(app)
    container = make_async_container(RegistrationProvider(registration))
    setup_dishka(container, app)
    try:
        yield app
    finally:
        await container.close()


@pytest_asyncio.fixture
async def auth_login_app(auth_login: AuthLoginContext) -> AsyncIterator[FastAPI]:
    app = FastAPI()
    app.include_router(auth_router)
    setup_auth_exception_handlers(app)
    setup_user_exception_handlers(app)
    container = make_async_container(AuthLoginProvider(auth_login))
    setup_dishka(container, app)
    try:
        yield app
    finally:
        await container.close()
