import taskiq_redis
from taskiq import InMemoryBroker

from src.settings import settings

# Для разработки можно InMemory, для продакшена - Redis
broker = taskiq_redis.ListQueueBroker(settings.REDIS_URL)

