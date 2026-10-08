from datetime import UTC, datetime

from dishka.integrations.fastapi import FromDishka, inject
from fastapi import APIRouter, Request, Response, status

from modules.auth.application.dto import UserAuthCredentialCommand, UserRegisterCommand
from modules.auth.application.service import AuthService
from modules.auth.presentation.dto import (
    AuthSessionResponse,
    UserAuthCredentialRequest,
    UserRegisterRequest,
    UserRegisterResponse,
)

auth_router = APIRouter(prefix="/auth", tags=["auth"])


@auth_router.post("/register", status_code=status.HTTP_201_CREATED)
@inject
async def user_register(user_request: UserRegisterRequest, service: FromDishka[AuthService]) -> UserRegisterResponse:
    user = UserRegisterCommand(
        username=user_request.username,
        timezone=user_request.timezone,
        email=user_request.email,
        password=user_request.password,
    )
    user_result = await service.register_user(user_data=user)
    return UserRegisterResponse(
        id=user_result.user_id,
        username=user_result.username,
        timezone=user_result.timezone,
        status=user_result.status,
        email=user_result.email,
        created_at=user_result.created_at,
    )


@auth_router.post("/login", status_code=status.HTTP_200_OK)
@inject
async def user_login(
    request: Request, response: Response, user_auth_request: UserAuthCredentialRequest, service: FromDishka[AuthService]
) -> AuthSessionResponse:
    ip_address = request.client.host if request.client else "unknown"
    user_agent = request.headers.get("user-agent", "unknown")
    client_name = request.headers.get("x-client-name", "unknown")

    user_auth_command = UserAuthCredentialCommand(
        identifier=user_auth_request.identifier,
        password=user_auth_request.password,
        ip_address=ip_address,
        user_agent=user_agent,
        client_name=client_name,
    )
    auth_session = await service.auth_user(user_data=user_auth_command)
    response.set_cookie(
        key="refresh_token",
        value=auth_session.refresh_token,
        httponly=True,
        secure=True,
        samesite="lax",
        path="/auth",
        max_age=int((auth_session.refresh_token_expires_at - datetime.now(UTC)).total_seconds()),
    )
    response.set_cookie(
        key="device_id",
        value=auth_session.device_id,
        httponly=True,
        secure=True,
        samesite="lax",
        path="/auth",
    )
    response.set_cookie(
        key="csrf_token",
        value=auth_session.csrf_token,
        httponly=False,
        secure=True,
        samesite="lax",
        path="/",
    )

    return AuthSessionResponse(
        access_token=auth_session.access_token,
        access_token_expires_at=auth_session.access_token_expires_at,
        csrf_token=auth_session.csrf_token,
    )
