from src.modules.activities.domain.entity import ActivityEntity, SavedActivityEntity
from src.modules.activities.infrastructure.repository import ActivityRepository


class ActivityService:
    def __init__(self, repository: ActivityRepository):
        self.repository = repository

    async def create_activity(self, activity: ActivityEntity) -> SavedActivityEntity:
        return await self.repository.save_activity(activity=activity)
