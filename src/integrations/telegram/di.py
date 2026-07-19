from dishka import Provider, Scope, provide

from integrations.telegram.sender import TelegramSender
from shared.config import Settings


class TelegramSenderProvider(Provider):
    @provide(scope=Scope.APP)
    async def send_message(self, settings: Settings) -> TelegramSender:
        return TelegramSender(bot_token=settings.TELEGRAM_BOT_TOKEN)
