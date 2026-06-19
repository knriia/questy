from dishka import Provider, Scope, provide

from src.core.config import Settings


class SettingsProvider(Provider):
    @provide(scope=Scope.APP)
    def settings(self) -> Settings:
        return Settings()
