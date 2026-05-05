"""
Cache module for Redis and in-memory caching
"""

from .redis_cache import RedisCacheManager, cache_manager
from .decorators import cached, cache_invalidate_pattern

# Alias for backward compatibility
cache = cache_manager

__all__ = [
    "RedisCacheManager",
    "cache_manager",
    "cache",  # Alias for backward compatibility
    "cached",
    "cache_invalidate_pattern"
]