from sqlalchemy.ext.asyncio import AsyncSession

from src.modules.activity_records.domain.entities import ActivityRecordEntity, SavedActivityRecordEntity
from src.modules.activity_records.enums import ActivityRecordStatus
from src.modules.activity_records.infrastructure.models import ActivityRecordModel


class ActivityRecordRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def save_activity_record(self, activity_record: ActivityRecordEntity) -> SavedActivityRecordEntity:
        model = ActivityRecordModel(
            id=activity_record.id,
            activity_id=activity_record.activity_id,
            user_id=activity_record.user_id,
            status=activity_record.status,
            data=activity_record.data,
        )
        self.session.add(model)
        await self.session.commit()
        await self.session.refresh(model)
        return SavedActivityRecordEntity(
            id=model.id,
            activity_id=model.activity_id,
            user_id=model.user_id,
            status=ActivityRecordStatus(model.status),
            data=model.data,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )
