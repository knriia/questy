import logging

from modules.activities.presentation.dto.activity_schedule_notification import ActivityScheduleNotificationPayload
from shared.taskiq import broker

logger = logging.getLogger(__name__)


@broker.task
async def send_activity_notification(payload: ActivityScheduleNotificationPayload) -> None:
    logger.info("Activity notification payload: %s", payload)
