from sqlalchemy.ext.asyncio import AsyncSession

from modules.activity.application.interfaces.activity import IActivityRepository
from modules.activity.domain.entities.activity import ActivityEntity, SavedActivityEntity
from modules.activity.infrastructure.mappers.activity import activity_entity_to_model, activity_model_to_entity


class ActivityRepository(IActivityRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_activity(self, activity: ActivityEntity) -> SavedActivityEntity:
        model = activity_entity_to_model(activity_entity=activity)
        self.session.add(model)
        await self.session.flush()
        return activity_model_to_entity(activity_model=model)
