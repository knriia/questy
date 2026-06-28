from taskiq_redis import ListQueueBroker

from src.core.config import Settings

settings = Settings()
broker = ListQueueBroker(settings.REDIS_URL)
