from datetime import UTC, datetime
from typing import Annotated
from uuid import UUID

import jwt
from dishka.integrations.fastapi import FromDishka, inject
from fastapi import Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from modules.auth.application.service import AuthService
from modules.auth.domain.exceptions import UnauthenticatedError
from modules.auth.presentation.dto import AccessTokenClaims
from modules.auth.security.dto import Principal
from shared.config import Settings

access_scheme = HTTPBearer(bearerFormat="JWT", description="Access JWT", auto_error=False)


@inject
async def get_access_token_claims(
    settings: FromDishka[Settings],
    credentials: HTTPAuthorizationCredentials | None = Security(access_scheme),
) -> AccessTokenClaims:
    if credentials is None:
        raise UnauthenticatedError

    try:
        token_clims = jwt.decode(
            credentials.credentials,
            settings.ACCESS_TOKEN_HMAC_KEY,
            algorithms=["HS256"],
            issuer=settings.JWT_ISSUER,
            audience=settings.JWT_AUDIENCE,
        )
        return AccessTokenClaims(
            sub=token_clims.get("sub"),
            sid=token_clims.get("sid"),
            jti=token_clims.get("jti"),
            iat=token_clims.get("iat"),
            exp=token_clims.get("exp"),
            iss=token_clims.get("iss"),
            aud=token_clims.get("aud"),
        )
    except jwt.PyJWTError as error:
        raise UnauthenticatedError("Invalid access token") from error


@inject
async def get_current_principal(
    auth_service: FromDishka[AuthService],
    access_token_claims: Annotated[AccessTokenClaims, Security(get_access_token_claims)],
) -> Principal:
    session_entity = await auth_service.get_auth_session_by_id(UUID(access_token_claims.sid))
    now = datetime.now(UTC)
    if session_entity and session_entity.is_active(now) and session_entity.user_id == UUID(access_token_claims.sub):
        return Principal(
            user_id=session_entity.user_id,
            session_id=session_entity.id,
        )

    raise UnauthenticatedError
