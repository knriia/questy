import jwt
from dishka.integrations.fastapi import FromDishka, inject
from fastapi import HTTPException, Security, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from modules.auth.application.service import AuthService
from modules.auth.presentation.dto import AccessTokenClaims
from shared.config import Settings

access_scheme = HTTPBearer(bearerFormat="JWT", description="Access JWT", auto_error=False)


@inject
async def get_access_token_claims(
    settings: FromDishka[Settings],
    credentials: HTTPAuthorizationCredentials | None = Security(access_scheme),
) -> AccessTokenClaims:
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )

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
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid access token",
            headers={"WWW-Authenticate": "Bearer"},
        ) from error


async def get_current_current_user(
    auth_service: FromDishka[AuthService],
    principal: dict = Security(get_access_token_claims),
) -> None:
    pass
