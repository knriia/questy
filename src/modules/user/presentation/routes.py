from typing import Annotated

from fastapi import APIRouter, Security

from modules.auth.presentation.dependencies import get_current_principal

user_router = APIRouter(prefix="/users", tags=["users"])


@user_router.get("/me")
async def get_principal(principal: Annotated[dict, Security(get_current_principal)]) -> dict:
    return principal
