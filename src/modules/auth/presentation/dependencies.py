import jwt
from dishka.integrations.fastapi import FromDishka, inject
from fastapi import HTTPException, Security, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from modules.auth.application.service import AuthService
from shared.config import Settings

access_scheme = HTTPBearer(bearerFormat="JWT", description="Access JWT", auto_error=False)


@inject
async def get_current_principal(
    settings: FromDishka[Settings],
    credentials: HTTPAuthorizationCredentials | None = Security(access_scheme),
) -> dict:
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        return jwt.decode(
            credentials.credentials,
            settings.ACCESS_TOKEN_HMAC_KEY,
            algorithms=["HS256"],
            issuer=settings.JWT_ISSUER,
            audience=settings.JWT_AUDIENCE,
        )
    except jwt.PyJWTError as error:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid access token",
            headers={"WWW-Authenticate": "Bearer"},
        ) from error


async def get_current_current_user(
    auth_service: FromDishka[AuthService],
    principal: dict = Security(get_current_principal),
) -> None:
    return auth_service.get_user_credential()
