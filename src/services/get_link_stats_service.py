from typing import Self
from dataclasses import dataclass

from sqlalchemy.ext.asyncio import AsyncSession

from daos import LinkDAO
from dtos.link_stats_dto import LinkStatsResponseDTO


@dataclass
class GetLinkStatsService:
    _link_dao: LinkDAO

    @classmethod
    def build(cls, session: AsyncSession) -> Self:
        return cls(
            _link_dao=LinkDAO(session),
        )

    async def execute(self, short_code: str) -> LinkStatsResponseDTO:
        link = await self._link_dao.get_by_code_with_stats(short_code)
        if link is None or link.stats is None:
            raise ValueError("Link not found")

        return LinkStatsResponseDTO(
            short_code=link.short_code,
            original_url=link.original_url,
            click_count=link.stats.click_count,
            last_click_at=link.stats.last_click_at,
        )
