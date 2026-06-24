from src.modules.activities.domain.entities.activity_schedule import ActivityScheduleEntity, SavedActivityScheduleEntity
from src.modules.activities.enums import ActivityScheduleType
from src.modules.activities.infrastructure.models.activity_schedule import ActivityScheduleModel


def activity_schedule_entity_to_model(activity_schedule_entity: ActivityScheduleEntity) -> ActivityScheduleModel:
    return ActivityScheduleModel(
        id=activity_schedule_entity.id,
        activity_id=activity_schedule_entity.activity_id,
        schedule_type=activity_schedule_entity.schedule_type,
        interval_minutes=activity_schedule_entity.interval_minutes,
        next_run_at=activity_schedule_entity.next_run_at,
        timezone=activity_schedule_entity.timezone,
        is_enabled=activity_schedule_entity.is_enabled,
        last_run_at=activity_schedule_entity.last_run_at,
    )


def activity_schedule_model_to_entity(activity_schedule_model: ActivityScheduleModel) -> SavedActivityScheduleEntity:
    return SavedActivityScheduleEntity(
        id=activity_schedule_model.id,
        activity_id=activity_schedule_model.activity_id,
        schedule_type=ActivityScheduleType(activity_schedule_model.schedule_type),
        interval_minutes=activity_schedule_model.interval_minutes,
        next_run_at=activity_schedule_model.next_run_at,
        timezone=activity_schedule_model.timezone,
        is_enabled=activity_schedule_model.is_enabled,
        last_run_at=activity_schedule_model.last_run_at,
        created_at=activity_schedule_model.created_at,
        updated_at=activity_schedule_model.updated_at,
    )
