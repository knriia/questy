from dishka import make_async_container

from src.core.di.config import SettingsProvider
from src.core.di.db import DbProvider

container = make_async_container(
    SettingsProvider(),
    DbProvider(),
)
