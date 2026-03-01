from redis import Redis as RedisSync
from redis.asyncio import Redis as RedisAsync

import src.app.config as config

redis_sync = RedisSync(
    host = config.REDIS_HOST,
    port = config.REDIS_PORT,
    db = 0,
    decode_responses = True
)

redis_async = RedisAsync(
    host=config.REDIS_HOST,
    port=config.REDIS_PORT,
    db=0,
    decode_responses=True
)
