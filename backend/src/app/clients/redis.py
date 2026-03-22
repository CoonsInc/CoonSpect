from redis import Redis as RedisSync
from redis.asyncio import Redis as RedisAsync

from src.app.settings import settings

redis_sync = RedisSync(
    host = settings.REDIS_HOST,
    port = settings.REDIS_PORT,
    db = 0,
    decode_responses = True
)

redis_async = RedisAsync(
    host=settings.REDIS_HOST,
    port=settings.REDIS_PORT,
    db=0,
    decode_responses=True
)
