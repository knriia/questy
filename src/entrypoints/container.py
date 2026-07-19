from dishka import AsyncContainer, make_async_container

from integrations.telegram.di import TelegramSenderProvider
from modules.activities.di import ActivityProvider, ActivityScheduleProvider
from modules.activity_records.di import ActivityRecordProvider
from modules.users.di import UserProvider
from shared.db.di import DbProvider
from shared.di import SettingsProvider


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
