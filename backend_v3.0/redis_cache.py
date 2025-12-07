import redis.asyncio as redis
import json
import os

redis_client = redis.Redis(
    host=os.getenv("REDIS_HOST", "localhost"),
    port=int(os.getenv("REDIS_PORT", 6379)),
    decode_responses=True
)

TTL = int(os.getenv("REDIS_TTL", 300))


async def get_menu_from_cache(branch):
    key = f"menu:{branch}"
    data = await redis_client.get(key)
    if data:
        return json.loads(data)
    return None


async def store_menu_in_cache(branch, data):
    key = f"menu:{branch}"
    await redis_client.set(key, json.dumps(data), ex=TTL)
