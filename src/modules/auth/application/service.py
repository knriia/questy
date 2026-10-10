import hashlib
import hmac
import logging
import secrets
from datetime import UTC, datetime, timedelta
from uuid import UUID, uuid7

import jwt

from modules.auth.application.dto import UserAuthCredentialCommand, UserAuthSessionResult, UserRegisterCommand
from modules.auth.application.interface.credential import IAuthCredentialRepository
from modules.auth.application.interface.refresh_token import IRefreshTokenRepository
from modules.auth.application.interface.session import IAuthSessionRepository
from modules.auth.domain.entities.credential import AuthCredentialEntity
from modules.auth.domain.entities.refresh_token import AuthRefreshTokenEntity
from modules.auth.domain.entities.session import AuthSessionEntity
from modules.auth.domain.exceptions import CredentialsValidationError
from modules.auth.domain.value_objects import Password
from modules.auth.infrastructure.password_hasher import Argon2PasswordHasher
from modules.user.application.dto import UserCommand, UserResult
from modules.user.application.service import UserService
from modules.user.domain.entities import UserEntity
from shared.config import Settings
from shared.iuow import IUoW

logger = logging.getLogger(__name__)


class AuthService:
    def __init__(
        self,
        user_service: UserService,
        auth_credential_repo: IAuthCredentialRepository,
        auth_session_repo: IAuthSessionRepository,
        refresh_token_repo: IRefreshTokenRepository,
        uow: IUoW,
        password_hash: Argon2PasswordHasher,
        settings: Settings,
    ):
        self._user_service = user_service
        self._auth_credential_repo = auth_credential_repo
        self._auth_session_repo = auth_session_repo
        self._refresh_token_repo = refresh_token_repo
        self._uow = uow
        self._password_hash = password_hash
        self._settings = settings

    async def register_user(self, user_data: UserRegisterCommand) -> UserResult:
        password = Password(user_data.password)
        password_hash = await self._password_hash.hash(password.value)
        async with self._uow:
            user_command = UserCommand(
                username=user_data.username,
                timezone=user_data.timezone,
                email=user_data.email,
            )
            created_user = await self._user_service.create_user(user_command=user_command)
            auth_credential = AuthCredentialEntity.create(user_id=created_user.user_id, password_hash=password_hash)
            await self._auth_credential_repo.create_auth_credential(auth_credential=auth_credential)
            await self._uow.commit()

        logger.info("User registered: user_id=%s", created_user.user_id)
        return created_user

    async def auth_user(self, user_data: UserAuthCredentialCommand) -> UserAuthSessionResult:
        if user_data.identifier_is_email:
            user_entity = await self._user_service.get_user_by_email(email=user_data.identifier)
        else:
            user_entity = await self._user_service.get_user_by_username(username=user_data.identifier)

        if user_entity is None:
            raise CredentialsValidationError("Invalid credentials.")

        if not user_entity.is_active:
            raise CredentialsValidationError("Invalid credentials.")

        auth_credential = await self.get_user_credential(user_id=user_entity.id)
        if not auth_credential:
            raise CredentialsValidationError("Invalid credentials.")

        verified = await self._password_hash.verify(
            password=user_data.password, password_hash=auth_credential.password_hash
        )
        if not verified:
            raise CredentialsValidationError("Invalid credentials.")

        now = datetime.now(UTC)
        device_key = self._settings.DEVICE_ID_HMAC_KEY.encode("utf-8")
        device_id = secrets.token_urlsafe(32)
        device_id_hash = hmac.new(key=device_key, msg=device_id.encode("utf-8"), digestmod=hashlib.sha256).hexdigest()
        expires_at = now + timedelta(seconds=self._settings.AUTH_SESSION_TTL_SECONDS)
        session_entity = AuthSessionEntity.create(
            user_id=user_entity.id,
            device_id_hash=device_id_hash,
            user_agent=user_data.user_agent,
            client_name=user_data.client_name,
            ip_created=user_data.ip_address,
            expires_at=expires_at,
        )

        refresh_secret = secrets.token_urlsafe(32)
        refresh_key = self._settings.REFRESH_TOKEN_HMAC_KEY.encode("utf-8")
        secret_hash = hmac.new(
            key=refresh_key,
            msg=refresh_secret.encode("utf-8"),
            digestmod=hashlib.sha256,
        ).hexdigest()
        refresh_token = AuthRefreshTokenEntity.create(
            session_id=session_entity.id,
            secret_hash=secret_hash,
            expires_at=expires_at,
        )

        access_expire_at = now + timedelta(seconds=self._settings.ACCESS_TOKEN_TTL_SECONDS)
        access_payload = {
            "sub": str(user_entity.id),
            "sid": str(session_entity.id),
            "jti": str(uuid7()),
            "iat": int(now.timestamp()),
            "exp": int(access_expire_at.timestamp()),
            "iss": self._settings.JWT_ISSUER,
            "aud": self._settings.JWT_AUDIENCE,
        }
        access_token = jwt.encode(payload=access_payload, key=self._settings.ACCESS_TOKEN_HMAC_KEY, algorithm="HS256")

        csrf_nonce = secrets.token_urlsafe(32)
        csrf_signature = hmac.new(
            key=self._settings.CSRF_HMAC_KEY.encode("utf-8"),
            msg=f"{session_entity.id}.{csrf_nonce}".encode(),
            digestmod=hashlib.sha256,
        ).hexdigest()

        async with self._uow:
            await self._auth_session_repo.create_auth_session(auth_session=session_entity)
            await self._refresh_token_repo.create_refresh_token(refresh_token=refresh_token)
            await self._uow.commit()

        return UserAuthSessionResult(
            session_id=session_entity.id,
            access_token=access_token,
            access_token_expires_at=access_expire_at,
            refresh_token=f"{refresh_token.id}.{refresh_secret}",
            refresh_token_expires_at=refresh_token.expires_at,
            device_id=device_id,
            csrf_token=f"{csrf_nonce}.{csrf_signature}",
        )

    async def get_user_credential(self, user_id: UUID) -> AuthCredentialEntity | None:
        return await self._auth_credential_repo.get_auth_credential_by_user_id(user_id=user_id)

    async def get_authenticated_user(self, principal: dict) -> UserEntity | None:
        pass
