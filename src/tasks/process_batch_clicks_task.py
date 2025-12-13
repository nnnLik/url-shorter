from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

import core.constants
from core.database import db_session
from core.taskiq_broker import broker
from services.batch_click_processor_service import BatchClickProcessorService


@broker.task(
    schedule=[{"cron": f"*/{core.constants.BATCH_CLICK_PROCESSING_INTERVAL_MIN} * * * *"}],
    name=core.constants.PROCESS_BATCH_CLICKS__TASK_NAME,
)
async def process_batch_clicks_task(
    session: Annotated[
        AsyncSession,
        Depends(db_session.session_getter),
    ],
) -> None:
    service = BatchClickProcessorService.build(session)
    await service.execute()

