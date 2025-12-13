from typing import Annotated

from fastapi import Depends
from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession

import core.constants
from core.database import db_session
from core.taskiq_broker import broker
from services.generate_batch_of_codes_service import GenerateBatchOfCodesService


@broker.task(
    schedule=[{'cron': '*/5 * * * *'}],
    name=core.constants.REFILL_CODE_POOL__TASK_NAME,
)
async def refill_code_pool_task(
    session: Annotated[
        AsyncSession,
        Depends(db_session.session_getter),
    ],
) -> None:
    service = GenerateBatchOfCodesService.build(session)
    current_size = await service._redis_dao.get_pool_size()

    if current_size >= core.constants.CODE_POOL_REFILL_THRESHOLD:
        logger.debug(f'Pool size {current_size} >= threshold {core.constants.CODE_POOL_REFILL_THRESHOLD}, skipping')
        return

    logger.info(f'Pool size {current_size} < threshold {core.constants.CODE_POOL_REFILL_THRESHOLD}, refilling...')
    await service.execute()
    logger.info('Refill completed')
