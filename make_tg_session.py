from telethon.sync import TelegramClient

from app.settings import Settings

client = TelegramClient(Settings.TG_SESSION, Settings.API_ID, Settings.API_HASH)
client.start()

client.send_message(Settings.TG_BOT_NAME, 'Make session')
