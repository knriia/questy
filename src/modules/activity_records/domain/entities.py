from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from uuid6 import uuid6

from src.modules.activity_records.enums import ActivityRecordStatus


@dataclass
class ActivityRecordEntity:
    id: UUID
    activity_id: UUID
    user_id: UUID
    status: ActivityRecordStatus
    data: dict

    @classmethod
    def create(
        cls,
        activity_id: UUID,
        user_id: UUID,
        status: ActivityRecordStatus,
        data: dict,
    ) -> "ActivityRecordEntity":
        return cls(
            id=uuid6(),
            activity_id=activity_id,
            user_id=user_id,
            status=status,
            data=data,
        )


@dataclass
class SavedActivityRecordEntity(ActivityRecordEntity):
    created_at: datetime
    updated_at: datetime
