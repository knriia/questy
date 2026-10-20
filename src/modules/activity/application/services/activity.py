from modules.activity.application.interfaces.activity import IActivityRepository
from modules.activity.domain.entities.activity import ActivityEntity, SavedActivityEntity
from shared.iuow import IUoW


class ActivityService:
    def __init__(self, repository: IActivityRepository, uow: IUoW):
        self._repository = repository
        self._uow = uow

    async def create_activity(self, activity: ActivityEntity) -> SavedActivityEntity:
        async with self._uow:
            saved_activity = await self._repository.create_activity(activity=activity)
            await self._uow.commit()

        return saved_activity
