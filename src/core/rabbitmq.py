from dataclasses import dataclass, field

import aio_pika
from aio_pika.abc import AbstractChannel, AbstractConnection, AbstractQueue
from loguru import logger

import core.constants
from config import settings


@dataclass
class RabbitMQClient:
    _connection: AbstractConnection | None = field(default=None, init=False)
    _channel: AbstractChannel | None = field(default=None, init=False)
    _queue: AbstractQueue | None = field(default=None, init=False)

    async def initialize(self) -> None:
        if self._connection is None or self._connection.is_closed:
            self._connection = await aio_pika.connect_robust(settings.taskiq.BROKER_URL)
            logger.info("Connected to RabbitMQ")

        if self._channel is None or self._channel.is_closed:
            self._channel = await self._connection.channel()
            logger.info("RabbitMQ channel created")

        if self._queue is None:
            self._queue = await self._channel.declare_queue(
                core.constants.DURABLE_CLICK_EVENTS_QUEUE_NAME,
                durable=True,
            )
            logger.info(f"RabbitMQ queue '{core.constants.DURABLE_CLICK_EVENTS_QUEUE_NAME}' declared")

    async def close(self) -> None:
        if self._channel and not self._channel.is_closed:
            await self._channel.close()
        if self._connection and not self._connection.is_closed:
            await self._connection.close()
        logger.info("RabbitMQ connection closed")

    def get_connection(self) -> AbstractConnection:
        if self._connection is None:
            raise RuntimeError("RabbitMQ not initialized. Call initialize() first.")
        return self._connection

    def get_channel(self) -> AbstractChannel:
        if self._channel is None:
            raise RuntimeError("RabbitMQ not initialized. Call initialize() first.")
        return self._channel

    def get_queue(self) -> AbstractQueue:
        if self._queue is None:
            raise RuntimeError("RabbitMQ not initialized. Call initialize() first.")
        return self._queue


rabbitmq_client: RabbitMQClient = RabbitMQClient()
