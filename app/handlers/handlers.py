import asyncio
import json
import logging
from abc import ABC, abstractmethod

from app.clients.bot import Bot
from app.services.commands import CommandsService
from app.storages.chunks_storage import ChunksStorage
from app.storages.rabbitmq import Rabbit

logger = logging.getLogger(__name__)


class BaseConsumer(ABC):
    @abstractmethod
    async def run(self) -> None:
        pass


class BaseRabbitConsumer(BaseConsumer):
    def __init__(self, rabbit: Rabbit, queue_name: str):
        self._rabbit = rabbit
        self._queue_name = queue_name

    async def run(self) -> None:
        logger.info("start consuming %s", self._queue_name)
        async for message in self._rabbit.consume(self._queue_name):
            logger.info("processing message %s", message)
            try:
                await self._run(message)
            except Exception as e:  # pylint:disable=broad-exception-caught
                logger.exception("unexpected exception occurred: %s ", e)

    @abstractmethod
    async def _run(self, message: dict[str, str]) -> None:
        pass


class RabbitDbConsumer(BaseRabbitConsumer):
    def __init__(self, rabbit: Rabbit, queue_name: str, commands_service: CommandsService):
        super().__init__(rabbit, queue_name)
        self._commands_service = commands_service

    async def _run(self, message: dict[str, str]) -> None:
        await self._commands_service.store_result(message["cmd_id"], message["result"])


class RabbitTgConsumer(BaseRabbitConsumer):
    def __init__(self, rabbit: Rabbit, queue_name: str, bot: Bot):
        super().__init__(rabbit, queue_name)
        self._bot = bot

    async def _run(self, message: dict[str, str]) -> None:
        await self._bot.send_new_command(json.dumps(message))


class RedisTgConsumer(BaseConsumer):
    def __init__(self, redis_app: ChunksStorage, bot: Bot):
        self._redis_app = redis_app
        self._bot = bot

    async def run(self) -> None:
        while True:
            answers = await self._bot.read_commands()
            for answer in answers:
                self._redis_app.add_chunk(answer)
            await asyncio.sleep(1)


class ChunksConsumer(BaseConsumer):
    def __init__(self, redis: ChunksStorage, rabbit: Rabbit):
        self._redis = redis
        self._rabbit = rabbit

    async def run(self) -> None:
        logger.info("start consuming")
        while True:
            data = self._redis.get_chunks()
            if not data:
                continue
            for key, value in data.items():
                if len(value) == value[0].len:
                    value = sorted(value, key=lambda x: x.index)
                    final_result = ""
                    for item in value:
                        final_result += item.chunk
                    to_rabbit = json.dumps({"cmd_id": key, "result": final_result})
                    print(f"{to_rabbit=}")
                    await self._rabbit.producer_result(to_rabbit)
                    keys_to_delete = [item.key for item in value]
                    self._redis.del_keys(keys_to_delete)
