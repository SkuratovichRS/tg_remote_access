import asyncio
import logging
from typing import Type

import asyncpg
import redis
import uvicorn
from aio_pika import connect_robust
from fastapi import FastAPI
from telethon.sync import TelegramClient  # type:ignore

from app.api.api import router
from app.clients.api_client import ApiClient
from app.clients.bot import Bot
from app.constants import QueueNames
from app.handlers.handlers import ChunksConsumer, RabbitDbConsumer, RabbitTgConsumer, RedisTgConsumer
from app.services.commands import CommandsService
from app.settings import Settings
from app.storages.chunks_storage import ChunksStorage
from app.storages.db_postgres import Db
from app.storages.rabbitmq import Rabbit

logger = logging.getLogger(__name__)


class Factory:
    def __init__(self, settings: Type[Settings]):
        self._settings = settings
        logging.basicConfig(
            level=logging.INFO, format="%(asctime)s; %(filename)s; %(funcName)s; %(lineno)d; %(message)s"
        )
        logger.info("logger configured")

    def run_api(self) -> None:
        app = self._create_app()

        uvicorn.run(app, host="0.0.0.0", port=8000)

    async def run_tg_consumers(self) -> None:
        bot = self._create_bot()
        await bot.client.start()
        rabbit_tg_consumer = RabbitTgConsumer(await self._create_rabbit(), QueueNames.COMMANDS, bot)
        redis_tg_consumer = RedisTgConsumer(self._create_chunks_storage(), bot)
        task1 = asyncio.create_task(rabbit_tg_consumer.run())
        task2 = asyncio.create_task(redis_tg_consumer.run())
        await asyncio.gather(task1, task2)

    async def run_chunks_consumer(self) -> None:
        chunks_consumer = ChunksConsumer(self._create_chunks_storage(), await self._create_rabbit())
        await chunks_consumer.run()

    async def run_rabbit_db_consumer(self) -> None:
        db = await self._create_db()
        consumer = RabbitDbConsumer(await self._create_rabbit(), QueueNames.RESULTS, self._create_commands_service(db))
        await consumer.run()

    def run_api_client(self) -> None:
        api_client = self._create_api_client()
        while True:
            command = input("Write command ")
            result = api_client.execute(command)
            print(
                result.get("result").get("stdout"),
                result.get("result").get("stderr"),
                result.get("result").get("returncode"),
            )

    def _create_app(self) -> FastAPI:
        app = FastAPI()
        app.include_router(router)

        @app.on_event("startup")
        async def _startup() -> None:
            db = await self._create_db()
            rabbit = await self._create_rabbit()
            app.state.db = db
            app.state.rabbit = rabbit
            await db.create_tables()

        return app

    async def _create_rabbit(self) -> Rabbit:
        connection = await connect_robust(host=self._settings.RABBIT_HOST)
        channel = await connection.channel()
        return Rabbit(channel)

    async def _create_db(self) -> Db:
        print(self._settings.DB_HOST)
        connection_pool = await asyncpg.create_pool(
            database=self._settings.DB_NAME,
            user=self._settings.DB_USER,
            password=self._settings.DB_PASSWORD,
            host=self._settings.DB_HOST,
            port=self._settings.DB_PORT,
        )
        return Db(connection_pool)  # type:ignore

    def _create_commands_service(self, db: Db) -> CommandsService:
        return CommandsService(db)

    def _create_bot(self) -> Bot:
        return Bot(
            target=Settings.TG_BOT_NAME,
            client=TelegramClient(self._settings.TG_SESSION, self._settings.API_ID, self._settings.API_HASH),
        )

    def _create_chunks_storage(self) -> ChunksStorage:
        return ChunksStorage(redis.Redis(host=self._settings.REDIS_HOST, port=int(self._settings.REDIS_PORT)))

    def _create_api_client(self) -> ApiClient:
        return ApiClient(self._settings.API_HOST)
