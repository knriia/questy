from modules.activities.domain.entities.activity_schedule import ActivityScheduleEntity, SavedActivityScheduleEntity
from modules.activities.presentation.dto.activity_schedule import ActivityScheduleCreateDTO, ActivityScheduleReadDTO


def activity_schedule_entity_to_dto(activity_schedule_entity: SavedActivityScheduleEntity) -> ActivityScheduleReadDTO:
    return ActivityScheduleReadDTO(
        id=activity_schedule_entity.id,
        activity_id=activity_schedule_entity.activity_id,
        schedule_type=activity_schedule_entity.schedule_type,
        interval_minutes=activity_schedule_entity.interval_minutes,
        next_run_at=activity_schedule_entity.next_run_at,
        timezone=activity_schedule_entity.timezone,
        is_enabled=activity_schedule_entity.is_enabled,
        last_run_at=activity_schedule_entity.last_run_at,
        created_at=activity_schedule_entity.created_at,
        updated_at=activity_schedule_entity.updated_at,
    )


def activity_schedule_dto_to_entity(activity_schedule_dto: ActivityScheduleCreateDTO) -> ActivityScheduleEntity:
    return ActivityScheduleEntity.create(
        activity_id=activity_schedule_dto.activity_id,
        schedule_type=activity_schedule_dto.schedule_type,
        interval_minutes=activity_schedule_dto.interval_minutes,
        next_run_at=activity_schedule_dto.next_run_at,
        timezone=activity_schedule_dto.timezone,
        is_enabled=activity_schedule_dto.is_enabled,
    )
