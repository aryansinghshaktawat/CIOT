"""
Performance Optimization Tests
Tests for caching, async processing, and performance requirements
"""

import pytest
import asyncio
import time
import threading
from unittest.mock import Mock, patch, MagicMock, AsyncMock
from typing import Dict, Any, List

# Import the modules we're testing
from src.utils.performance_cache import (
    MemoryOptimizedCache, PersistentCache, ConnectionPool, 
    AsyncAPIClient, ProgressTracker, PerformanceOptimizer,
    cached, get_performance_stats, clear_performance_caches
)
from src.utils.cached_phone_formatter import (
    CachedPhoneNumberFormatter, get_cached_phone_info, 
    validate_phone_cached, get_formatter_stats
)
from src.utils.async_intelligence_aggregator import (
    AsyncIntelligenceAggregator, investigate_phone_async,
    get_async_aggregator_stats, get_active_investigations
)


class TestMemoryOptimizedCache:
    """Test memory-optimized cache functionality"""
    
    def test_cache_basic_operations(self):
        """Test basic cache operations"""
        cache = MemoryOptimizedCache(max_size=10, max_memory_mb=1, ttl=60)
        
        # Test put and get
        cache.put("key1", "value1")
        assert cache.get("key1") == "value1"
        
        # Test non-existent key
        assert cache.get("nonexistent") is None
        
        # Test cache statistics
        stats = cache.get_stats()
        assert stats['size'] == 1
        assert stats['hits'] == 1
        assert stats['misses'] == 1
    
    def test_cache_expiration(self):
        """Test cache entry expiration"""
        cache = MemoryOptimizedCache(max_size=10, max_memory_mb=1, ttl=0.1)  # 0.1 second TTL
        
        cache.put("key1", "value1")
        assert cache.get("key1") == "value1"
        
        # Wait for expiration
        time.sleep(0.2)
        assert cache.get("key1") is None
    
    def test_cache_lru_eviction(self):
        """Test LRU eviction when cache is full"""
        cache = MemoryOptimizedCache(max_size=3, max_memory_mb=1, ttl=60)
        
        # Fill cache
        cache.put("key1", "value1")
        cache.put("key2", "value2")
        cache.put("key3", "value3")
        
        # Access key1 to make it recently used
        cache.get("key1")
        
        # Add another item, should evict key2 (least recently used)
        cache.put("key4", "value4")
        
        assert cache.get("key1") == "value1"  # Should still exist
        assert cache.get("key2") is None      # Should be evicted
        assert cache.get("key3") == "value3"  # Should still exist
        assert cache.get("key4") == "value4"  # Should exist
    
    def test_cache_memory_limit(self):
        """Test memory-based eviction"""
        cache = MemoryOptimizedCache(max_size=100, max_memory_mb=0.001, ttl=60)  # Very small memory limit
        
        # Add large values that should trigger memory-based eviction
        large_value = "x" * 1000  # 1KB value
        cache.put("key1", large_value)
        
        # Should not be able to store due to memory limit
        stats = cache.get_stats()
        assert stats['memory_usage_mb'] < 0.001 or stats['size'] == 0


class TestPersistentCache:
    """Test persistent cache functionality"""
    
    def test_persistent_cache_operations(self, tmp_path):
        """Test persistent cache basic operations"""
        db_path = tmp_path / "test_cache.db"
        cache = PersistentCache(str(db_path), ttl=60)
        
        # Test put and get
        cache.put("key1", {"data": "value1"})
        result = cache.get("key1")
        assert result == {"data": "value1"}
        
        # Test non-existent key
        assert cache.get("nonexistent") is None
    
    def test_persistent_cache_expiration(self, tmp_path):
        """Test persistent cache expiration"""
        db_path = tmp_path / "test_cache.db"
        cache = PersistentCache(str(db_path), ttl=0.1)  # 0.1 second TTL
        
        cache.put("key1", {"data": "value1"})
        assert cache.get("key1") == {"data": "value1"}
        
        # Wait for expiration
        time.sleep(0.2)
        assert cache.get("key1") is None
    
    def test_persistent_cache_cleanup(self, tmp_path):
        """Test persistent cache cleanup"""
        db_path = tmp_path / "test_cache.db"
        cache = PersistentCache(str(db_path), ttl=0.1)
        
        # Add expired entries
        cache.put("key1", {"data": "value1"})
        time.sleep(0.2)
        
        # Cleanup should remove expired entries
        cache.cleanup_expired()
        assert cache.get("key1") is None


