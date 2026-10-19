from uuid import UUID

from pydantic import BaseModel


class Principal(BaseModel):
    user_id: UUID
    session_id: UUID
