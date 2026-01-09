import asyncio
from datetime import timedelta
from redis import asyncio as aioredis
from typing import Any, Optional
from config import settings

class RedisManager:
    """Асинхронный менеджер для работы с Redis."""

    def __init__(self, prefix: str, url: str = "redis://localhost:6379", ttl: int = 600):
        """
        :param url: строка подключения к Redis
        :param ttl: время жизни ключей по умолчанию (в секундах)
        """
        self._url = url
        self._ttl = ttl
        self._prefix = prefix
        self._redis: Optional[aioredis.Redis] = None

    def _key_handler(self, key: Any):
        return self._prefix + str(key).rstrip(":") + ":"

    async def connect(self):
        """Установить соединение с Redis."""
        if not self._redis:
            self._redis = aioredis.from_url(
                self._url,
                encoding="utf-8",
                decode_responses=True,
            )

    async def close(self):
        """Закрыть соединение с Redis."""
        if self._redis:
            await self._redis.close()
            self._redis = None

    async def set(self, key: str, value: Any, ttl: Optional[int | timedelta] = None):
        """Установить значение по ключу с TTL."""
        if not self._redis:
            raise RuntimeError("Redis не подключён. Вызови connect().")

        if isinstance(ttl, timedelta):
            ttl = int(ttl.total_seconds())
        key = self._key_handler(key)
        await self._redis.set(key, value, ex=ttl or self._ttl)

    async def get(self, key: str) -> Optional[str]:
        """Получить значение по ключу."""
        if not self._redis:
            raise RuntimeError("Redis не подключён. Вызови connect().")
        key = self._key_handler(key)
        return await self._redis.get(key)

    async def delete(self, key: str):
        """Удалить ключ."""
        if not self._redis:
            raise RuntimeError("Redis не подключён. Вызови connect().")
        key = self._key_handler(key)
        await self._redis.delete(key)

    async def exists(self, key: str) -> bool:
        """Проверить, существует ли ключ."""
        if not self._redis:
            raise RuntimeError("Redis не подключён. Вызови connect().")
        key = self._key_handler(key)
        return bool(await self._redis.exists(key))

    async def ttl(self, key: str) -> int:
        """Посмотреть, сколько осталось жить ключу (в секундах)."""
        if not self._redis:
            raise RuntimeError("Redis не подключён. Вызови connect().")
        key = self._key_handler(key)
        return await self._redis.ttl(key)

    async def __aenter__(self):
        await self.connect()
        return self

    async def __aexit__(self, exc_type, exc, tb):
        await self.close()