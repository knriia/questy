from collections.abc import Awaitable, Callable

from modules.activities.presentation.dto.activity_schedule_notification import ActivityScheduleNotificationPayload


class ActivityNotificationTaskSender:
    def __init__(self, enqueue: Callable[[ActivityScheduleNotificationPayload], Awaitable[None]]) -> None:
        self.enqueue = enqueue

    async def send_activity_notification(self, payload: ActivityScheduleNotificationPayload) -> None:
        await self.enqueue(payload)
