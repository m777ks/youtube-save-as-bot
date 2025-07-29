from redis_client.client_redis import redis_client, sync_redis


async def check_throttle(user_id: int, message_text: str, throttle_time: int = 3) -> bool:
    key = f"throttle:{user_id}:{message_text}"
    is_throttled = await redis_client.get(key)
    print(is_throttled)

    if is_throttled:
        return True

    await redis_client.set(key, '1', ex=throttle_time)
    return False

def del_throttle(user_id: int, message_text: str):
    key = f"throttle:{user_id}:{message_text}"
    sync_redis.delete(key)
    print(f'del key: {key}')