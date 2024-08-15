import asyncio

from app.factory import Factory
from app.settings import Settings


async def main():
    factory = Factory(Settings)
    await factory.run_tg_consumers()


if __name__ == '__main__':
    asyncio.run(main())
