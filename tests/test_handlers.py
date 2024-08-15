from unittest.mock import AsyncMock, call

import pytest

from app.handlers.handlers import RabbitDbConsumer
from tests.utils import RabbitMock


@pytest.mark.asyncio
async def test_rabbit_db_consumer():
    rabbit = RabbitMock(
        [
            {"cmd_id": "cmd_id1", "result": "data1"},
            {"err": "err"},
            "hello",
            {"cmd_id": "cmd_id2", "result": "data2"},
        ]
    )

    commands_service = AsyncMock()
    consumer = RabbitDbConsumer(rabbit, "q", commands_service)
    await consumer.run()

    assert commands_service.store_result.await_args_list == [
        call("cmd_id1", "data1"),
        call("cmd_id2", "data2"),
    ]
