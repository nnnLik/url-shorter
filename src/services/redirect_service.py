from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Self

from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession

import core.constants
from daos import LinkDAO, RedisDAO
from utils.taskiq_utils import exec_task_by_name


@dataclass
class RedirectService:
    _redis_dao: RedisDAO
    _link_dao: LinkDAO


    class LinkNotFoundError(Exception):
        pass

    @classmethod
    def build(cls, session: AsyncSession) -> Self:
        return cls(
            _redis_dao=RedisDAO(),
            _link_dao=LinkDAO(session),
        )

    async def execute(
        self,
        short_code: str,
        ip_address: str | None,
        user_agent: str | None,
    ) -> str:
        now = datetime.now(tz=UTC)

        # 1. Проверяем Redis кеш
        cached_url = await self._redis_dao._client.get(f'cache:link:{short_code}')
        if cached_url:
            logger.debug(f'Cache hit for {short_code}')
            # Отправляем задачу постобработки даже для кеша (для статистики)
            await exec_task_by_name(
                task_name=core.constants.PROCESS_CLICK__TASK_NAME,
                short_code=short_code,
                timestamp=now,
                ip_address=ip_address,
                user_agent=user_agent,
                original_url=cached_url,
            )
            return cached_url

        # 2. Проверяем БД
        link_dto = await self._link_dao.get_by_code(short_code)
        if link_dto is None:
            logger.debug(f'Link not found: {short_code}')
            raise self.LinkNotFoundError('Link not found')

        # 3. Проверяем срок действия
        if link_dto.expires_at and link_dto.expires_at < now:
            logger.info(f'Link expired: {short_code}')
            raise self.LinkNotFoundError('Link expired')

        # 4. Сразу возвращаем URL (не ждем кеширования)
        # Кеширование и запись клика выполнятся асинхронно в задаче постобработки
        await exec_task_by_name(
            task_name=core.constants.PROCESS_CLICK__TASK_NAME,
            short_code=short_code,
            timestamp=now,
            ip_address=ip_address,
            user_agent=user_agent,
            original_url=link_dto.original_url,
        )

        return link_dto.original_url
