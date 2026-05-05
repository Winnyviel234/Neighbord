import json
import time
from typing import Any

from app.core.config import settings


class CacheBackend:
    def __init__(self):
        self._store: dict[str, Any] = {}
        self._expires: dict[str, float] = {}
        self.client = None
        self.redis_enabled = False

        if settings.redis_url:
            try:
                import redis

                self.client = redis.from_url(settings.redis_url, decode_responses=True)
                self.redis_enabled = True
            except ImportError:
                self.redis_enabled = False

    def _purge_expired(self) -> None:
        now = time.time()
        for key in list(self._expires.keys()):
            if self._expires[key] <= now:
                self._store.pop(key, None)
                self._expires.pop(key, None)

    def get(self, key: str) -> Any:
        if self.redis_enabled and self.client is not None:
            value = self.client.get(key)
            if value is None:
                return None
            try:
                return json.loads(value)
            except json.JSONDecodeError:
                return value

        self._purge_expired()
        return self._store.get(key)

    def set(self, key: str, value: Any, ttl: int = 120) -> bool:
        if self.redis_enabled and self.client is not None:
            self.client.set(key, json.dumps(value), ex=ttl)
            return True

        self._store[key] = value
        self._expires[key] = time.time() + ttl
        return True

    def delete(self, key: str) -> bool:
        if self.redis_enabled and self.client is not None:
            return self.client.delete(key) > 0

        self._store.pop(key, None)
        self._expires.pop(key, None)
        return True


cache = CacheBackend()
