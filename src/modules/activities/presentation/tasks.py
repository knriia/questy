from src.core.logger import logger
from src.core.taskiq import broker
from src.modules.activities.presentation.dto.activity_schedule_notification import ActivityScheduleNotificationPayload


@broker.task
async def send_activity_notification(payload: ActivityScheduleNotificationPayload) -> None:
    logger.info("Activity notification payload: %s", payload)
