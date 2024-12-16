import pytest
import asyncio
from unittest.mock import Mock, patch
from src.optimization.cache_manager import CacheManager
import redis
import json
import time

@pytest.fixture
def cache_manager():
    """Create a cache manager instance with mock redis"""
    return CacheManager("redis://localhost:6379/0")

@pytest.fixture
def mock_redis():
    """Create a mock redis client"""
    with patch('redis.from_url') as mock:
        yield mock

class TestCacheManager:
    @pytest.mark.asyncio
    async def test_cache_decorator(self, cache_manager):
        """Test the caching decorator"""
        call_count = 0

        @cache_manager.cached('test')
        async def test_func(x):
            nonlocal call_count
            call_count += 1
            return x * 2

        # First call should execute the function
        result1 = await test_func(5)
        assert result1 == 10
        assert call_count == 1

        # Second call should use cache
        result2 = await test_func(5)
        assert result2 == 10
        assert call_count == 1  # Function not called again

    def test_cache_key_generation(self, cache_manager):
        """Test cache key generation"""
        # Test with different argument types
        key1 = cache_manager.cache_key('test', 123, name='john')
        key2 = cache_manager.cache_key('test', 123, name='john')
        key3 = cache_manager.cache_key('test', 456, name='jane')

        assert key1 == key2  # Same args should generate same key
        assert key1 != key3  # Different args should generate different key

    def test_set_get_operations(self, cache_manager, mock_redis):
        """Test basic set and get operations"""
        # Setup mock
        mock_redis.return_value.get.return_value = json.dumps({'data': 'test'})
        mock_redis.return_value.setex.return_value = True

        # Test set operation
        result = cache_manager.set('test_key', {'data': 'test'}, 60)
        assert result is True

        # Test get operation
        data = cache_manager.get('test_key')
        assert data == {'data': 'test'}

    def test_delete_operation(self, cache_manager, mock_redis):
        """Test delete operation"""
        mock_redis.return_value.delete.return_value = 1

        result = cache_manager.delete('test_key')
        assert result is True
        mock_redis.return_value.delete.assert_called_once_with('test_key')

    def test_clear_prefix(self, cache_manager, mock_redis):
        """Test clearing keys by prefix"""
        mock_redis.return_value.keys.return_value = ['test:1', 'test:2']
        mock_redis.return_value.delete.return_value = 2

        result = cache_manager.clear_prefix('test')
        assert result is True
        mock_redis.return_value.delete.assert_called_once_with('test:1', 'test:2')

    def test_cache_stats(self, cache_manager, mock_redis):
        """Test cache statistics"""
        mock_redis.return_value.info.return_value = {
            'keyspace_hits': 100,
            'keyspace_misses': 20,
            'used_memory': 1024,
            'db0': {'keys': 50}
        }

        stats = cache_manager.get_stats()
        assert stats['hits'] == 100
        assert stats['misses'] == 20
        assert stats['memory_used'] == 1024
        assert stats['total_keys'] == 50

    @pytest.mark.asyncio
    async def test_cache_error_handling(self, cache_manager, mock_redis):
        """Test error handling in cache operations"""
        # Simulate redis error
        mock_redis.return_value.get.side_effect = redis.RedisError("Connection failed")

        @cache_manager.cached('test')
        async def test_func(x):
            return x * 2

        # Should still work despite cache error
        result = await test_func(5)
        assert result == 10

    def test_ttl_handling(self, cache_manager, mock_redis):
        """Test TTL handling in cache operations"""
        # Test with custom TTL
        cache_manager.set('test_key', 'value', ttl=30)
        mock_redis.return_value.setex.assert_called_with(
            'test_key', 30, json.dumps('value')
        )

        # Test with default TTL
        cache_manager.set('test_key', 'value')
        mock_redis.return_value.setex.assert_called_with(
            'test_key', cache_manager.default_ttl, json.dumps('value')
        )

    @pytest.mark.asyncio
    async def test_concurrent_cache_access(self, cache_manager):
        """Test concurrent cache access"""
        call_count = 0

        @cache_manager.cached('test')
        async def test_func(x):
            nonlocal call_count
            call_count += 1
            await asyncio.sleep(0.1)  # Simulate work
            return x * 2

        # Run multiple concurrent calls
        tasks = [test_func(5) for _ in range(5)]
        results = await asyncio.gather(*tasks)

        # All results should be the same
        assert all(r == 10 for r in results)
        # Function should only be called once
        assert call_count == 1

    def test_large_data_handling(self, cache_manager, mock_redis):
        """Test handling of large data objects"""
        large_data = {'key': 'x' * 1000000}  # 1MB of data
        
        # Should handle large data without issues
        result = cache_manager.set('large_key', large_data)
        assert result is True

        mock_redis.return_value.setex.assert_called_once()

    def test_invalid_json_handling(self, cache_manager, mock_redis):
        """Test handling of invalid JSON data"""
        mock_redis.return_value.get.return_value = "invalid json"

        # Should return None for invalid JSON
        result = cache_manager.get('test_key')
        assert result is None
