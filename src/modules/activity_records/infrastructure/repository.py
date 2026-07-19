from sqlalchemy.ext.asyncio import AsyncSession

from modules.activity_records.domain.entities import ActivityRecordEntity, SavedActivityRecordEntity
from modules.activity_records.infrastructure.mappers import (
    activity_record_entity_to_model,
    activity_record_model_to_entity,
)


class ActivityRecordRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def save_activity_record(self, activity_record: ActivityRecordEntity) -> SavedActivityRecordEntity:
        model = activity_record_entity_to_model(activity_record_entity=activity_record)
        self.session.add(model)
        await self.session.commit()
        await self.session.refresh(model)
        return activity_record_model_to_entity(activity_record_model=model)
