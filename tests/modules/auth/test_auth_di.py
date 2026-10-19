from unittest.mock import AsyncMock, Mock

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from modules.auth.application.interface.credential import IAuthCredentialRepository
from modules.auth.application.interface.refresh_token import IAuthRefreshTokenRepository
from modules.auth.application.interface.session import IAuthSessionRepository
from modules.auth.application.service import AuthService
from modules.auth.di import AuthProvider
from modules.auth.infrastructure.password_hasher import Argon2PasswordHasher
from modules.auth.infrastructure.repositories.credential import AuthCredentialRepository
from modules.auth.infrastructure.repositories.refresh_token import AuthRefreshTokenRepository
from modules.auth.infrastructure.repositories.session import AuthSessionRepository
from modules.user.application.service import UserService
from shared.config import Settings
from shared.iuow import IUoW

pytestmark = pytest.mark.unit


@pytest.mark.asyncio
async def test_auth_provider_builds_service_and_infrastructure_dependencies() -> None:
    provider = AuthProvider()
    session = AsyncMock(spec=AsyncSession)
    user_service = Mock(spec=UserService)
    credential_repository = Mock(spec=IAuthCredentialRepository)
    session_repository = Mock(spec=IAuthSessionRepository)
    refresh_token_repository = Mock(spec=IAuthRefreshTokenRepository)
    uow = Mock(spec=IUoW)
    password_hasher = Mock(spec=Argon2PasswordHasher)
    settings = Mock(spec=Settings)

    auth_service = await provider.create_auth_service(
        user_service=user_service,
        auth_credential_repo=credential_repository,
        auth_session_repo=session_repository,
        refresh_token_repo=refresh_token_repository,
        uow=uow,
        password_hash=password_hasher,
        settings=settings,
    )

    assert isinstance(auth_service, AuthService)
    assert auth_service._user_service is user_service
    assert auth_service._auth_credential_repo is credential_repository
    assert auth_service._auth_session_repo is session_repository
    assert auth_service._auth_refresh_token_repo is refresh_token_repository
    assert auth_service._uow is uow
    assert auth_service._password_hash is password_hasher
    assert auth_service._settings is settings

    assert isinstance(await provider.create_auth_session_repository(session), AuthSessionRepository)
    assert isinstance(await provider.create_refresh_token_repository(session), AuthRefreshTokenRepository)
    assert isinstance(await provider.create_auth_credential_repository(session), AuthCredentialRepository)
    assert isinstance(await provider.create_hasher(), Argon2PasswordHasher)
