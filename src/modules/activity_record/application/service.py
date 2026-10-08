from modules.activity_record.domain.entities import ActivityRecordEntity, SavedActivityRecordEntity
from modules.activity_record.infrastructure.repository import ActivityRecordRepository


class ActivityRecordService:
    def __init__(self, repository: ActivityRecordRepository):
        self.repository = repository

    async def create_activity_record(self, activity_record: ActivityRecordEntity) -> SavedActivityRecordEntity:
        return await self.repository.save_activity_record(activity_record=activity_record)
