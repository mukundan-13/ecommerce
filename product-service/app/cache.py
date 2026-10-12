
import json
import os

import redis
from dotenv import load_dotenv

load_dotenv()

cache = redis.Redis.from_url(
    os.getenv("REDIS_URL", "redis://localhost:6379/0"),
    decode_responses=True,
)
def get_cached(key: str):
    value = cache.get(key)
    return json.loads(value) if value else None


def set_cached(key: str, value: dict, ttl: int = 60):
    cache.set(key, json.dumps(value), ex=ttl)


def delete_cached(key: str):
    cache.delete(key)
