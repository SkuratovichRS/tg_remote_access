import pytest

from app.storages.db_postgres import Db
from tests.utils import add_command


@pytest.mark.asyncio
async def test_db_create_tables_does_not_fail_if_tables_exist(session_pool):
    db = Db(session_pool)
    assert await db.create_tables() is None


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "command, command_id",
    [
        ("ls", "id_1"),
        ("ls -la | grep hello", "id_1"),
    ],
)
async def test_db_write_new_command(session_pool, command, command_id):
    await add_command(session_pool, "cmd1", "cmd_id1", "new")
    await add_command(session_pool, "cmd2", "cmd_id2", "error")
    expected = [
        {"cmd": "cmd1", "cmd_id": "cmd_id1", "status": "new"},
        {"cmd": "cmd2", "cmd_id": "cmd_id2", "status": "error"},
        {"cmd": command, "cmd_id": command_id, "status": "new"},
    ]
    db = Db(session_pool)
    await db.write_new_command(command, command_id)

    async with session_pool.acquire() as session:
        rows = await session.fetch("SELECT * FROM commands")
        result = [{"cmd": item["command"], "cmd_id": item["command_id"], "status": item["status"]} for item in rows]
        assert sorted(result, key=lambda x: x["cmd_id"]) == sorted(expected, key=lambda x: x["cmd_id"])
