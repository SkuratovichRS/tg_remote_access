from app.storages.db_postgres import Db


class CommandsService:
    def __init__(self, db: Db):
        self._db = db

    async def store_result(self, cmd_id: str, result: str) -> None:
        await self._db.add_result(cmd_id, result)
