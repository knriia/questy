from dishka import make_async_container

from src.core.db.di import DbProvider
from src.core.di import SettingsProvider
from src.modules.activities.di import ActivityProvider, ScheduleProvider
from src.modules.activity_records.di import ActivityRecordProvider
from src.modules.users.di import UserProvider

container = make_async_container(
    SettingsProvider(),
    DbProvider(),
    UserProvider(),
    ActivityProvider(),
    ActivityRecordProvider(),
    ScheduleProvider(),
)
