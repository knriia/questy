from dishka import AsyncContainer, make_async_container

from src.core.db.di import DbProvider
from src.core.di import SettingsProvider
from src.integrations.telegram.di import TelegramSenderProvider
from src.modules.activities.di import ActivityProvider, ActivityScheduleProvider
from src.modules.activity_records.di import ActivityRecordProvider
from src.modules.users.di import UserProvider


def create_container() -> AsyncContainer:
    return make_async_container(
        SettingsProvider(),
        DbProvider(),
        UserProvider(),
        ActivityProvider(),
        ActivityRecordProvider(),
        ActivityScheduleProvider(),
        TelegramSenderProvider(),
    )
