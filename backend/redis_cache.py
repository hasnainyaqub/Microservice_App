import os
import json
from dotenv import load_dotenv
import redis.asyncio as redis

load_dotenv()

REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
REDIS_TTL = int(os.getenv("REDIS_TTL", 300))

redis_client = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)

async def get_menu_from_cache(branch: int):
    key = f"menu_branch_{branch}"
    data = await redis_client.get(key)
    if not data:
        return None
    try:
        return json.loads(data)
    except Exception:
        return None

async def store_menu_in_cache(branch: int, menu):
    key = f"menu_branch_{branch}"
    try:
        await redis_client.set(key, json.dumps(menu), ex=REDIS_TTL)
    except Exception:
        pass
