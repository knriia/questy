from modules.activities.domain.entities.activity import ActivityEntity, SavedActivityEntity
from modules.activities.presentation.dto.activity import ActivityCreateDTO, ActivityReadDTO


def activity_entity_to_dto(activity_entity: SavedActivityEntity) -> ActivityReadDTO:
    return ActivityReadDTO(
        id=activity_entity.id,
        user_id=activity_entity.user_id,
        title=activity_entity.title,
        description=activity_entity.description,
        activity_type=activity_entity.activity_type,
        status=activity_entity.status,
        fields_schema=activity_entity.fields_schema,
        created_at=activity_entity.created_at,
        updated_at=activity_entity.updated_at,
    )


def activity_dto_to_entity(activity_dto: ActivityCreateDTO) -> ActivityEntity:
    return ActivityEntity.create(
        user_id=activity_dto.user_id,
        title=activity_dto.title,
        description=activity_dto.description,
        activity_type=activity_dto.activity_type,
        fields_schema=activity_dto.fields_schema,
    )
