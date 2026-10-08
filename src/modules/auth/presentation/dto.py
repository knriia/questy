import uuid
from datetime import datetime
from typing import Annotated

from pydantic import BaseModel, ConfigDict, StringConstraints

from modules.user.domain.enums import UserStatus


class UserRegisterRequest(BaseModel):
    username: Annotated[str, StringConstraints(strip_whitespace=True, min_length=3, max_length=30)]
    timezone: Annotated[str, StringConstraints(strip_whitespace=True, min_length=3, max_length=100)]
    email: Annotated[str, StringConstraints(strip_whitespace=True, max_length=100)]
    password: Annotated[str, StringConstraints(min_length=15, max_length=100)]


class UserRegisterResponse(BaseModel):
    id: uuid.UUID
    username: str
    timezone: str
    status: UserStatus
    email: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class UserAuthCredentialRequest(BaseModel):
    identifier: str
    password: str


class AuthSessionResponse(BaseModel):
    access_token: str
    access_token_expires_at: datetime
    csrf_token: str
