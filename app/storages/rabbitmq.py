import asyncio
import json
import logging
from typing import AsyncGenerator

import aio_pika
from aio_pika.channel import AbstractChannel  # type:ignore

from app.constants import QueueNames

logger = logging.getLogger(__name__)


class Rabbit:
    def __init__(self, channel: AbstractChannel):
        self._channel = channel

    async def producer_cmd(self, command: str, command_id: str) -> None:
        data = {"cmd": command, "cmd_id": command_id}
        serialized_data = json.dumps(data)
        await self._channel.default_exchange.publish(
            aio_pika.Message(body=serialized_data.encode()), routing_key=QueueNames.COMMANDS
        )
        logger.info("produced: %s", serialized_data)

    async def producer_result(self, result: str) -> None:
        await self._channel.default_exchange.publish(
            aio_pika.Message(body=result.encode()), routing_key=QueueNames.RESULTS
        )
        logger.info("produced: %s", result)

    async def consume(self, queue_name: str) -> AsyncGenerator[dict[str, str], None]:
        exchange = await self._channel.declare_exchange("direct", auto_delete=False)
        queue = await self._channel.declare_queue(queue_name, auto_delete=False)
        await queue.bind(exchange, queue_name)
        while True:
            try:
                message = await queue.get(timeout=1)
                await message.ack()
                message_body = message.body
                logger.info("message get: %s", message_body)
                yield json.loads(message_body)
            except aio_pika.exceptions.QueueEmpty:
                await asyncio.sleep(1)


if __name__ == "__main__":
    pass
