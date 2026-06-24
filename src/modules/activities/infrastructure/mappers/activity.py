from src.modules.activities.domain.entities.activity import ActivityEntity, SavedActivityEntity
from src.modules.activities.enums import ActivityStatus, ActivityType
from src.modules.activities.infrastructure.models.activity import ActivityModel


def activity_entity_to_model(activity_entity: ActivityEntity) -> ActivityModel:
    return ActivityModel(
        id=activity_entity.id,
        user_id=activity_entity.user_id,
        title=activity_entity.title,
        description=activity_entity.description,
        activity_type=activity_entity.activity_type,
        status=activity_entity.status,
        fields_schema=activity_entity.fields_schema,
    )


def activity_model_to_entity(activity_model: ActivityModel) -> SavedActivityEntity:
    return SavedActivityEntity(
        id=activity_model.id,
        user_id=activity_model.user_id,
        title=activity_model.title,
        description=activity_model.description,
        activity_type=ActivityType(activity_model.activity_type),
        status=ActivityStatus(activity_model.status),
        fields_schema=activity_model.fields_schema,
        created_at=activity_model.created_at,
        updated_at=activity_model.updated_at,
    )
