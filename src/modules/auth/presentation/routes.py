from datetime import UTC, datetime
from typing import Annotated

from dishka.integrations.fastapi import FromDishka, inject
from fastapi import APIRouter, Header, Request, Response, Security, status

from modules.auth.application.dto import UserAuthCredentialCommand, UserAuthSessionResult, UserRegisterCommand
from modules.auth.application.service import AuthService
from modules.auth.presentation.dto import (
    AuthSessionResponse,
    UserAuthCredentialRequest,
    UserRegisterRequest,
    UserRegisterResponse,
)
from modules.auth.security.dependencies import get_current_principal
from modules.auth.security.dto import Principal

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
    request: Request,
    response: Response,
    user_auth_request: UserAuthCredentialRequest,
    service: FromDishka[AuthService],
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
    set_cookies_in_response(response=response, auth_session=auth_session)

    return AuthSessionResponse(
        access_token=auth_session.access_token,
        access_token_expires_at=auth_session.access_token_expires_at,
        csrf_token=auth_session.csrf_token,
    )


@auth_router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
@inject
async def user_logout(
    response: Response,
    auth_service: FromDishka[AuthService],
    current_principal: Annotated[Principal, Security(get_current_principal)],
) -> None:
    await auth_service.user_logout(current_principal.session_id)
    response.delete_cookie(key="refresh_token", path="/auth")
    response.delete_cookie(key="device_id", path="/auth")
    response.delete_cookie(key="csrf_token")


@auth_router.post("/refresh", status_code=status.HTTP_200_OK)
@inject
async def update_refresh_and_access_tokens(
    request: Request,
    response: Response,
    auth_service: FromDishka[AuthService],
    csrf_token_from_header: Annotated[str, Header(alias="csrf_token")],
) -> AuthSessionResponse:
    cookies = request.cookies
    refresh_token = cookies.get("refresh_token", "")
    device_id = cookies.get("device_id", "")
    csrf_token = cookies.get("csrf_token", "")
    auth_session = await auth_service.update_refresh_and_access_tokens(
        refresh_token=refresh_token,
        device_id=device_id,
        csrf_token=csrf_token,
        csrf_token_from_header=csrf_token_from_header,
    )
    set_cookies_in_response(response=response, auth_session=auth_session)
    return AuthSessionResponse(
        access_token=auth_session.access_token,
        access_token_expires_at=auth_session.access_token_expires_at,
        csrf_token=auth_session.csrf_token,
    )


def set_cookies_in_response(response: Response, auth_session: UserAuthSessionResult) -> None:
    max_age = int((auth_session.refresh_token_expires_at - datetime.now(UTC)).total_seconds())
    response.set_cookie(
        key="refresh_token",
        value=auth_session.refresh_token,
        httponly=True,
        secure=True,
        samesite="lax",
        path="/auth",
        max_age=max_age,
    )
    response.set_cookie(
        key="device_id",
        value=auth_session.device_id,
        httponly=True,
        secure=True,
        samesite="lax",
        path="/auth",
        max_age=max_age,
    )
    response.set_cookie(
        key="csrf_token",
        value=auth_session.csrf_token,
        httponly=False,
        secure=True,
        samesite="lax",
        path="/",
        max_age=max_age,
    )
