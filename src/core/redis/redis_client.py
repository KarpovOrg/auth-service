from .base import BaseRedisClient

from core.config import settings


redis_client = BaseRedisClient(
    url=settings.redis.url,
    max_connections=settings.redis.max_connections,
)