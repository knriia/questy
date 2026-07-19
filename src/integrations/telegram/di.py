from dishka import Provider, Scope, provide

from src.core.config import Settings
from src.integrations.telegram.sender import TelegramSender


class TelegramSenderProvider(Provider):
    @provide(scope=Scope.APP)
    async def send_message(self, settings: Settings) -> TelegramSender:
        return TelegramSender(bot_token=settings.TELEGRAM_BOT_TOKEN)
