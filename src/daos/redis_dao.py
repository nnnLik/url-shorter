from dataclasses import dataclass

from redis.asyncio import Redis

from core.redis import redis_client


@dataclass
class RedisDAO:
    _client: Redis = redis_client.get_client()

    async def get_pool_size(self) -> int:
        return await self._client.scard("pool:codes")

    async def pop_code(self) -> str | None:
        return await self._client.spop("pool:codes")

    async def add_codes(self, codes: list[str]) -> int:
        if not codes:
            return 0
        return await self._client.sadd("pool:codes", *codes)
