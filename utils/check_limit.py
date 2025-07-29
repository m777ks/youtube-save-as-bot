from db.ORM import DataBase
from redis_client.client_redis import redis_client


async def can_download(user_id: int,) -> bool:
    # Получаем лимит из БД
    user = await DataBase.get_user(user_id)
    if not user:
        return False  # или True, если гость — разрешить?
    limit = user.download_limit or 3

    # Получаем счетчик из Redis
    key = f"downloads:{user_id}"
    value = await redis_client.get(key)
    current = int(value) if value else 0
    return current < limit

async def incr_download(user_id: int, url: str):
    key = f"downloads:{user_id}"
    pipe = redis_client.pipeline()
    pipe.incr(key)
    pipe.expire(key, 60 * 60 * 24)
    await pipe.execute()
