from sqlalchemy.ext.asyncio import AsyncSession

from modules.activities.domain.entities.activity import ActivityEntity, SavedActivityEntity
from modules.activities.infrastructure.mappers.activity import activity_entity_to_model, activity_model_to_entity


class ActivityRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def save_activity(self, activity: ActivityEntity) -> SavedActivityEntity:
        model = activity_entity_to_model(activity_entity=activity)
        self.session.add(model)
        await self.session.commit()
        await self.session.refresh(model)
        return activity_model_to_entity(activity_model=model)
