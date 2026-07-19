import uuid
from datetime import datetime

from pydantic import BaseModel

from modules.activities.enums import ActivityScheduleType


class ActivityScheduleCreateDTO(BaseModel):
    activity_id: uuid.UUID
    schedule_type: ActivityScheduleType
    interval_minutes: int | None = None
    next_run_at: datetime
    timezone: str
    is_enabled: bool = True


class ActivityScheduleReadDTO(BaseModel):
    id: uuid.UUID
    activity_id: uuid.UUID
    schedule_type: ActivityScheduleType
    interval_minutes: int | None
    next_run_at: datetime
    last_run_at: datetime | None
    timezone: str
    is_enabled: bool
    created_at: datetime
    updated_at: datetime
