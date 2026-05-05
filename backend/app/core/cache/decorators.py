# Cache decorators and utilities for easy integration

import functools
import hashlib
import json
import logging
from typing import Any, Callable, Optional
from app.core.cache.redis_cache import cache_get, cache_set, cache_delete

logger = logging.getLogger(__name__)

def cache_key(*args, **kwargs) -> str:
    """Generate cache key from function arguments"""
    # Convert args and kwargs to a stable string representation
    key_parts = []

    for arg in args:
        if isinstance(arg, (str, int, float, bool)):
            key_parts.append(str(arg))
        else:
            key_parts.append(json.dumps(arg, sort_keys=True, default=str))

    for k, v in sorted(kwargs.items()):
        if isinstance(v, (str, int, float, bool)):
            key_parts.append(f"{k}:{v}")
        else:
            key_parts.append(f"{k}:{json.dumps(v, sort_keys=True, default=str)}")

    key_string = "|".join(key_parts)
    return hashlib.md5(key_string.encode()).hexdigest()

def cached(ttl_seconds: int = 300, key_prefix: str = ""):
    """Decorator to cache function results"""
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            # Generate cache key
            func_name = f"{key_prefix}:{func.__name__}" if key_prefix else func.__name__
            cache_key_value = f"{func_name}:{cache_key(*args, **kwargs)}"

            # Try to get from cache first
            cached_result = await cache_get(cache_key_value)
            if cached_result is not None:
                logger.debug(f"Cache hit for {cache_key_value}")
                return cached_result

            # Execute function
            result = await func(*args, **kwargs)

            # Cache the result
            if result is not None:
                await cache_set(cache_key_value, result, ttl_seconds)
                logger.debug(f"Cached result for {cache_key_value}")

            return result

        return wrapper
    return decorator

def cache_invalidate_pattern(pattern: str):
    """Decorator to invalidate cache patterns after function execution"""
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            result = await func(*args, **kwargs)

            # Invalidate cache patterns
            try:
                from app.core.cache.redis_cache import cache_manager
                if cache_manager.enabled:
                    import redis.asyncio as redis
                    redis_client = cache_manager.redis_client
                    if redis_client:
                        keys = await redis_client.keys(pattern)
                        if keys:
                            await redis_client.delete(*keys)
                            logger.debug(f"Invalidated {len(keys)} cache keys matching {pattern}")
            except Exception as e:
                logger.error(f"Cache invalidation error: {e}")

            return result

        return wrapper
    return decorator

def cache_invalidate_keys(*keys: str):
    """Decorator to invalidate specific cache keys after function execution"""
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            result = await func(*args, **kwargs)

            # Invalidate specific keys
            for key in keys:
                try:
                    await cache_delete(key)
                    logger.debug(f"Invalidated cache key: {key}")
                except Exception as e:
                    logger.error(f"Cache key invalidation error for {key}: {e}")

            return result

        return wrapper
    return decorator

# Specific cache utilities for common patterns
class CacheUtils:
    @staticmethod
    def user_profile_key(user_id: str) -> str:
        return f"user:profile:{user_id}"

    @staticmethod
    def user_permissions_key(user_id: str) -> str:
        return f"user:permissions:{user_id}"

    @staticmethod
    def sector_members_key(sector_id: str) -> str:
        return f"sector:members:{sector_id}"

    @staticmethod
    def complaints_list_key(filters: dict) -> str:
        return f"complaints:list:{cache_key(filters)}"

    @staticmethod
    def audit_logs_key(filters: dict) -> str:
        return f"audit:logs:{cache_key(filters)}"

    @staticmethod
    def invalidate_user_cache(user_id: str):
        """Invalidate all user-related cache"""
        return cache_invalidate_pattern(f"user:*:{user_id}")

    @staticmethod
    def invalidate_sector_cache(sector_id: str):
        """Invalidate all sector-related cache"""
        return cache_invalidate_pattern(f"sector:*:{sector_id}")

    @staticmethod
    def invalidate_complaints_cache():
        """Invalidate complaints list cache"""
        return cache_invalidate_pattern("complaints:list:*")

# Rate limiting utilities
class RateLimiter:
    def __init__(self, requests_per_minute: int = 60):
        self.requests_per_minute = requests_per_minute
        self.cache_manager = None

    async def is_allowed(self, key: str) -> bool:
        """Check if request is allowed under rate limit"""
        try:
            from app.core.cache.redis_cache import cache_manager
            if not cache_manager.enabled:
                return True  # Allow if cache is disabled

            # Use sliding window rate limiting
            window_key = f"ratelimit:{key}"
            current = await cache_manager.increment(window_key)

            if current == 1:
                # First request in window, set TTL
                await cache_manager.set(window_key, 1, 60)  # 1 minute window

            return current <= self.requests_per_minute

        except Exception as e:
            logger.error(f"Rate limiting error: {e}")
            return True  # Allow on error

# Global rate limiter instance
rate_limiter = RateLimiter()