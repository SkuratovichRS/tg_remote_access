import asyncio

from app.factory import Factory
from app.settings import Settings


async def main():
    factory = Factory(Settings)
    await factory.run_rabbit_db_consumer()

if __name__ == '__main__':
    asyncio.run(main())