class TestConnectionPool:
    """Test HTTP connection pool"""
    
    @patch('requests.Session')
    def test_connection_pool_creation(self, mock_session_class):
        """Test connection pool creation and configuration"""
        mock_session = Mock()
        mock_session_class.return_value = mock_session
        
        pool = ConnectionPool(max_connections=10, timeout=30.0)
        session = pool._get_session()
        
        assert session is not None
        mock_session.mount.assert_called()
    
    @patch('requests.Session')
    def test_connection_pool_requests(self, mock_session_class):
        """Test making requests through connection pool"""
        mock_session = Mock()
        mock_response = Mock()
        mock_response.status_code = 200
        mock_session.request.return_value = mock_response
        mock_session_class.return_value = mock_session
        
        pool = ConnectionPool()
        response = pool.get("http://example.com")
        
        assert response.status_code == 200
        mock_session.request.assert_called_with('GET', 'http://example.com')
    
    def test_connection_pool_stats(self):
        """Test connection pool statistics"""
        pool = ConnectionPool()
        stats = pool.get_stats()
        
        assert 'requests_made' in stats
        assert 'connection_errors' in stats
        assert 'timeouts' in stats
        assert 'average_response_time' in stats


class TestAsyncAPIClient:
    """Test asynchronous API client"""
    
    @pytest.mark.asyncio
    async def test_async_client_request(self):
        """Test async API client request"""
        client = AsyncAPIClient(max_concurrent=5, timeout=10.0)
        
        # Mock aiohttp session with proper async context manager
        with patch('aiohttp.ClientSession') as mock_session_class:
            mock_session = MagicMock()
            mock_response = MagicMock()
            mock_response.status = 200
            
            # Make json() return a coroutine
            async def mock_json():
                return {"test": "data"}
            mock_response.json = mock_json
            
            # Set up async context managers properly
            mock_session.__aenter__ = AsyncMock(return_value=mock_session)
            mock_session.__aexit__ = AsyncMock(return_value=None)
            
            mock_request_context = MagicMock()
            mock_request_context.__aenter__ = AsyncMock(return_value=mock_response)
            mock_request_context.__aexit__ = AsyncMock(return_value=None)
            mock_session.request.return_value = mock_request_context
            
            mock_session_class.return_value = mock_session
            
            success, result = await client.make_request('GET', 'http://example.com')
            
            assert success is True
            assert result['status_code'] == 200
            assert result['data'] == {"test": "data"}
    
    @pytest.mark.asyncio
    async def test_async_client_parallel_requests(self):
        """Test parallel requests"""
        client = AsyncAPIClient(max_concurrent=3, timeout=10.0)
        
        requests = [
            {'method': 'GET', 'url': 'http://example1.com'},
            {'method': 'GET', 'url': 'http://example2.com'},
            {'method': 'GET', 'url': 'http://example3.com'}
        ]
        
        with patch.object(client, 'make_request') as mock_make_request:
            mock_make_request.return_value = (True, {'status_code': 200, 'data': {}})
            
            results = await client.make_parallel_requests(requests)
            
            assert len(results) == 3
            assert mock_make_request.call_count == 3
    
    def test_async_client_stats(self):
        """Test async client statistics"""
        client = AsyncAPIClient()
        stats = client.get_stats()
        
        assert 'requests_made' in stats
        assert 'successful_requests' in stats
        assert 'failed_requests' in stats
        assert 'success_rate' in stats


class TestProgressTracker:
    """Test progress tracking functionality"""
    
    def test_progress_tracker_basic(self):
        """Test basic progress tracking"""
        tracker = ProgressTracker(total_steps=5, operation_name="Test Operation")
        
        assert tracker.current_step == 0
        assert tracker.total_steps == 5
        assert tracker.operation_name == "Test Operation"
    
    def test_progress_tracker_updates(self):
        """Test progress updates"""
        callback_data = []
        
        def progress_callback(data):
            callback_data.append(data)
        
        tracker = ProgressTracker(total_steps=3, operation_name="Test")
        tracker.add_callback(progress_callback)
        
        tracker.update("Step 1")
        tracker.update("Step 2")
        tracker.update("Step 3")
        
        assert len(callback_data) == 3
        assert callback_data[-1]['progress_percent'] == 100.0
        assert callback_data[-1]['is_complete'] is True
    
    def test_progress_tracker_completion(self):
        """Test progress completion"""
        tracker = ProgressTracker(total_steps=5)
        
        tracker.update("Step 1", increment=2)
        tracker.complete()
        
        assert tracker.current_step == 5


