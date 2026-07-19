from taskiq_redis import ListQueueBroker

from shared.config import Settings

settings = Settings()
broker = ListQueueBroker(
    settings.REDIS_URL,
    queue_name="questy",
    socket_timeout=None,
)
