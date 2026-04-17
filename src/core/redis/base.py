import json

from typing import Any

from redis.asyncio import Redis
from redis.asyncio.connection import ConnectionPool


class BaseRedisClient:
    def __init__(
            self,
            url: str,
            max_connections: int,
    ) -> None:
        self.url = url
        self.max_connections = max_connections
        self.pool = ConnectionPool.from_url(
            url=self.url,
            max_connections=self.max_connections,
            decode_responses=True,
        )
        self.redis: Redis | None = None

    async def connect(self) -> None:
        self.redis = Redis(
            connection_pool=self.pool,
        )

    async def disconnect(self) -> None:
        if self.redis:
            await self.redis.close()

    async def get(
            self,
            key: str,
    ) -> Any | None:
        if not self.redis:
            return None

        data = await self.redis.get(key)
        if data:
            try:
                return json.loads(data)
            except json.JSONDecodeError:
                return data
        return None

    async def set(
            self,
            key: str,
            value: Any,
            ttl: int = 300,
    ) -> bool:
        if not self.redis:
            return False

        if isinstance(
                value,
                (dict, list, tuple),
        ):
            value = json.dumps(
                value,
                ensure_ascii=False,
            )

        return await self.redis.setex(
            key,
            ttl,
            value,
        )

    async def delete(
            self,
            key: str,
    ) -> bool:
        if not self.redis:
            return False
        return await self.redis.delete(key)

    async def lrange(self, key: str, start: int, end: int) -> list:
        if not self.redis:
            return []
        return await self.redis.lrange(key, start, end)

    async def rpush(self, key: str, *values: Any) -> int:
        if not self.redis:
            return 0
        return await self.redis.rpush(key, *values)

    async def expire(self, key: str, seconds: int) -> bool:
        if not self.redis:
            return False
        return await self.redis.expire(key, seconds)

    async def clear_pattern(
            self,
            pattern: str,
    ) -> int:
        if not self.redis:
            return 0

        keys = await self.redis.keys(pattern)
        if keys:
            return await self.redis.delete(*keys)
        return 0