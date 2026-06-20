from sqlalchemy.ext.asyncio import AsyncSession

from src.modules.activities.domain.entities import ActivityEntity, SavedActivityEntity
from src.modules.activities.enums import ActivityStatus, ActivityType
from src.modules.activities.infrastructure.models import ActivityModel


class ActivityRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def save_activity(self, activity: ActivityEntity) -> SavedActivityEntity:
        model = ActivityModel(
            id=activity.id,
            user_id=activity.user_id,
            title=activity.title,
            description=activity.description,
            activity_type=activity.activity_type,
            status=activity.status,
        )
        self.session.add(model)
        await self.session.commit()
        await self.session.refresh(model)
        return SavedActivityEntity(
            id=model.id,
            user_id=model.user_id,
            title=model.title,
            description=model.description,
            activity_type=ActivityType(model.activity_type),
            status=ActivityStatus(model.status),
            created_at=model.created_at,
            updated_at=model.updated_at,
        )
