from modules.activity_records.domain.entities import ActivityRecordEntity, SavedActivityRecordEntity
from modules.activity_records.enums import ActivityRecordStatus
from modules.activity_records.infrastructure.models import ActivityRecordModel


def activity_record_entity_to_model(activity_record_entity: ActivityRecordEntity) -> ActivityRecordModel:
    return ActivityRecordModel(
        id=activity_record_entity.id,
        activity_id=activity_record_entity.activity_id,
        user_id=activity_record_entity.user_id,
        status=activity_record_entity.status,
        data=activity_record_entity.data,
    )


def activity_record_model_to_entity(activity_record_model: ActivityRecordModel) -> SavedActivityRecordEntity:
    return SavedActivityRecordEntity(
        id=activity_record_model.id,
        activity_id=activity_record_model.activity_id,
        user_id=activity_record_model.user_id,
        status=ActivityRecordStatus(activity_record_model.status),
        data=activity_record_model.data,
        created_at=activity_record_model.created_at,
        updated_at=activity_record_model.updated_at,
    )
