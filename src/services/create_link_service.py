from dataclasses import dataclass
from datetime import datetime
from typing import Self
from urllib.parse import urlparse

from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession

import core.constants
from config import settings
from daos import LinkDAO, RedisDAO
from dtos import CreateLinkResponseDTO
from services import CodeGeneratorService
from utils.taskiq_utils import exec_task_by_name


@dataclass
class CreateLinkService:
    _redis_dao: RedisDAO
    _link_dao: LinkDAO
    _code_generator: CodeGeneratorService
    _session: AsyncSession

    SHORT_URL_TEMPLATE: str = f"{settings.app.BASE_URL}/{{code}}"

    class CreateLinkServiceError(Exception):
        pass

    class InvalidURLFormatError(CreateLinkServiceError):
        pass

    class InvalidCustomCodeError(CreateLinkServiceError):
        pass

    class PoolIsEmptyError(CreateLinkServiceError):
        pass

    @classmethod
    def build(cls, session: AsyncSession) -> Self:
        return cls(
            _redis_dao=RedisDAO(),
            _link_dao=LinkDAO(session),
            _code_generator=CodeGeneratorService.build(),
            _session=session,
        )

    def _validate_url(self, url: str) -> None:
        result = urlparse(url)
        if not all([result.scheme, result.netloc]):
            raise self.InvalidURLFormatError("Invalid URL format")
        if result.scheme not in ["http", "https"]:
            raise self.InvalidURLFormatError("URL must use http or https protocol")

    def _validate_custom_code(self, code: str) -> None:
        if not (6 <= len(code) <= 20):
            raise self.InvalidCustomCodeError("Custom code must be 6-20 characters")
        if not code.isalnum():
            raise self.InvalidCustomCodeError("Custom code must contain only alphanumeric characters")

    async def _get_code_from_pool(self) -> str:
        code = await self._redis_dao.pop_code()

        if code is not None:
            return code

        # Триггерим экстренное пополнение
        await exec_task_by_name(core.constants.REFILL_CODE_POOL__TASK_NAME)

        # Пул пуст - генерируем синхронно
        logger.warning("Pool is empty, generating code synchronously")
        code = self._code_generator.execute(1)[0]

        # Проверяем коллизию
        existing = await self._link_dao.get_by_code(code)
        if existing:
            # Коллизия - генерируем еще раз
            return await self._get_code_from_pool()

        return code

    async def execute(self, original_url: str, expires_at: datetime | None = None) -> CreateLinkResponseDTO:
        self._validate_url(original_url)

        short_code = await self._get_code_from_pool()

        # Создаем ссылку в БД
        link_dto = await self._link_dao.create_link(
            short_code=short_code,
            original_url=original_url,
            expires_at=expires_at,
        )

        # Кешируем в Redis (TTL 24h)
        await self._redis_dao._client.setex(
            f"cache:link:{short_code}",
            core.constants.CACHE_LINK_TTL_SEC,
            original_url,
        )

        logger.info(f"Link created: {short_code} -> {original_url}")

        return CreateLinkResponseDTO(
            short_code=link_dto.short_code,
            short_url=self.SHORT_URL_TEMPLATE.format(code=link_dto.short_code),
            created_at=link_dto.created_at,
            expires_at=link_dto.expires_at,
        )
