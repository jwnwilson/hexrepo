import asyncio
import json
from redis.asyncio import Redis

from .interface import CacheInterface
from app.config import config


class RedisCache(CacheInterface):
    def __init__(self):
        self.redis = Redis(
            host=config.REDIS_URL,
            port=config.REDIS_PORT,
            db=config.REDIS_DB,
            decode_responses=True,
        )

    async def get(self, key: str) -> str:
        return await self.redis.get(key)
    
    async def get_multi(self, keys: list[str]) -> list[str]:
        return await self.redis.mget(*keys)
    
    async def set(self, key: str, value: str, **kwargs) -> bool:
        return await self.redis.set(key, value, **kwargs)
    
    async def set_mulit(self, values: dict[str, str], **kwargs) -> bool:
        return await self.redis.mset(values, **kwargs)
