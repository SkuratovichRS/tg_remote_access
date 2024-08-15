from dataclasses import dataclass


@dataclass
class ChunkModel:
    key: bytes
    len: int
    index: int
    chunk: str
