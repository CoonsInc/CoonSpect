from redis.asyncio import Redis

from src.settings import settings

redis = Redis(
    host=settings.REDIS_HOST,
    port=settings.REDIS_PORT,
    db=0,
    decode_responses=True
)

async def get_redis() -> Redis:
    return redis
