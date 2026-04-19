import taskiq_fastapi
from taskiq_redis import RedisAsyncResultBackend, ListQueueBroker
from typing import Any

from src.settings import settings

# 1. Настраиваем хранилище результатов (Result Backend)
# Именно сюда воркеры будут записывать ответы, чтобы ты мог их забрать через get_result()
result_backend = RedisAsyncResultBackend(
    redis_url=str(settings.REDIS_URL),
    keep_results = False,
    result_ex_time=7200
)

# 2. Создаем брокер и привязываем к нему Backend
broker = ListQueueBroker(
    str(settings.REDIS_URL),
).with_result_backend(result_backend)

# 3. Инициализация для FastAPI
taskiq_fastapi.init(broker, "src.main:app")


async def get_progress(task_id: str) -> dict[str, Any] | None:
    progress = await result_backend.get_progress(task_id)

    if progress is None:
        return None
    
    return {
        "state": progress.state,
        "meta": progress.meta
    }
