from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class ActivityScheduleNotificationPayload(BaseModel):
    schedule_id: UUID
    activity_id: UUID
    scheduled_at: datetime
