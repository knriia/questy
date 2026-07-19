from aiogram import Bot


class TelegramSender:
    def __init__(self, bot_token: str) -> None:
        self.bot = Bot(bot_token)

    async def send_message(self, telegram_id: str, text: str) -> None:
        await self.bot.send_message(chat_id=telegram_id, text=text)
