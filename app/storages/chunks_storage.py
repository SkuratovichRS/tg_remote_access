import json
from collections import defaultdict

from redis import Redis

from app.types import ChunkModel


class ChunksStorage:
    def __init__(self, redis_client: Redis):
        self._redis_client = redis_client

    def add_chunk(self, message: str) -> None:
        message_json = json.loads(message)
        key = f"chunk:{message_json.get('cmd_id')}:{message_json.get('index')}"
        value = message
        if not self._redis_client.get(key):
            self._redis_client.set(key, value)

    def get_chunks(self) -> dict[str, list[ChunkModel]]:
        keys = self._redis_client.keys("chunk:*")
        if not keys:
            return {}
        data = defaultdict(list)
        for key in keys:  # type:ignore
            value = json.loads(self._redis_client.get(key).decode("utf-8"))  # type:ignore
            cmd_id = value.get("cmd_id")
            data[cmd_id].append(ChunkModel(key=key, len=value["len"], index=value["index"], chunk=value["chunk"]))
        return data

    def del_keys(self, keys: list[bytes]) -> None:
        self._redis_client.delete(*keys)
