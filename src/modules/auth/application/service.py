import hashlib
import hmac
import logging
import secrets
from datetime import UTC, datetime, timedelta
from unicodedata import normalize
from uuid import UUID, uuid7

import jwt

from modules.auth.application.dto import UserAuthCredentialCommand, UserAuthSessionResult, UserRegisterCommand
from modules.auth.application.interface.credential import IAuthCredentialRepository
from modules.auth.application.interface.refresh_token import IAuthRefreshTokenRepository
from modules.auth.application.interface.session import IAuthSessionRepository
from modules.auth.domain.entities.credential import AuthCredentialEntity
from modules.auth.domain.entities.refresh_token import AuthRefreshTokenEntity
from modules.auth.domain.entities.session import AuthSessionEntity
from modules.auth.domain.exceptions import CredentialsValidationError, UnauthenticatedError
from modules.auth.domain.value_objects import Password
from modules.auth.infrastructure.password_hasher import Argon2PasswordHasher
from modules.user.application.dto import UserCommand, UserResult
from modules.user.application.service import UserService
from shared.config import Settings
from shared.iuow import IUoW

logger = logging.getLogger(__name__)


class AuthService:
    def __init__(
        self,
        user_service: UserService,
        auth_credential_repo: IAuthCredentialRepository,
        auth_session_repo: IAuthSessionRepository,
        auth_refresh_token_repo: IAuthRefreshTokenRepository,
        uow: IUoW,
        password_hash: Argon2PasswordHasher,
        settings: Settings,
    ):
        self._user_service = user_service
        self._auth_credential_repo = auth_credential_repo
        self._auth_session_repo = auth_session_repo
        self._auth_refresh_token_repo = auth_refresh_token_repo
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
        password = self._validate_password_on_login(user_data.password)
        user_id = await self._user_service.get_user_id_by_identifier(identifier=user_data.identifier)
        if user_id is None:
            await self._password_hash.verify(
                password=password,
                password_hash=self._settings.AUTH_DUMMY_PASSWORD_HASH,
            )
            raise CredentialsValidationError("Invalid credentials.")

        auth_credential = await self.get_user_credential(user_id=user_id)
        if not auth_credential:
            await self._password_hash.verify(
                password=password,
                password_hash=self._settings.AUTH_DUMMY_PASSWORD_HASH,
            )
            raise CredentialsValidationError("Invalid credentials.")

        verified = await self._password_hash.verify(
            password=password,
            password_hash=auth_credential.password_hash,
        )
        if not verified:
            raise CredentialsValidationError("Invalid credentials.")

        now = datetime.now(UTC)
        device_id = secrets.token_urlsafe(32)
        expires_at = now + timedelta(seconds=self._settings.AUTH_SESSION_TTL_SECONDS)

        session_entity = AuthSessionEntity.create(
            user_id=user_id,
            device_id_hash=self._create_device_id_hash(device_id=device_id),
            user_agent=user_data.user_agent,
            client_name=user_data.client_name,
            ip_created=user_data.ip_address,
            expires_at=expires_at,
        )

        sid = session_entity.id
        refresh_secret = secrets.token_urlsafe(32)
        refresh_token = AuthRefreshTokenEntity.create(
            session_id=sid,
            secret_hash=self._create_secret_hash_refresh_token(secret=refresh_secret),
            expires_at=expires_at,
        )

        access_expire_at = now + timedelta(seconds=self._settings.ACCESS_TOKEN_TTL_SECONDS)
        access_token = self._create_access_token(
            user_id=user_id,
            sid=sid,
            access_expire_at=access_expire_at,
            now=now,
        )

        async with self._uow:
            await self._auth_session_repo.create_auth_session(auth_session=session_entity)
            await self._auth_refresh_token_repo.create_refresh_token(refresh_token=refresh_token)
            await self._uow.commit()

        return UserAuthSessionResult(
            sid=sid,
            access_token=access_token,
            access_token_expires_at=access_expire_at,
            refresh_token=f"{refresh_token.id}.{refresh_secret}",
            refresh_token_expires_at=refresh_token.expires_at,
            device_id=device_id,
            csrf_token=self._create_csrf_token(sid=sid, secret=secrets.token_urlsafe(32)),
        )

    async def get_user_credential(self, user_id: UUID) -> AuthCredentialEntity | None:
        return await self._auth_credential_repo.get_auth_credential_by_user_id(user_id=user_id)

    @staticmethod
    def _validate_password_on_login(password: str) -> str:
        normalized = normalize("NFC", password)

        if len(normalized) > 100:
            raise CredentialsValidationError("Invalid credentials.")

        return normalized

    def _create_secret_hash_refresh_token(self, secret: str) -> str:
        refresh_key = self._settings.REFRESH_TOKEN_HMAC_KEY.encode("utf-8")
        return hmac.new(key=refresh_key, msg=secret.encode("utf-8"), digestmod=hashlib.sha256).hexdigest()

    def _create_access_token(self, user_id: UUID, sid: UUID, access_expire_at: datetime, now: datetime) -> str:
        access_payload = {
            "sub": str(user_id),
            "sid": str(sid),
            "jti": str(uuid7()),
            "iat": int(now.timestamp()),
            "exp": int(access_expire_at.timestamp()),
            "iss": self._settings.JWT_ISSUER,
            "aud": self._settings.JWT_AUDIENCE,
        }
        return jwt.encode(payload=access_payload, key=self._settings.ACCESS_TOKEN_HMAC_KEY, algorithm="HS256")

    def _create_csrf_token(self, sid: UUID, secret: str) -> str:
        csrf_signature = hmac.new(
            key=self._settings.CSRF_HMAC_KEY.encode("utf-8"),
            msg=f"{sid}.{secret}".encode(),
            digestmod=hashlib.sha256,
        ).hexdigest()
        return f"{secret}.{csrf_signature}"

    async def get_auth_session_by_id(self, sid: UUID) -> AuthSessionEntity | None:
        return await self._auth_session_repo.get_auth_session_by_id(sid=sid)

    async def user_logout(self, sid: UUID) -> None:
        session_entity = await self._auth_session_repo.get_auth_session_by_id(sid=sid)
        if session_entity is None:
            raise UnauthenticatedError

        token_entities = await self._auth_refresh_token_repo.get_auth_refresh_token_by_session_id(sid=sid)
        now = datetime.now(UTC)
        session_entity.revoke(now)
        for token_entity in token_entities:
            token_entity.revoke(now)

        async with self._uow:
            await self._auth_session_repo.update_auth_session(auth_session=session_entity)
            for token_entity in token_entities:
                await self._auth_refresh_token_repo.update_auth_refresh_token(token_entity)

            await self._uow.commit()

    async def update_refresh_and_access_tokens(
        self,
        refresh_token: str,
        device_id: str,
        csrf_token: str,
        csrf_token_from_header: str,
    ) -> UserAuthSessionResult:
        token_entity = await self._verify_refresh_token(refresh_token)
        now = datetime.now(UTC)
        token_entity.revoke(now)

        sid = token_entity.session_id
        if not self._comp_csrf_tokens(csrf_token=csrf_token, csrf_token_from_header=csrf_token_from_header, sid=sid):
            raise UnauthenticatedError

        session = await self._auth_session_repo.get_auth_session_by_id(sid=sid)
        device_id_hash = self._create_device_id_hash(device_id=device_id)
        if session is None or not session.is_active(now) or session.device_id_hash != device_id_hash:
            raise UnauthenticatedError

        expires_at = now + timedelta(seconds=self._settings.AUTH_SESSION_TTL_SECONDS)
        refresh_secret = secrets.token_urlsafe(32)
        refresh_token = AuthRefreshTokenEntity.create(
            session_id=sid,
            secret_hash=self._create_secret_hash_refresh_token(secret=refresh_secret),
            expires_at=expires_at,
        )
        device_id = secrets.token_urlsafe(32)
        session.expires_at = expires_at
        session.device_id_hash = self._create_device_id_hash(device_id=device_id)
        access_expire_at = now + timedelta(seconds=self._settings.ACCESS_TOKEN_TTL_SECONDS)
        access_token = self._create_access_token(
            user_id=session.user_id,
            sid=sid,
            access_expire_at=access_expire_at,
            now=now,
        )

        async with self._uow:
            await self._auth_refresh_token_repo.update_auth_refresh_token(refresh_token=token_entity)
            await self._auth_refresh_token_repo.create_refresh_token(refresh_token=refresh_token)
            await self._auth_session_repo.update_auth_session(auth_session=session)
            await self._uow.commit()

        return UserAuthSessionResult(
            sid=sid,
            access_token=access_token,
            access_token_expires_at=access_expire_at,
            refresh_token=f"{refresh_token.id}.{refresh_secret}",
            refresh_token_expires_at=refresh_token.expires_at,
            device_id=device_id,
            csrf_token=self._create_csrf_token(sid=sid, secret=secrets.token_urlsafe(32)),
        )

    def _comp_csrf_tokens(self, csrf_token: str, csrf_token_from_header: str, sid: UUID) -> bool:
        if csrf_token != csrf_token_from_header:
            return False

        try:
            csrf_nonce, _ = csrf_token.split(".")
        except ValueError as error:
            raise UnauthenticatedError from error

        return csrf_token == self._create_csrf_token(sid=sid, secret=csrf_nonce)

    async def _verify_refresh_token(self, refresh_token: str) -> AuthRefreshTokenEntity:
        try:
            token_id, refresh_secret = refresh_token.split(".")
        except ValueError as error:
            raise UnauthenticatedError from error

        try:
            token_id = UUID(token_id)
        except ValueError as error:
            raise UnauthenticatedError from error

        token_entity = await self._auth_refresh_token_repo.get_auth_refresh_token_by_token_id(token_id=token_id)
        secret_hash_refresh_token = self._create_secret_hash_refresh_token(refresh_secret)
        if token_entity is None:
            raise UnauthenticatedError

        if token_entity.secret_hash != secret_hash_refresh_token:
            raise UnauthenticatedError

        if not token_entity.is_active(datetime.now(UTC)):
            raise UnauthenticatedError

        return token_entity

    def _create_device_id_hash(self, device_id: str) -> str:
        device_key = self._settings.DEVICE_ID_HMAC_KEY.encode("utf-8")
        return hmac.new(key=device_key, msg=device_id.encode("utf-8"), digestmod=hashlib.sha256).hexdigest()
