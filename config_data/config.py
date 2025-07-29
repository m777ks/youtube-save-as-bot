from dataclasses import dataclass
from environs import Env


@dataclass
class TgBot:
    token: str
    admin_ids: list[int]

    channel_id_1: int
    channel_id_2: int
    # Имя бота для формирования ссылок
    bot_username: str


@dataclass
class Postgres:
    host: str
    port: int
    user: str
    password: str
    database: str

@dataclass
class Redis:
    host: str
    port: int
    password: str

@dataclass
class S3:
    key_id: str
    key_secret: str
    url: str
    name: str


@dataclass
class ConfigEnv:
    tg_bot: TgBot
    postgres: Postgres
    redis: Redis
    s3: S3

def load_config(path: str | None = None) -> ConfigEnv:
    env = Env()
    env.read_env(path)
    return ConfigEnv(
        tg_bot=TgBot(
            token=env('BOT_TOKEN'),
            admin_ids=list(map(int, env.list('ADMIN_IDS'))),
            channel_id_1=int(env('CHANNEL_ID_1')),
            channel_id_2=int(env('CHANNEL_ID_2')),
            bot_username=env('BOT_USERNAME'),
        ),  
        postgres=Postgres(
            host=env('POSTGRES_HOST'),
            port=env('POSTGRES_PORT'),
            user=env('POSTGRES_USER'),
            password=env('POSTGRES_PASSWORD'),
            database=env('POSTGRES_DB'),
        ),
        redis=Redis(
            host=env('REDIS_HOST'),
            port=env('REDIS_PORT'),
            password=env('REDIS_PASSWORD'),
        ),
        s3=S3(
            key_id=env('S3_ACCESS_KEY_ID'),
            key_secret=env('S3_ACCESS_KEY_SECRET'),
            url=env('S3_ENDPOINT_URL'),
            name=env('S3_BUCKET_NAME')
        ),  
    )

config: ConfigEnv = load_config()


def DATABASE_URL_asyncpg():
    """
    Формирует URL подключения для asyncpg
    """
    return f'postgresql+asyncpg://{config.postgres.user}:{config.postgres.password}@{config.postgres.host}:{config.postgres.port}/{config.postgres.database}'


def DATABASE_URL_psycorg():
    """
    Формирует URL подключения для psycopg
    """
    return f'postgresql+psycopg://{config.postgres.user}:{config.postgres.password}@{config.postgres.host}:{config.postgres.port}/{config.postgres.database}'