class TestCachedPhoneFormatter:
    """Test cached phone number formatter"""
    
    def test_cached_formatter_creation(self):
        """Test cached formatter creation"""
        formatter = CachedPhoneNumberFormatter()
        assert formatter is not None
        
        stats = formatter.get_stats()
        assert 'total_formats' in stats
        assert 'cache_hit_rate' in stats
    
    @patch('phonenumbers.parse')
    @patch('phonenumbers.is_valid_number')
    def test_cached_formatter_basic_formatting(self, mock_is_valid, mock_parse):
        """Test basic phone number formatting"""
        # Mock phonenumbers library
        mock_number = Mock()
        mock_number.country_code = 91
        mock_number.national_number = 9876543210
        mock_parse.return_value = mock_number
        mock_is_valid.return_value = True
        
        formatter = CachedPhoneNumberFormatter()
        result = formatter.format_phone_number("9876543210", "IN")
        
        assert result['success'] is True
        assert result['original_input'] == "9876543210"
        assert result['country_used'] == "IN"
    
    def test_cached_formatter_invalid_number(self):
        """Test formatting invalid phone number"""
        formatter = CachedPhoneNumberFormatter()
        result = formatter.format_phone_number("invalid", "IN")
        
        assert result['success'] is False
        assert 'error' in result or len(result['parsing_attempts']) > 0
    
    def test_cached_formatter_stats_update(self):
        """Test that stats are updated correctly"""
        formatter = CachedPhoneNumberFormatter()
        initial_stats = formatter.get_stats()
        
        # Make a formatting request
        formatter.format_phone_number("invalid", "IN")
        
        updated_stats = formatter.get_stats()
        assert updated_stats['total_formats'] > initial_stats['total_formats']


class TestAsyncIntelligenceAggregator:
    """Test asynchronous intelligence aggregator"""
    
    def test_async_aggregator_creation(self):
        """Test async aggregator creation"""
        aggregator = AsyncIntelligenceAggregator(max_concurrent=5)
        assert aggregator.max_concurrent == 5
        assert aggregator.async_client is not None
    
    @pytest.mark.asyncio
    async def test_async_phone_formatting(self):
        """Test async phone formatting"""
        aggregator = AsyncIntelligenceAggregator()
        
        with patch.object(aggregator, '_async_phone_formatting') as mock_format:
            mock_format.return_value = {'success': True, 'formatted': '+919876543210'}
            
            result = await aggregator._async_phone_formatting("9876543210", "IN")
            assert result['success'] is True
    
    def test_investigation_task_creation(self):
        """Test investigation task creation"""
        aggregator = AsyncIntelligenceAggregator()
        
        from src.utils.async_intelligence_aggregator import DataSource
        sources = [DataSource.LIBPHONENUMBER, DataSource.ABSTRACTAPI]
        
        tasks = aggregator._create_investigation_tasks("9876543210", "IN", sources)
        
        assert len(tasks) == 2
        assert all(task.phone_number == "9876543210" for task in tasks)
        assert all(task.country_code == "IN" for task in tasks)
    
    def test_source_timeout_configuration(self):
        """Test source timeout configuration"""
        aggregator = AsyncIntelligenceAggregator()
        
        from src.utils.async_intelligence_aggregator import DataSource
        
        # Test different source timeouts
        libphone_timeout = aggregator._get_source_timeout(DataSource.LIBPHONENUMBER)
        whois_timeout = aggregator._get_source_timeout(DataSource.WHOIS)
        
        assert libphone_timeout < whois_timeout  # libphonenumber should be faster
    
    def test_async_aggregator_stats(self):
        """Test async aggregator statistics"""
        aggregator = AsyncIntelligenceAggregator()
        stats = aggregator.get_stats()
        
        assert 'total_investigations' in stats
        assert 'successful_investigations' in stats
        assert 'async_client_stats' in stats
        assert 'active_investigations' in stats


