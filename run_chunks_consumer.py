import asyncio

from app.factory import Factory
from app.settings import Settings


async def main():
    factory = Factory(Settings)
    print("created factory")
    await factory.run_chunks_consumer()


if __name__ == '__main__':
    asyncio.run(main())
