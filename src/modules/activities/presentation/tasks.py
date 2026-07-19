from modules.activities.presentation.dto.activity_schedule_notification import ActivityScheduleNotificationPayload
from shared.logger import logger
from shared.taskiq import broker


@broker.task
async def send_activity_notification(payload: ActivityScheduleNotificationPayload) -> None:
    logger.info("Activity notification payload: %s", payload)
