"""Cache decorators for endpoints"""
import json
from functools import wraps
from typing import Callable, Any
from app.core.cache import cache


def cache_response(ttl: int = 300, key_builder: Callable = None):
    """
    Decorator to cache endpoint responses.
    
    Args:
        ttl: Time to live in seconds (default 5 minutes)
        key_builder: Function to build cache key from request params.
                     If None, uses function name + all args/kwargs
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            # Build cache key
            if key_builder:
                cache_key = key_builder(*args, **kwargs)
            else:
                # Default: use function name + serialized params
                try:
                    params_str = json.dumps({
                        "args": str(args),
                        "kwargs": str(kwargs)
                    }, default=str, sort_keys=True)
                except:
                    params_str = str(args) + str(kwargs)
                cache_key = f"{func.__name__}:{params_str}"
            
            # Try to get from cache
            cached = await cache.get(cache_key)
            if cached is not None:
                return cached
            
            # Call function and cache result
            result = await func(*args, **kwargs)
            await cache.set(cache_key, result, ttl=ttl)
            return result
        
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            # Build cache key
            if key_builder:
                cache_key = key_builder(*args, **kwargs)
            else:
                try:
                    params_str = json.dumps({
                        "args": str(args),
                        "kwargs": str(kwargs)
                    }, default=str, sort_keys=True)
                except:
                    params_str = str(args) + str(kwargs)
                cache_key = f"{func.__name__}:{params_str}"
            
            # Try to get from cache
            cached = cache.get(cache_key)
            if cached is not None:
                return cached
            
            # Call function and cache result
            result = func(*args, **kwargs)
            cache.set(cache_key, result, ttl=ttl)
            return result
        
        # Return appropriate wrapper
        if hasattr(func, '__call__'):
            import inspect
            if inspect.iscoroutinefunction(func):
                return async_wrapper
            else:
                return sync_wrapper
        return func
    
    return decorator
