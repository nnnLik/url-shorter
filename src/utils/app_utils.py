from collections.abc import Generator
from contextlib import asynccontextmanager
from typing import Any

from fastapi import FastAPI

from api import router as api_router
from config import settings
from config.logging import init_logging
from core.database import db_session
from core.rabbitmq import rabbitmq_client
from core.redis import redis_client
from core.taskiq_broker import broker
from utils.fastapi_utils import MsgSpecJSONResponse


def get_app() -> FastAPI:
    @asynccontextmanager
    async def lifespan(_: FastAPI) -> Generator[None, Any]:
        if not broker.is_worker_process and not broker.is_scheduler_process:
            await broker.startup()
            await rabbitmq_client.initialize()
        yield
        if not broker.is_worker_process and not broker.is_scheduler_process:
            await broker.shutdown()
        await db_session.dispose()
        await redis_client.close()
        await rabbitmq_client.close()

    return FastAPI(
        title=settings.app.TITLE,
        description=settings.app.DESCRIPTION,
        version=settings.app.VERSION,
        lifespan=lifespan,
        default_response_class=MsgSpecJSONResponse,
    )


def setup_app(app: FastAPI) -> FastAPI:
    init_logging()
    app.include_router(api_router)
    return app


def get_and_setup_app() -> FastAPI:
    app = get_app()
    setup_app(app)
    return app
