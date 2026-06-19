import datetime
import uuid

from pydantic import BaseModel, ConfigDict


class UserCreateDTO(BaseModel):
    nickname: str
    username: str
    email: str
    telegram_id: str | None = None


class UserReadDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    nickname: str
    username: str
    email: str
    telegram_id: str | None
    created_at: datetime.datetime
    updated_at: datetime.datetime
