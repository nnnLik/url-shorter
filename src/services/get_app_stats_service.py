from typing import Self
from dataclasses import dataclass

from sqlalchemy.ext.asyncio import AsyncSession

from config import settings
from daos import LinkDAO
from dtos.link_stats_dto import AppStatsResponseDTO, TopLinkDTO


@dataclass
class GetAppStatsService:
    _link_dao: LinkDAO

    SHORT_URL_TEMPLATE: str = f"{settings.app.BASE_URL}/{{code}}"

    @classmethod
    def build(cls, session: AsyncSession) -> Self:
        return cls(
            _link_dao=LinkDAO(session),
        )

    async def execute(self) -> AppStatsResponseDTO:
        total_links = await self._link_dao.get_total_links_count()
        total_clicks = await self._link_dao.get_total_clicks_count()
        active_links = await self._link_dao.get_active_links_count()
        top_links_data = await self._link_dao.get_top_links_by_clicks(limit=5)

        top_links = [
            TopLinkDTO(
                original_url=link.original_url,
                short_url=self.SHORT_URL_TEMPLATE.format(code=link.short_code),
                click_count=link_stats.click_count,
            )
            for link, link_stats in top_links_data
        ]

        return AppStatsResponseDTO(
            total_links=total_links,
            total_clicks=total_clicks,
            active_links=active_links,
            top_links=top_links,
        )
