from dishka import make_async_container

from di.config import SettingsProvider
from di.db import DbProvider
from src.modules.activities.di import ActivityProvider
from src.modules.users.di import UserProvider

container = make_async_container(
    SettingsProvider(),
    DbProvider(),
    UserProvider(),
    ActivityProvider(),
)
