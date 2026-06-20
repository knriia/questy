import uuid
from datetime import datetime

from pydantic import BaseModel

from src.modules.activity_records.enums import ActivityRecordStatus


class ActivityRecordCreateDTO(BaseModel):
    activity_id: uuid.UUID
    user_id: uuid.UUID
    status: ActivityRecordStatus
    data: dict


class ActivityRecordReadDTO(BaseModel):
    id: uuid.UUID
    activity_id: uuid.UUID
    user_id: uuid.UUID
    status: ActivityRecordStatus
    data: dict
    created_at: datetime
    updated_at: datetime
