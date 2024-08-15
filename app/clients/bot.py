import logging

from telethon.sync import TelegramClient  # type:ignore

logger = logging.getLogger(__name__)


class Bot:

    def __init__(self, target: str, client: TelegramClient):
        self._target = target
        self.client = client
        self._last_message_id = None

    async def send_new_command(self, message: str) -> None:
        await self.client.send_message(self._target, message)

    async def read_commands(self) -> list[str]:
        messages = await self.client.get_messages(self._target)
        if not self._last_message_id:
            self._last_message_id = max([m.id for m in messages])
        messages = await self.client.get_messages(
            self._target, min_id=self._last_message_id, from_user=self._target, limit=10
        )
        if not messages:
            return []
        logging.info("found messages")
        answers = []
        for m in messages:
            answers.append(m.message)
        self._last_message_id = max([m.id for m in messages])
        logging.info("answers: %s", answers)
        return answers
