import logging

from modules.activities.presentation.tasks import send_activity_notification
from shared.logger import setup_logging
from shared.taskiq import broker

__all__ = ["broker", "send_activity_notification"]

setup_logging()

logger = logging.getLogger("activity_notification_worker")
