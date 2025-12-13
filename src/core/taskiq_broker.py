import taskiq_fastapi
from loguru import logger
from taskiq import TaskiqEvents, TaskiqScheduler, TaskiqState
from taskiq.schedule_sources import LabelScheduleSource
from taskiq_aio_pika import AioPikaBroker

from config import init_logging, settings
from core.rabbitmq import rabbitmq_client

broker = AioPikaBroker(
    url=settings.taskiq.BROKER_URL,
)

taskiq_fastapi.init(broker, 'main:app')
scheduler = TaskiqScheduler(
    broker=broker,
    sources=[LabelScheduleSource(broker)],
)


@broker.on_event(TaskiqEvents.WORKER_STARTUP)
async def on_worker_startup(state: TaskiqState) -> None:
    init_logging()
    await rabbitmq_client.initialize()
    logger.info('Worker startup complete, got state: %s', state)


# Импортируем задачи для регистрации
from tasks import *  # noqa: E402 F403
