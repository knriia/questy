from src.modules.activity_records.domain.entities import ActivityRecordEntity, SavedActivityRecordEntity
from src.modules.activity_records.presentation.dto import ActivityRecordCreateDTO, ActivityRecordReadDTO


def activity_record_entity_to_dto(activity_record_entity: SavedActivityRecordEntity) -> ActivityRecordReadDTO:
    return ActivityRecordReadDTO(
        id=activity_record_entity.id,
        activity_id=activity_record_entity.activity_id,
        user_id=activity_record_entity.user_id,
        status=activity_record_entity.status,
        data=activity_record_entity.data,
        created_at=activity_record_entity.created_at,
        updated_at=activity_record_entity.updated_at,
    )


def activity_record_dto_to_entity(activity_record_dto: ActivityRecordCreateDTO) -> ActivityRecordEntity:
    return ActivityRecordEntity.create(
        user_id=activity_record_dto.user_id,
        activity_id=activity_record_dto.activity_id,
        status=activity_record_dto.status,
        data=activity_record_dto.data,
    )
