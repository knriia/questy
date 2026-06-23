from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from uuid6 import uuid6

from src.modules.activities.enums import ActivityScheduleType


@dataclass(kw_only=True)
class ActivityScheduleEntity:
    id: UUID
    activity_id: UUID
    schedule_type: ActivityScheduleType
    interval_minutes: int | None
    next_run_at: datetime
    timezone: str
    is_enabled: bool
    last_run_at: datetime | None = None

    @classmethod
    def create(
        cls,
        activity_id: UUID,
        schedule_type: ActivityScheduleType,
        interval_minutes: int | None,
        next_run_at: datetime,
        timezone: str,
        is_enabled: bool,
        last_run_at: datetime | None = None,
    ) -> "ActivityScheduleEntity":
        return cls(
            id=uuid6(),
            activity_id=activity_id,
            schedule_type=schedule_type,
            interval_minutes=interval_minutes,
            next_run_at=next_run_at,
            timezone=timezone,
            is_enabled=is_enabled,
            last_run_at=last_run_at,
        )


@dataclass
class SavedActivityScheduleEntity(ActivityScheduleEntity):
    created_at: datetime
    updated_at: datetime