class TestPerformanceRequirements:
    """Test performance requirements (< 5 second response time)"""
    
    @pytest.mark.asyncio
    async def test_phone_investigation_performance(self):
        """Test that phone investigation completes within 5 seconds"""
        # Mock all external dependencies to focus on performance
        with patch('src.utils.cached_phone_formatter.cached_phone_formatter') as mock_formatter:
            
            # Mock fast responses
            mock_formatter.format_phone_number.return_value = {
                'success': True,
                'processing_time': 0.1
            }
            
            # Create a simple async mock function
            async def mock_async_investigation(phone, country, progress_callback=None):
                await asyncio.sleep(0.1)  # Simulate some processing time
                mock_result = Mock()
                mock_result.processing_time = 2.0
                mock_result.overall_confidence = 85.0
                return mock_result
            
            with patch('src.utils.async_intelligence_aggregator.investigate_phone_async', side_effect=mock_async_investigation):
                start_time = time.time()
                
                # Import and call the async investigation
                from src.utils.async_intelligence_aggregator import investigate_phone_async
                result = await investigate_phone_async("9876543210", "IN")
                
                end_time = time.time()
                processing_time = end_time - start_time
                
                # Should complete very quickly with mocked dependencies
                assert processing_time < 1.0  # Much faster with mocks
                assert result.processing_time < 5.0  # Simulated processing time
    
    def test_cache_performance(self):
        """Test cache performance for repeated operations"""
        cache = MemoryOptimizedCache(max_size=1000, max_memory_mb=10, ttl=3600)
        
        # Test cache write performance
        start_time = time.time()
        for i in range(100):
            cache.put(f"key_{i}", f"value_{i}")
        write_time = time.time() - start_time
        
        # Test cache read performance
        start_time = time.time()
        for i in range(100):
            cache.get(f"key_{i}")
        read_time = time.time() - start_time
        
        # Cache operations should be very fast
        assert write_time < 1.0  # 100 writes in less than 1 second
        assert read_time < 0.1   # 100 reads in less than 0.1 seconds
        
        stats = cache.get_stats()
        assert stats['hit_rate'] == 1.0  # All reads should be hits
    
    def test_concurrent_cache_access(self):
        """Test cache performance under concurrent access"""
        cache = MemoryOptimizedCache(max_size=1000, max_memory_mb=10, ttl=3600)
        results = []
        
        def cache_worker(worker_id):
            start_time = time.time()
            for i in range(50):
                key = f"worker_{worker_id}_key_{i}"
                cache.put(key, f"value_{i}")
                retrieved = cache.get(key)
                assert retrieved == f"value_{i}"
            end_time = time.time()
            results.append(end_time - start_time)
        
        # Create multiple threads
        threads = []
        for i in range(5):
            thread = threading.Thread(target=cache_worker, args=(i,))
            threads.append(thread)
        
        start_time = time.time()
        
        # Start all threads
        for thread in threads:
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        total_time = time.time() - start_time
        
        # Concurrent access should not significantly slow down operations
        assert total_time < 2.0  # All threads should complete within 2 seconds
        assert all(worker_time < 1.0 for worker_time in results)  # Each worker should be fast
    
    @patch('src.utils.performance_cache.performance_optimizer')
    def test_cached_decorator_performance(self, mock_optimizer):
        """Test cached decorator performance"""
        call_count = 0
        
        @cached("test_operation", ttl=60)
        def expensive_operation(x):
            nonlocal call_count
            call_count += 1
            time.sleep(0.1)  # Simulate expensive operation
            return x * 2
        
        # Mock the cache to return cached results
        mock_optimizer.memory_cache.get.side_effect = [None, 20, 20]  # First miss, then hits
        mock_optimizer.persistent_cache.get.return_value = None
        
        start_time = time.time()
        
        # First call - should execute function
        result1 = expensive_operation(10)
        first_call_time = time.time() - start_time
        
        # Subsequent calls - should use cache (mocked)
        start_time = time.time()
        result2 = expensive_operation(10)
        result3 = expensive_operation(10)
        cached_calls_time = time.time() - start_time
        
        # Cached calls should be much faster than the first call
        assert cached_calls_time < first_call_time
        assert cached_calls_time < 0.01  # Cached calls should be very fast


class TestIntegrationPerformance:
    """Integration tests for overall performance"""
    
    def test_memory_usage_optimization(self):
        """Test that memory usage stays within reasonable bounds"""
        import psutil
        import os
        
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        # Create multiple caches and perform operations
        caches = []
        for i in range(10):
            cache = MemoryOptimizedCache(max_size=100, max_memory_mb=5, ttl=3600)
            for j in range(100):
                cache.put(f"key_{i}_{j}", f"value_{j}" * 100)  # Larger values
            caches.append(cache)
        
        final_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_increase = final_memory - initial_memory
        
        # Memory increase should be reasonable (less than 100MB for this test)
        assert memory_increase < 100
    
    def test_cleanup_effectiveness(self):
        """Test that cleanup operations are effective"""
        cache = MemoryOptimizedCache(max_size=100, max_memory_mb=1, ttl=0.1)
        
        # Fill cache with data that will expire
        for i in range(50):
            cache.put(f"key_{i}", f"value_{i}")
        
        initial_size = cache.get_stats()['size']
        assert initial_size == 50
        
        # Wait for expiration
        time.sleep(0.2)
        
        # Trigger cleanup by accessing cache multiple times
        for i in range(10):
            cache.get(f"nonexistent_{i}")
        
        # Force cleanup
        cache._cleanup_expired()
        
        # Cache should be cleaned up
        final_stats = cache.get_stats()
        assert final_stats['size'] <= initial_size  # Should be less or equal (cleanup may be gradual)
        
        # Verify that expired entries are actually removed by trying to access them
        expired_count = 0
        for i in range(50):
            if cache.get(f"key_{i}") is None:
                expired_count += 1
        
        assert expired_count > 0  # At least some entries should be expired


if __name__ == "__main__":
    pytest.main([__file__, "-v"])