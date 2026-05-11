import taskiq_fastapi
from taskiq import InMemoryBroker, SimpleRetryMiddleware
from taskiq_redis import ListQueueBroker, RedisAsyncResultBackend

from src.settings import settings

broker = (
    ListQueueBroker(
        str(settings.REDIS_URL),
    )
    .with_result_backend(
        RedisAsyncResultBackend(
            redis_url=str(settings.REDIS_URL), keep_results=False, result_ex_time=7200
        )
    )
    .with_middlewares(SimpleRetryMiddleware())
)

print(settings.ENVIRONMENT)
if settings.ENVIRONMENT and settings.ENVIRONMENT == "pytest":
    broker = InMemoryBroker()

taskiq_fastapi.init(broker, "src.main:app")
