import json
from datetime import datetime

import redis.asyncio as aioredis

from app.core.config import settings

# Global variable to hold the Redis connection
_redis = None


# ✅ NEW: Custom JSON Encoder to handle Python datetime objects
class DateTimeEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()  # Convert datetime to string
        return super().default(obj)


async def get_redis_client():
    """
    Connects to Redis asynchronously.
    We reuse the same connection to avoid overhead.
    """
    global _redis
    if _redis is None:
        # Connect to the same Redis instance we use for ARQ
        _redis = await aioredis.from_url(
            settings.REDIS_URL, encoding="utf-8", decode_responses=True
        )
    return _redis


async def set_cache(key: str, value, expire: int = 300):
    try:
        r = await get_redis_client()
        json_str = json.dumps(value)
        print(f"🔴 Redis SET: {key} (size: {len(json_str)} bytes, expire: {expire}s)")
        await r.set(key, json_str, ex=expire)
        print("✅ Redis SET successful")
    except Exception as e:
        print(f"❌ Redis SET failed: {e}")
        raise


async def get_cache(key: str):
    try:
        r = await get_redis_client()
        data = await r.get(key)
        if data:
            print(f"🟢 Redis HIT: {key}")
            return json.loads(data)
        else:
            print(f" Redis MISS: {key}")
            return None
    except Exception as e:
        print(f"❌ Redis GET failed: {e}")
        return None


async def delete_cache(key: str):
    """
    Manually delete a cache key (used when data is updated/deleted).
    """
    r = await get_redis_client()
    await r.delete(key)
