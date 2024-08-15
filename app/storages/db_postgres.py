from asyncpg import Pool


class Db:

    def __init__(self, connection_pool: Pool):  # type:ignore
        self._pool = connection_pool

    async def create_tables(self) -> None:
        async with self._pool.acquire() as connection:
            await connection.execute(
                """
                CREATE TABLE IF NOT EXISTS commands
                (
                command_id VARCHAR(128) PRIMARY KEY,
                command VARCHAR(1024) NOT NULL,
                status VARCHAR(32) NOT NULL,
                result VARCHAR(1024)
                );
                """
            )

    async def write_new_command(self, cmd: str, cmd_id: str) -> None:
        async with self._pool.acquire() as connection:
            await connection.execute(
                """
                INSERT INTO commands (command_id, command, status)
                VALUES ($1, $2, $3);
                """,
                cmd_id,
                cmd,
                "new",
            )

    async def get_status_and_result(self, cmd_id: str) -> tuple[str, str | None]:
        async with self._pool.acquire() as connection:
            raw = await connection.fetchrow(
                """
                SELECT status, result FROM commands WHERE command_id = $1;
                """,
                cmd_id,
            )
        if not raw:
            raise ValueError("command with such id does not exists")
        return raw[0], raw[1]

    async def add_result(self, cmd_id: str, result: str) -> None:
        async with self._pool.acquire() as connection:
            await connection.execute(
                """
                UPDATE commands SET result = $1, status = $2 WHERE command_id = $3;
                """,
                result,
                "executed",
                cmd_id,
            )
