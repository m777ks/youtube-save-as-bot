import redis.asyncio as redis
from config_data.config import ConfigEnv, load_config
from redis import Redis

config: ConfigEnv = load_config()

redis_client = redis.Redis(host=config.redis.host, port=config.redis.port, password=config.redis.password)

sync_redis = Redis(host=config.redis.host, port=config.redis.port, password=config.redis.password)