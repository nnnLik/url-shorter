from collections import defaultdict
from collections.abc import Mapping
from dataclasses import dataclass
from datetime import datetime
from typing import Self

from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession

import core.constants
from daos import LinkDAO, RabbitMQDAO
from dtos.click_event_dto import ClickEventDTO


@dataclass
class BatchClickProcessorService:
    _rabbitmq_dao: RabbitMQDAO
    _link_dao: LinkDAO

    @classmethod
    def build(cls, session: AsyncSession) -> Self:
        return cls(
            _rabbitmq_dao=RabbitMQDAO(),
            _link_dao=LinkDAO(session),
        )

    async def _consume_click_events(self) -> None:
        events = await self._rabbitmq_dao.consume_click_events(
            batch_size=core.constants.BATCH_CLICK_PROCESSING_BATCH_SIZE,
            timeout=core.constants.BATCH_CLICK_PROCESSING_TIMEOUT_SEC,
        )

        if not events:
            logger.debug('No click events to process')
            return

        logger.info(f'Processing batch of {len(events)} click events')

        # Группируем клики по short_code
        clicks_by_code: dict[str, list[ClickEventDTO]] = defaultdict[str, list[ClickEventDTO]](list)
        for event in events:
            clicks_by_code[event.short_code].append(event)

        # Получаем link_id для каждого short_code
        link_ids_by_code: Mapping[str, int] = {}
        for short_code in clicks_by_code.keys():
            link_dto = await self._link_dao.get_by_code(short_code)
            if link_dto:
                link_ids_by_code[short_code] = link_dto.id
            else:
                logger.warning(f'Link not found for code: {short_code}')

        # Группируем клики по link_id и собираем статистику
        click_counts: Mapping[int, int] = defaultdict[int, int](int)
        last_click_times: Mapping[int, datetime] = {}

        for short_code, clicks in clicks_by_code.items():
            link_id = link_ids_by_code.get(short_code)
            if link_id is None:
                continue

            # Считаем количество кликов для этой ссылки
            click_counts[link_id] += len(clicks)

            # Находим последний клик
            latest_timestamp: datetime | None = None
            for click in clicks:
                if click.timestamp:
                    try:
                        click_time = datetime.fromisoformat(click.timestamp)
                        if latest_timestamp is None or click_time > latest_timestamp:
                            latest_timestamp = click_time
                    except ValueError as e:
                        logger.warning(f'Invalid timestamp format in click event: {click.timestamp}, error: {e}')

            if latest_timestamp:
                # Обновляем только если новый клик позже существующего
                current_last = last_click_times.get(link_id)
                if current_last is None or latest_timestamp > current_last:
                    last_click_times[link_id] = latest_timestamp

        # Батч-обновление LinkStats
        if click_counts:
            await self._link_dao.batch_update_link_stats(
                click_counts=click_counts,
                last_click_times=last_click_times,
            )
            logger.info(f'Updated stats for {len(click_counts)} links: total clicks={sum(click_counts.values())}')

    async def execute(self) -> None:
        await self._consume_click_events()
