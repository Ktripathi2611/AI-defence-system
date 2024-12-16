from typing import Any, Optional, Dict, List
import redis
from functools import wraps
import json
import hashlib
import time
import logging
from ..utils.monitoring import MonitoringService

class CacheManager:
    def __init__(self, redis_url: str):
        self.redis_client = redis.from_url(redis_url)
        self.monitoring = MonitoringService()
        self.logger = self._setup_logger()
        self.default_ttl = 3600  # 1 hour

    def _setup_logger(self) -> logging.Logger:
        """Initialize logger for cache operations"""
        logger = logging.getLogger('cache_manager')
        logger.setLevel(logging.INFO)
        handler = logging.FileHandler('cache.log')
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        return logger

    def cache_key(self, prefix: str, *args, **kwargs) -> str:
        """Generate cache key from arguments"""
        key_parts = [prefix]
        
        # Add positional arguments
        if args:
            key_parts.extend([str(arg) for arg in args])
            
        # Add keyword arguments (sorted for consistency)
        if kwargs:
            key_parts.extend([f"{k}:{v}" for k, v in sorted(kwargs.items())])
            
        # Create hash of the key parts
        key = hashlib.md5(":".join(key_parts).encode()).hexdigest()
        return f"{prefix}:{key}"

    def cached(self, prefix: str, ttl: Optional[int] = None):
        """Decorator for caching function results"""
        def decorator(func):
            @wraps(func)
            async def wrapper(*args, **kwargs):
                # Generate cache key
                cache_key = self.cache_key(prefix, *args, **kwargs)
                
                try:
                    # Try to get from cache
                    cached_value = self.get(cache_key)
                    if cached_value is not None:
                        self.monitoring.record_metric('cache_hit', 1)
                        return cached_value

                    # If not in cache, execute function
                    self.monitoring.record_metric('cache_miss', 1)
                    result = await func(*args, **kwargs)
                    
                    # Store in cache
                    self.set(cache_key, result, ttl or self.default_ttl)
                    return result
                    
                except Exception as e:
                    self.logger.error(f'Cache error for key {cache_key}: {str(e)}')
                    self.monitoring.record_error('cache_operation', str(e))
                    # Fall back to function execution
                    return await func(*args, **kwargs)
                    
            return wrapper
        return decorator

    def get(self, key: str) -> Any:
        """Get value from cache"""
        try:
            value = self.redis_client.get(key)
            if value:
                return json.loads(value)
            return None
        except Exception as e:
            self.logger.error(f'Failed to get from cache: {str(e)}')
            self.monitoring.record_error('cache_get', str(e))
            return None

    def set(self, key: str, value: Any, ttl: int = None) -> bool:
        """Set value in cache"""
        try:
            return self.redis_client.setex(
                key,
                ttl or self.default_ttl,
                json.dumps(value)
            )
        except Exception as e:
            self.logger.error(f'Failed to set cache: {str(e)}')
            self.monitoring.record_error('cache_set', str(e))
            return False

    def delete(self, key: str) -> bool:
        """Delete value from cache"""
        try:
            return bool(self.redis_client.delete(key))
        except Exception as e:
            self.logger.error(f'Failed to delete from cache: {str(e)}')
            self.monitoring.record_error('cache_delete', str(e))
            return False

    def clear_prefix(self, prefix: str) -> bool:
        """Clear all keys with given prefix"""
        try:
            keys = self.redis_client.keys(f"{prefix}:*")
            if keys:
                return bool(self.redis_client.delete(*keys))
            return True
        except Exception as e:
            self.logger.error(f'Failed to clear prefix {prefix}: {str(e)}')
            self.monitoring.record_error('cache_clear_prefix', str(e))
            return False

    def get_stats(self) -> Dict:
        """Get cache statistics"""
        try:
            info = self.redis_client.info()
            return {
                'hits': info.get('keyspace_hits', 0),
                'misses': info.get('keyspace_misses', 0),
                'memory_used': info.get('used_memory', 0),
                'total_keys': sum(
                    db.get('keys', 0)
                    for db in info.items()
                    if isinstance(db, dict)
                )
            }
        except Exception as e:
            self.logger.error(f'Failed to get cache stats: {str(e)}')
            self.monitoring.record_error('cache_stats', str(e))
            return {}
