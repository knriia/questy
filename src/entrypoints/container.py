from dishka import AsyncContainer, make_async_container

from integrations.telegram.di import TelegramSenderProvider
from modules.activity.di import ActivityProvider, ActivityScheduleProvider
from modules.activity_record.di import ActivityRecordProvider
from modules.auth.di import AuthProvider
from modules.user.di import UserProvider
from shared.db.di import DbProvider
from shared.di import SettingsProvider


def create_container() -> AsyncContainer:
    return make_async_container(
        SettingsProvider(),
        DbProvider(),
        UserProvider(),
        AuthProvider(),
        ActivityProvider(),
        ActivityRecordProvider(),
        ActivityScheduleProvider(),
        TelegramSenderProvider(),
    )
