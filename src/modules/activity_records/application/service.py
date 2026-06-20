from src.modules.activity_records.domain.entities import ActivityRecordEntity, SavedActivityRecordEntity
from src.modules.activity_records.infrastructure.repository import ActivityRecordRepository


class ActivityRecordService:
    def __init__(self, repository: ActivityRecordRepository):
        self.repository = repository

    async def create_activity_record(self, activity_record: ActivityRecordEntity) -> SavedActivityRecordEntity:
        return await self.repository.save_activity_record(activity_record=activity_record)
