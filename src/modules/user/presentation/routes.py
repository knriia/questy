from typing import Annotated

from fastapi import APIRouter, Security

from modules.auth.presentation.dto import UserRegisterResponse
from modules.auth.security.dependencies import get_access_token_claims

user_router = APIRouter(prefix="/users", tags=["users"])


@user_router.get("/me")
async def get_me(access_token_claims: Annotated[dict, Security(get_access_token_claims)]) -> UserRegisterResponse:
    return access_token_claims
