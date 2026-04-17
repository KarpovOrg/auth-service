from taskiq import TaskiqScheduler
from taskiq_redis import (
    ListRedisScheduleSource,
    RedisAsyncResultBackend,
    RedisStreamBroker,
)

from core.config import settings


broker = RedisStreamBroker(
    url=settings.redis.url,
).with_result_backend(RedisAsyncResultBackend(redis_url=settings.redis.url))

scheduler = TaskiqScheduler(
    broker=broker,
    sources=[ListRedisScheduleSource(url=settings.redis.url)],
)