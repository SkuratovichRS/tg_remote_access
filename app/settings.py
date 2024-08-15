import os


def get_env(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise ValueError(f"Environment variable {name} not found")
    return value


class Settings:
    API_ID = get_env("API_ID")
    API_HASH = get_env("API_HASH")
    API_HOST = get_env("API_HOST")
    TG_SESSION = get_env("TG_SESSION")
    TG_BOT_NAME = get_env("TG_BOT_NAME")
    REDIS_HOST = get_env("REDIS_HOST")
    REDIS_PORT = get_env("REDIS_PORT")
    RABBIT_HOST = get_env("RABBIT_HOST")
    RABBIT_PORT = get_env("RABBIT_PORT")
    DB_NAME = get_env("DB_NAME")
    DB_USER = get_env("DB_USER")
    DB_PASSWORD = get_env("DB_PASSWORD")
    DB_HOST = get_env("DB_HOST")
    DB_PORT = get_env("DB_PORT")
