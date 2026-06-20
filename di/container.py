from dishka import make_async_container

from src.core.db.di import DbProvider
from src.core.di import SettingsProvider
from src.modules.activities.di import ActivityProvider
from src.modules.users.di import UserProvider

container = make_async_container(
    SettingsProvider(),
    DbProvider(),
    UserProvider(),
    ActivityProvider(),
)
