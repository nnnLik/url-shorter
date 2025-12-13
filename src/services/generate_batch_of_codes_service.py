from dataclasses import dataclass
from typing import Self

from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession

import core.constants
from daos import LinkDAO, RedisDAO
from services.code_generator_service import CodeGeneratorService


@dataclass
class GenerateBatchOfCodesService:
    _redis_dao: RedisDAO
    _link_dao: LinkDAO
    _code_generator: CodeGeneratorService

    @classmethod
    def build(cls, session: AsyncSession) -> Self:
        return cls(
            _redis_dao=RedisDAO(),
            _link_dao=LinkDAO(session),
            _code_generator=CodeGeneratorService.build(),
        )

    async def execute(self, count: int | None = None) -> None:
        # Определяем сколько нужно сгенерировать
        current_size = await self._redis_dao.get_pool_size()
        if count is None:
            count = max(0, core.constants.CODE_POOL_MAX_SIZE - current_size)

        if count <= 0:
            logger.info('Pool is full, no generation needed')
            return

        # Генерируем запасом на коллизии (10% запас)
        codes_to_generate = count + (count // 10)
        all_codes = set[str]()

        # Генерируем батчами
        batch_size = core.constants.CODE_POOL_BATCH_SIZE
        while len(all_codes) < codes_to_generate:
            batch = self._code_generator.execute(batch_size)
            all_codes.update(batch)
            if len(all_codes) >= codes_to_generate:
                break

        # Проверяем коллизии в БД
        codes_list = list[str](all_codes)
        existing_codes = await self._link_dao.get_existing_codes(codes_list)
        unique_codes = [c for c in codes_list if c not in existing_codes]

        # Берем только нужное количество
        codes_to_add = unique_codes[:count]
        collisions = len(existing_codes)

        # Добавляем в Redis
        added = await self._redis_dao.add_codes(codes_to_add)
        pool_size_after = await self._redis_dao.get_pool_size()

        logger.info(
            f'Generated batch: requested={count}, '
            f'generated={len(codes_list)}, '
            f'collisions={collisions}, '
            f'added={added}, '
            f'pool_size={pool_size_after}'
        )
