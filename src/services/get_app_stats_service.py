from typing import Self
from dataclasses import dataclass

from sqlalchemy.ext.asyncio import AsyncSession

from daos import LinkDAO
from dtos.link_stats_dto import AppStatsResponseDTO


@dataclass
class GetAppStatsService:
    _link_dao: LinkDAO

    @classmethod
    def build(cls, session: AsyncSession) -> Self:
        return cls(
            _link_dao=LinkDAO(session),
        )

    async def execute(self) -> AppStatsResponseDTO:
        stats = await self._link_dao.get_app_statistics()
        return AppStatsResponseDTO(
            total_links=stats["total_links"],
            total_clicks=stats["total_clicks"],
            active_links=stats["active_links"],
        )
