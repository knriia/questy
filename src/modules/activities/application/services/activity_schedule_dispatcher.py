from datetime import datetime

from src.modules.activities.application.services.activity_schedule import ActivityScheduleService
from src.modules.activities.application.services.activity_schedule_task_sender import ActivityNotificationTaskSender
from src.modules.activities.presentation.dto.activity_schedule_notification import ActivityScheduleNotificationPayload


class ActivityScheduleDispatcher:
    def __init__(self, service: ActivityScheduleService, task_sender: ActivityNotificationTaskSender):
        self.service = service
        self.task_sender = task_sender

    async def dispatch_due(self, now: datetime) -> None:
        activity_schedules = await self.service.get_due_activity_schedules(now=now)
        for activity_schedule in activity_schedules:
            payload = ActivityScheduleNotificationPayload(
                schedule_id=activity_schedule.id,
                activity_id=activity_schedule.activity_id,
                scheduled_at=now,
            )
            await self.task_sender.send_activity_notification(payload=payload)
            await self.service.update_next_run_activity_schedule(
                activity_schedule=activity_schedule,
                now=now,
            )
