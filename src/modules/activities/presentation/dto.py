import uuid
from datetime import datetime

from pydantic import BaseModel

from src.modules.activities.enums import ActivityStatus, ActivityType


class ActivityCreateDTO(BaseModel):
    user_id: uuid.UUID
    title: str
    description: str | None = None
    activity_type: ActivityType


class ActivityReadDTO(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    title: str
    description: str | None = None
    activity_type: ActivityType
    status: ActivityStatus
    created_at: datetime
    updated_at: datetime
