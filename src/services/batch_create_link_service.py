from dataclasses import dataclass
from datetime import datetime
from typing import Self

from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession

from dtos import BatchCreateLinkResponseDTO

from .create_link_service import CreateLinkService


@dataclass
class BatchCreateLinkService:
    _create_link_service: CreateLinkService

    class BatchCreateLinkServiceError(Exception):
        pass

    class InvalidCountError(BatchCreateLinkServiceError):
        pass

    @classmethod
    def build(cls, session: AsyncSession) -> Self:
        return cls(
            _create_link_service=CreateLinkService.build(session),
        )

    def _validate_count(self, count: int) -> None:
        if count < 1 or count > 50:
            raise self.InvalidCountError('Count must be between 1 and 50')

    async def execute(
        self,
        original_url: str,
        count: int,
        expires_at: datetime | None = None,
    ) -> BatchCreateLinkResponseDTO:
        self._validate_count(count)

        links = []
        for _ in range(count):
            link = await self._create_link_service.execute(
                original_url=original_url,
                expires_at=expires_at,
            )
            links.append(link)

        logger.info(f'Batch created {count} links for {original_url}')

        return BatchCreateLinkResponseDTO(links=links)
