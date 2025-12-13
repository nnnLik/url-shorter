from dataclasses import dataclass, field

from loguru import logger
from redis.asyncio import Redis
from redis.asyncio.connection import ConnectionPool

from config import settings


@dataclass
class RedisClient:
    _pool: ConnectionPool = field(init=False)
    _client: Redis = field(init=False)

    def __post_init__(self) -> None:
        self._pool = ConnectionPool.from_url(
            url=settings.redis.URL,
            max_connections=settings.redis.MAX_CONNECTIONS,
            socket_connect_timeout=settings.redis.SOCKET_CONNECT_TIMEOUT,
            socket_timeout=settings.redis.SOCKET_TIMEOUT,
            decode_responses=settings.redis.DECODE_RESPONSES,
        )
        self._client = Redis(connection_pool=self._pool)
        logger.info('Redis client initialized')

    async def close(self) -> None:
        await self._client.aclose()
        await self._pool.aclose()
        logger.info('Redis client closed')

    def get_client(self) -> Redis:
        return self._client


redis_client: RedisClient = RedisClient()
