import pytest

from app.storages.chunks_storage import ChunksStorage


@pytest.mark.parametrize(
    "redis_data, keys, expected",
    [
        (
            {"key1": "v1", "key2": "v2", "key3": "v3", "key4": "v4"},
            ["key1", "key4"],
            {b"key2": b"v2", b"key3": b"v3"},
        ),
        (
            {},
            ["key1", "key4"],
            {},
        ),
    ],
)
def test_chunks_storage(redis_client, redis_data, keys, expected):
    for key, value in redis_data.items():
        redis_client.set(key, value)
    chunks_storage = ChunksStorage(redis_client)

    chunks_storage.del_keys(keys)

    result = {key: redis_client.get(key) for key in redis_client.keys()}
    assert result == expected
