from datetime import datetime

from loguru import logger

import core.constants
from core.taskiq_broker import broker
from daos import RabbitMQDAO, RedisDAO


@broker.task(
    queue_name=core.constants.PROCESS_CLICK_TASK__QUEUE_NAME,
    name=core.constants.PROCESS_CLICK__TASK_NAME,
)
async def process_click_task(
    short_code: str,
    timestamp: datetime,
    original_url: str,
    ip_address: str | None = None,
    user_agent: str | None = None,
) -> None:
    rabbitmq_dao = RabbitMQDAO()
    redis_dao = RedisDAO()

    # 1. Кеширование в Redis (TTL 24h)
    await redis_dao._client.setex(
        f"cache:link:{short_code}",
        core.constants.CACHE_LINK_TTL_SEC,
        original_url,
    )
    logger.debug(f"Cached link {short_code} in Redis")

    # 2. Отправка клика в RabbitMQ очередь для батч-обработки
    try:
        await rabbitmq_dao.publish_click_event(
            short_code=short_code,
            timestamp=timestamp.isoformat(),
            ip_address=ip_address,
            user_agent=user_agent,
        )
    except Exception as e:
        logger.error(f"Failed to publish click event to RabbitMQ for {short_code}: {e}")
