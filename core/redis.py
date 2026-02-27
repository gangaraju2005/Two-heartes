import redis
from core.config import settings

# Redis client (single instance, reused everywhere)
redis_client = redis.Redis.from_url(
    settings.REDIS_URL,
    decode_responses=True
)


def get_redis():
    """
    Dependency-style helper if needed later
    """
    return redis_client
