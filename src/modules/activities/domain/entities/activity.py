from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from uuid6 import uuid6

from modules.activities.enums import ActivityStatus, ActivityType


@dataclass
class ActivityEntity:
    id: UUID
    user_id: UUID
    title: str
    description: str | None
    activity_type: ActivityType
    status: ActivityStatus
    fields_schema: dict

    @classmethod
    def create(
        cls,
        user_id: UUID,
        title: str,
        activity_type: ActivityType,
        fields_schema: dict,
        description: str | None = None,
    ) -> "ActivityEntity":
        return cls(
            id=uuid6(),
            user_id=user_id,
            title=title,
            activity_type=activity_type,
            description=description,
            status=ActivityStatus.ACTIVE,
            fields_schema=fields_schema,
        )


@dataclass
class SavedActivityEntity(ActivityEntity):
    created_at: datetime
    updated_at: datetime
