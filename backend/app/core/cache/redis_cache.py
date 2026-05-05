import json
import logging
from typing import Any, Optional
import redis.asyncio as redis
from app.core.config import settings

logger = logging.getLogger(__name__)

class RedisCacheManager:
    def __init__(self):
        self.enabled = False
        self.redis_client: Optional[redis.Redis] = None
        self._initialize_cache()

    def _initialize_cache(self):
        """Initialize Redis cache connection"""
        try:
            if settings.redis_url:
                self.redis_client = redis.from_url(settings.redis_url)
                self.enabled = True
                logger.info("Redis cache enabled")
            else:
                logger.warning("Redis URL not configured, using memory cache")
                self.enabled = False
        except Exception as e:
            logger.error(f"Failed to initialize Redis cache: {e}")
            self.enabled = False

    async def get(self, key: str) -> Any:
        """Get value from cache"""
        if not self.enabled or not self.redis_client:
            return None

        try:
            value = await self.redis_client.get(key)
            if value:
                return json.loads(value)
            return None
        except Exception as e:
            logger.error(f"Cache get error for key {key}: {e}")
            return None

    async def set(self, key: str, value: Any, ttl_seconds: int = 300) -> bool:
        """Set value in cache with TTL"""
        if not self.enabled or not self.redis_client:
            return False

        try:
            serialized_value = json.dumps(value, default=str)
            await self.redis_client.setex(key, ttl_seconds, serialized_value)
            return True
        except Exception as e:
            logger.error(f"Cache set error for key {key}: {e}")
            return False

    async def delete(self, key: str) -> bool:
        """Delete value from cache"""
        if not self.enabled or not self.redis_client:
            return False

        try:
            await self.redis_client.delete(key)
            return True
        except Exception as e:
            logger.error(f"Cache delete error for key {key}: {e}")
            return False

    async def increment(self, key: str, amount: int = 1) -> int:
        """Increment counter in cache"""
        if not self.enabled or not self.redis_client:
            return 0

        try:
            return await self.redis_client.incrby(key, amount)
        except Exception as e:
            logger.error(f"Cache increment error for key {key}: {e}")
            return 0

    async def exists(self, key: str) -> bool:
        """Check if key exists in cache"""
        if not self.enabled or not self.redis_client:
            return False

        try:
            return await self.redis_client.exists(key) > 0
        except Exception as e:
            logger.error(f"Cache exists error for key {key}: {e}")
            return False

    async def clear_pattern(self, pattern: str) -> int:
        """Clear all keys matching pattern"""
        if not self.enabled or not self.redis_client:
            return 0

        try:
            keys = await self.redis_client.keys(pattern)
            if keys:
                await self.redis_client.delete(*keys)
                return len(keys)
            return 0
        except Exception as e:
            logger.error(f"Cache clear pattern error for {pattern}: {e}")
            return 0

    async def get_ttl(self, key: str) -> int:
        """Get TTL for key"""
        if not self.enabled or not self.redis_client:
            return -1

        try:
            return await self.redis_client.ttl(key)
        except Exception as e:
            logger.error(f"Cache TTL error for key {key}: {e}")
            return -1

    async def health_check(self) -> bool:
        """Check if Redis is healthy"""
        if not self.enabled or not self.redis_client:
            return False

        try:
            await self.redis_client.ping()
            return True
        except Exception as e:
            logger.error(f"Redis health check failed: {e}")
            return False

# Global cache manager instance
cache_manager = RedisCacheManager()

# Convenience functions for easy importing
async def cache_get(key: str) -> Any:
    """Get value from cache"""
    return await cache_manager.get(key)

async def cache_set(key: str, value: Any, ttl_seconds: int = 300) -> bool:
    """Set value in cache"""
    return await cache_manager.set(key, value, ttl_seconds)

async def cache_delete(key: str) -> bool:
    """Delete value from cache"""
    return await cache_manager.delete(key)

async def cache_increment(key: str, amount: int = 1) -> int:
    """Increment counter in cache"""
    return await cache_manager.increment(key, amount)

async def cache_exists(key: str) -> bool:
    """Check if key exists"""
    return await cache_manager.exists(key)

async def cache_clear_pattern(pattern: str) -> int:
    """Clear keys matching pattern"""
    return await cache_manager.clear_pattern(pattern)