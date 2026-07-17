"""统一缓存抽象层

支持两种后端:
- memory (默认): 基于 Python dict + asyncio，无需额外软件
- redis: 基于 Redis 异步客户端

通过 settings.CACHE_BACKEND 切换。
"""

import asyncio
import time
from typing import Optional
from loguru import logger
from fastapi import HTTPException


class MemoryBackend:
    """基于内存的缓存后端，支持 TTL 过期"""

    def __init__(self):
        self._store: dict[
            str, tuple[float, str | int | float]
        ] = {}  # key -> (expire_time, value)
        self._lock = asyncio.Lock()

    async def get(self, key: str) -> Optional[str]:
        async with self._lock:
            result = self._store.get(key)
            if result is None:
                return None
            expire_time, value = result
            if expire_time is not None and time.time() > expire_time:
                del self._store[key]
                return None
            return value

    async def set(self, key: str, value: str, ex: Optional[int] = None) -> None:
        async with self._lock:
            expire_time = (time.time() + ex) if ex is not None else None
            self._store[key] = (expire_time, value)

    async def delete(self, key: str) -> None:
        async with self._lock:
            self._store.pop(key, None)

    async def check_rate_limit(
        self, key: str, max_attempts: int = 5, window: int = 60
    ) -> None:
        """基于内存的滑动窗口频率限制"""
        now = time.time()
        window_key = f"ratelimit:{key}"
        async with self._lock:
            records = self._store.get(window_key)
            timestamps: list[float] = []
            if records is not None:
                _, raw = records
                timestamps = raw if isinstance(raw, list) else []

            # 清除窗口外的记录
            timestamps = [t for t in timestamps if t > now - window]

            # 检查是否超限
            if len(timestamps) >= max_attempts:
                raise HTTPException(
                    status_code=429,
                    detail="请求过于频繁，请稍后再试",
                )

            # 添加当前记录
            timestamps.append(now)
            self._store[window_key] = (now + window, timestamps)

    async def close(self):
        self._store.clear()


class RedisBackend:
    """基于 Redis 的缓存后端"""

    def __init__(self, redis_client):
        self._client = redis_client

    async def get(self, key: str) -> Optional[str]:
        val = await self._client.get(key)
        return val.decode("utf-8") if val else None

    async def set(self, key: str, value: str, ex: Optional[int] = None) -> None:
        await self._client.set(key, value, ex=ex)

    async def delete(self, key: str) -> None:
        await self._client.delete(key)

    async def check_rate_limit(
        self, key: str, max_attempts: int = 5, window: int = 60
    ) -> None:
        """基于 Redis 的滑动窗口频率限制"""
        now = asyncio.get_event_loop().time()
        pipe = self._client.pipeline()
        window_key = f"ratelimit:{key}"
        await pipe.zadd(window_key, {str(now): now})
        await pipe.zremrangebyscore(window_key, 0, now - window)
        await pipe.zcard(window_key)
        await pipe.expire(window_key, window)
        results = await pipe.execute()
        count = results[2]
        if count > max_attempts:
            raise HTTPException(
                status_code=429,
                detail="请求过于频繁，请稍后再试",
            )

    async def close(self):
        await self._client.aclose()


# 全局缓存实例，由 init_cache() 初始化
_cache: Optional[MemoryBackend | RedisBackend] = None


def get_cache() -> MemoryBackend | RedisBackend:
    """获取缓存实例"""
    if _cache is None:
        raise RuntimeError("Cache not initialized. Call init_cache() first.")
    return _cache


# 兼容旧版 db.redisclient 接口
async def check_rate_limit(key: str, max_attempts: int = 5, window: int = 60) -> None:
    await get_cache().check_rate_limit(key, max_attempts, window)


async def init_cache(backend: str = "memory", settings=None):
    """初始化缓存

    Args:
        backend: "memory" 或 "redis"
        settings: Settings 实例（redis 模式需要）
    """
    global _cache

    if backend == "redis":
        if settings is None:
            raise ValueError("Redis backend requires settings")
        import redis.asyncio

        client = redis.asyncio.Redis(
            username=settings.REDIS_USERNAME,
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            password=settings.REDIS_PASSWORD,
            db=settings.REDIS_DB,
        )
        _cache = RedisBackend(client)
        logger.info("缓存后端: Redis")
    else:
        _cache = MemoryBackend()
        logger.info("缓存后端: 内存 (Memory)")


async def close_cache():
    """关闭缓存连接"""
    if _cache is not None:
        await _cache.close()
