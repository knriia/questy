from uuid import UUID

from pydantic import BaseModel


class UserMeResponse(BaseModel):
    id: UUID
    username: str
    timezone: str
    email: str
