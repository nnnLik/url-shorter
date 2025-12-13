import asyncio
from dataclasses import dataclass

import aio_pika
import msgspec
from loguru import logger

import core.constants
from core.rabbitmq import rabbitmq_client
from dtos.click_event_dto import ClickEventDTO


@dataclass
class RabbitMQDAO:
    async def publish_click_event(
        self,
        short_code: str,
        timestamp: str,
        ip_address: str | None,
        user_agent: str | None,
    ) -> None:
        channel = rabbitmq_client.get_channel()

        click_event = ClickEventDTO(
            short_code=short_code,
            timestamp=timestamp,
            ip_address=ip_address,
            user_agent=user_agent,
        )

        message = aio_pika.Message(
            body=msgspec.json.encode(click_event),
            delivery_mode=aio_pika.DeliveryMode.PERSISTENT,
        )

        await channel.default_exchange.publish(
            message,
            routing_key=core.constants.DURABLE_CLICK_EVENTS_QUEUE_NAME,
        )
        logger.debug(f"Click event published to {core.constants.DURABLE_CLICK_EVENTS_QUEUE_NAME} for {short_code}")

    async def consume_click_events(
        self,
        batch_size: int,
        timeout: float = 1.0,
    ) -> list[ClickEventDTO]:
        queue = rabbitmq_client.get_queue()

        events: list[ClickEventDTO] = []
        consumed_count = 0

        try:
            async with queue.iterator(timeout=timeout) as queue_iter:
                async for message in queue_iter:
                    async with message.process():
                        try:
                            click_event = msgspec.json.decode(
                                message.body,
                                type=ClickEventDTO,
                            )
                            events.append(click_event)
                            consumed_count += 1

                            if consumed_count >= batch_size:
                                break
                        except msgspec.DecodeError as e:
                            logger.error(f"Invalid click event message format: {e}")
                            continue
                        except Exception as e:
                            logger.error(f"Error processing click event message: {e}")
                            continue
        except asyncio.TimeoutError:
            logger.debug("No messages in queue (timeout)")
        except Exception as e:
            logger.error(f"Error consuming click events: {e}")
            raise

        return events
