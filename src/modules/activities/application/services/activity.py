from src.modules.activities.domain.entities.activity import ActivityEntity, SavedActivityEntity
from src.modules.activities.infrastructure.repositories.activity import ActivityRepository


class ActivityService:
    def __init__(self, repository: ActivityRepository):
        self.repository = repository

    async def create_activity(self, activity: ActivityEntity) -> SavedActivityEntity:
        return await self.repository.save_activity(activity=activity)
