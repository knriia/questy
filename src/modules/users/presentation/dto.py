import uuid
from datetime import datetime
from typing import Annotated

from pydantic import BaseModel, ConfigDict, StringConstraints

from modules.users.domain.enums import UserStatus


class UserCreateDTO(BaseModel):
    username: Annotated[str, StringConstraints(strip_whitespace=True, min_length=3, max_length=30)]
    timezone: Annotated[str, StringConstraints(strip_whitespace=True, min_length=3, max_length=100)]
    email: Annotated[str, StringConstraints(strip_whitespace=True, max_length=254)]
    password: Annotated[str, StringConstraints(min_length=15, max_length=100)]


class UserReadDTO(BaseModel):
    id: uuid.UUID
    username: str
    timezone: str
    status: UserStatus
    email: str
    email_verified: bool
    created_at: datetime
    updated_at: datetime
    deleted_at: datetime | None

    model_config = ConfigDict(from_attributes=True)
