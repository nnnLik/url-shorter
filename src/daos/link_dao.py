from collections.abc import Mapping
from dataclasses import dataclass
from datetime import UTC, datetime

from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from dtos.link_dto import LinkDTO
from models.link import Link
from models.link_stats import LinkStats


@dataclass
class LinkDAO:
    _session: AsyncSession

    async def get_existing_codes(self, codes: list[str]) -> set[str]:
        if not codes:
            return set[str]()

        MAX_BATCH_SIZE = 30000
        existing_codes = set[str]()

        for i in range(0, len(codes), MAX_BATCH_SIZE):
            batch = codes[i : i + MAX_BATCH_SIZE]
            result = await self._session.execute(select(Link.short_code).where(Link.short_code.in_(batch)))
            existing_codes.update(result.scalars().all())

        return existing_codes

    async def get_by_code(self, code: str) -> LinkDTO | None:
        result = await self._session.execute(select(Link).where(Link.short_code == code))
        link = result.scalar_one_or_none()
        if link is None:
            return None

        return LinkDTO.from_model(link)

    async def get_by_code_with_stats(self, code: str) -> Link | None:
        result = await self._session.execute(
            select(Link).options(joinedload(Link.stats)).where(Link.short_code == code)
        )
        return result.scalar_one_or_none()

    async def create_link(
        self,
        short_code: str,
        original_url: str,
        expires_at: datetime | None = None,
    ) -> LinkDTO:
        link = Link(
            short_code=short_code,
            original_url=original_url,
            expires_at=expires_at,
        )
        self._session.add(link)
        await self._session.flush()
        await self._session.refresh(link)
        return LinkDTO.from_model(link)

    async def code_exists(self, code: str) -> bool:
        result = await self._session.execute(select(Link.short_code).where(Link.short_code == code))
        return result.scalar_one_or_none() is not None

    async def batch_update_link_stats(
        self,
        click_counts: Mapping[int, int],
        last_click_times: Mapping[int, datetime],
    ) -> None:
        if not click_counts:
            return

        link_ids = set[int](click_counts.keys()) | set[int](last_click_times.keys())

        for link_id in link_ids:
            click_count_delta = click_counts.get(link_id, 0)
            last_click_at = last_click_times.get(link_id)

            stmt = (
                update(LinkStats)
                .where(LinkStats.link_id == link_id)
                .values(
                    click_count=LinkStats.click_count + click_count_delta,
                    last_click_at=last_click_at,
                )
            )
            await self._session.execute(stmt)

        await self._session.flush()
        if self._session.in_transaction():
            await self._session.commit()

    async def get_total_links_count(self) -> int:
        result = await self._session.execute(select(func.count(Link.id)))
        return result.scalar_one()

    async def get_total_clicks_count(self) -> int:
        result = await self._session.execute(select(func.sum(LinkStats.click_count)))
        return result.scalar_one() or 0

    async def get_active_links_count(self) -> int:
        result = await self._session.execute(
            select(func.count(Link.id)).where((Link.expires_at.is_(None)) | (Link.expires_at > datetime.now(tz=UTC)))
        )
        return result.scalar_one()

    async def get_top_links_by_clicks(self, limit: int = 5) -> list[tuple[Link, LinkStats]]:
        result = await self._session.execute(
            select(Link, LinkStats)
            .join(LinkStats, Link.id == LinkStats.link_id)
            .order_by(LinkStats.click_count.desc())
            .limit(limit)
        )
        return result.all()
