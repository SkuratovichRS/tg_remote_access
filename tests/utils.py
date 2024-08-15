from typing import Any
from unittest.mock import Mock


async def add_command(session_pool, cmd: str, cmd_id: str, status: str) -> None:
    async with session_pool.acquire() as connection:
        await connection.execute(
            """
            INSERT INTO commands (command_id, command, status)
            VALUES ($1, $2, $3);
            """,
            cmd_id,
            cmd,
            status,
        )


class RabbitMock(Mock):
    def __init__(self, data, **kwargs: Any):
        super().__init__(**kwargs)
        self._data = data

    async def consume(self, *args, **kwargs):
        for item in self._data:
            yield item
