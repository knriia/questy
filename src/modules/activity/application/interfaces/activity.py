from abc import ABC, abstractmethod

from modules.activity.domain.entities.activity import ActivityEntity, SavedActivityEntity


class IActivityRepository(ABC):
    @abstractmethod
    async def create_activity(self, activity: ActivityEntity) -> SavedActivityEntity:
        pass
