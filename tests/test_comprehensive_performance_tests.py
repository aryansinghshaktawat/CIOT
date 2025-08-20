"""
Comprehensive Performance Tests for Enhanced Phone Investigation
Tests response time validation, load testing, and performance requirements
"""

import pytest
import asyncio
import time
import threading
import concurrent.futures
from unittest.mock import Mock, patch, MagicMock
from typing import Dict, Any, List
import psutil
import os
import statistics
from datetime import datetime, timedelta

# Import components for performance testing
from src.utils.enhanced_phone_investigation import EnhancedPhoneInvestigator
from src.utils.cached_phone_formatter import CachedPhoneNumberFormatter
from src.utils.async_intelligence_aggregator import AsyncIntelligenceAggregator
from src.utils.intelligence_aggregator import IntelligenceAggregator
from src.utils.performance_cache import MemoryOptimizedCache, PersistentCache
from src.utils.osint_utils import get_enhanced_phone_info


@pytest.mark.performance
class TestResponseTimeValidation:
    """Performance tests for response time requirements"""
    
    def test_single_investigation_response_time(self, sample_phone_numbers, performance_test_config):
        """Test single investigation meets response time requirements"""
        investigator = EnhancedPhoneInvestigator()
        
        # Measure response time
        start_time = time.time()
        result = investigator.investigate_phone_number(
            sample_phone_numbers['valid_indian'], 'IN'
        )
        end_time = time.time()
        
        response_time = end_time - start_time
        
        # Verify response time meets requirements
        assert response_time < performance_test_config['max_response_time'], \
            f"Response time {response_time:.2f}s exceeds limit {performance_test_config['max_response_time']}s"
        
        # Verify we got a valid result
        assert 'success' in result
        assert result.get('investigation_timestamp') is not None
    
    def test_cached_investigation_response_time(self, sample_phone_numbers, performance_test_config):
        """Test cached investigation has faster response time"""
        investigator = EnhancedPhoneInvestigator()
        phone_number = sample_phone_numbers['valid_indian']
        
        # First investigation (cache miss)
        start_time = time.time()
        result1 = investigator.investigate_phone_number(phone_number, 'IN')
        first_time = time.time() - start_time
        
        # Second investigation (cache hit)
        start_time = time.time()
        result2 = investigator.investigate_phone_number(phone_number, 'IN')
        second_time = time.time() - start_time
        
        # Cached result should be significantly faster
        assert second_time < first_time * 0.5, \
            f"Cached response time {second_time:.2f}s not significantly faster than first {first_time:.2f}s"
        
        # Both should return valid results
        assert result1.get('success') is not None
        assert result2.get('success') is not None
    
    def test_formatter_performance(self, sample_phone_numbers, performance_test_config):
        """Test phone formatter performance"""
        formatter = CachedPhoneNumberFormatter()
        
        # Test multiple formatting operations
        times = []
        for _ in range(10):
            start_time = time.time()
            result = formatter.format_phone_number(sample_phone_numbers['valid_indian'], 'IN')
            end_time = time.time()
            times.append(end_time - start_time)
        
        # Average time should be reasonable
        avg_time = statistics.mean(times)
        assert avg_time < 1.0, f"Average formatting time {avg_time:.2f}s too slow"
        
        # Verify caching improves performance
        cached_times = times[5:]  # Later calls should be faster due to caching
        initial_times = times[:5]
        
        if len(cached_times) > 0 and len(initial_times) > 0:
            assert statistics.mean(cached_times) <= statistics.mean(initial_times)
    
    @pytest.mark.asyncio
    async def test_async_investigation_performance(self, sample_phone_numbers, performance_test_config):
        """Test asynchronous investigation performance"""
        aggregator = AsyncIntelligenceAggregator()
        
        start_time = time.time()
        result = await aggregator.gather_intelligence_async(
            sample_phone_numbers['valid_indian'], 'IN'
        )
        end_time = time.time()
        
        response_time = end_time - start_time
        
        # Async should be faster than sync for multiple API calls
        assert response_time < performance_test_config['max_response_time'], \
            f"Async response time {response_time:.2f}s exceeds limit"
        
        assert isinstance(result, dict)
    
    def test_batch_investigation_performance(self, sample_phone_numbers, performance_test_config):
        """Test batch investigation performance"""
        investigator = EnhancedPhoneInvestigator()
        
        # Test batch of 5 numbers
        numbers = sample_phone_numbers['test_numbers'][:5]
        
        start_time = time.time()
        results = investigator.investigate_batch(numbers, 'IN')
        end_time = time.time()
        
        total_time = end_time - start_time
        avg_time_per_number = total_time / len(numbers)
        
        # Batch processing should be efficient
        assert avg_time_per_number < performance_test_config['max_response_time'], \
            f"Average time per number {avg_time_per_number:.2f}s too slow"
        
        assert len(results) == len(numbers)


@pytest.mark.performance
class TestConcurrencyPerformance:
    """Performance tests for concurrent operations"""
    
    def test_concurrent_investigations(self, sample_phone_numbers, performance_test_config):
        """Test concurrent investigation performance"""
        investigator = EnhancedPhoneInvestigator()
        concurrent_requests = performance_test_config['concurrent_requests']
        
        def investigate():
            return investigator.investigate_phone_number(
                sample_phone_numbers['valid_indian'], 'IN'
            )
        
        # Run concurrent investigations
        start_time = time.time()
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=concurrent_requests) as executor:
            futures = [executor.submit(investigate) for _ in range(concurrent_requests)]
            results = [future.result() for future in concurrent.futures.as_completed(futures)]
        
        end_time = time.time()
        total_time = end_time - start_time
        
        # Concurrent execution should be efficient
        sequential_time_estimate = concurrent_requests * performance_test_config['max_response_time']
        assert total_time < sequential_time_estimate * 0.7, \
            f"Concurrent time {total_time:.2f}s not much better than sequential estimate {sequential_time_estimate:.2f}s"
        
        # All requests should succeed
        assert len(results) == concurrent_requests
        successful_results = [r for r in results if r.get('success') is not False]
        assert len(successful_results) >= concurrent_requests * 0.8  # At least 80% success rate
    
    def test_thread_safety_performance(self, sample_phone_numbers):
        """Test thread safety doesn't significantly impact performance"""
        formatter = CachedPhoneNumberFormatter()
        
        def format_number():
            return formatter.format_phone_number(sample_phone_numbers['valid_indian'], 'IN')
        
        # Single-threaded performance
        start_time = time.time()
        for _ in range(10):
            format_number()
        single_thread_time = time.time() - start_time
        
        # Multi-threaded performance
        start_time = time.time()
        threads = []
        for _ in range(10):
            thread = threading.Thread(target=format_number)
            threads.append(thread)
            thread.start()
        
        for thread in threads:
            thread.join()
        multi_thread_time = time.time() - start_time
        
        # Multi-threaded shouldn't be significantly slower
        assert multi_thread_time < single_thread_time * 2, \
            f"Multi-threaded time {multi_thread_time:.2f}s much slower than single-threaded {single_thread_time:.2f}s"
    
    @pytest.mark.asyncio
    async def test_async_concurrency_performance(self, sample_phone_numbers, performance_test_config):
        """Test async concurrency performance"""
        aggregator = AsyncIntelligenceAggregator()
        concurrent_requests = min(performance_test_config['concurrent_requests'], 5)  # Limit for async
        
        async def investigate():
            return await aggregator.gather_intelligence_async(
                sample_phone_numbers['valid_indian'], 'IN'
            )
        
        # Run concurrent async investigations
        start_time = time.time()
        
        tasks = [investigate() for _ in range(concurrent_requests)]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        end_time = time.time()
        total_time = end_time - start_time
        
        # Async concurrency should be very efficient
        assert total_time < performance_test_config['max_response_time'] * 1.5, \
            f"Async concurrent time {total_time:.2f}s too slow"
        
        # Most requests should succeed
        successful_results = [r for r in results if isinstance(r, dict) and not isinstance(r, Exception)]
        assert len(successful_results) >= concurrent_requests * 0.7  # At least 70% success rate


@pytest.mark.performance
class TestMemoryPerformance:
    """Performance tests for memory usage"""
    
    def test_memory_usage_single_investigation(self, sample_phone_numbers):
        """Test memory usage for single investigation"""
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        investigator = EnhancedPhoneInvestigator()
        result = investigator.investigate_phone_number(
            sample_phone_numbers['valid_indian'], 'IN'
        )
        
        final_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_increase = final_memory - initial_memory
        
        # Memory increase should be reasonable
        assert memory_increase < 50, f"Memory increase {memory_increase:.2f}MB too high for single investigation"
        assert result.get('success') is not None
    
    def test_memory_usage_multiple_investigations(self, sample_phone_numbers):
        """Test memory usage doesn't grow excessively with multiple investigations"""
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        investigator = EnhancedPhoneInvestigator()
        
        # Perform multiple investigations
        for i in range(20):
            phone = sample_phone_numbers['test_numbers'][i % len(sample_phone_numbers['test_numbers'])]
            investigator.investigate_phone_number(phone, 'IN')
        
        final_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_increase = final_memory - initial_memory
        
        # Memory increase should be bounded
        assert memory_increase < 100, f"Memory increase {memory_increase:.2f}MB too high for multiple investigations"
    
    def test_cache_memory_efficiency(self):
        """Test cache memory efficiency"""
        cache = MemoryOptimizedCache(max_size=100, max_memory_mb=10, ttl=3600)
        
        # Fill cache with test data
        for i in range(150):  # More than max_size
            cache.put(f"key_{i}", f"value_{i}" * 100)  # Larger values
        
        stats = cache.get_stats()
        
        # Cache should respect size limits
        assert stats['size'] <= 100, f"Cache size {stats['size']} exceeds limit"
        
        # Memory usage should be reasonable
        memory_usage = cache.get_memory_usage()
        assert memory_usage < 15, f"Cache memory usage {memory_usage:.2f}MB exceeds reasonable limit"
    
    def test_memory_cleanup_after_investigation(self, sample_phone_numbers):
        """Test memory is properly cleaned up after investigation"""
        import gc
        
        process = psutil.Process(os.getpid())
        
        # Baseline memory
        gc.collect()
        baseline_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        # Perform investigation
        investigator = EnhancedPhoneInvestigator()
        result = investigator.investigate_phone_number(
            sample_phone_numbers['valid_indian'], 'IN'
        )
        
        # Clear references and force garbage collection
        del investigator
        del result
        gc.collect()
        
        final_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_difference = final_memory - baseline_memory
        
        # Memory should return close to baseline
        assert memory_difference < 20, f"Memory not properly cleaned up, difference: {memory_difference:.2f}MB"


@pytest.mark.performance
class TestCachePerformance:
    """Performance tests for caching mechanisms"""
    
    def test_cache_hit_ratio(self, sample_phone_numbers, performance_test_config):
        """Test cache achieves good hit ratio"""
        formatter = CachedPhoneNumberFormatter()
        
        # Perform repeated operations
        phone_numbers = sample_phone_numbers['test_numbers'] * 5  # Repeat numbers
        
        for phone in phone_numbers:
            formatter.format_phone_number(phone, 'IN')
        
        stats = formatter.stats
        total_operations = stats['cache_hits'] + stats['cache_misses']
        
        if total_operations > 0:
            hit_ratio = stats['cache_hits'] / total_operations
            assert hit_ratio >= performance_test_config['cache_hit_ratio_min'], \
                f"Cache hit ratio {hit_ratio:.2f} below minimum {performance_test_config['cache_hit_ratio_min']}"
    
    def test_cache_performance_improvement(self, sample_phone_numbers):
        """Test cache provides performance improvement"""
        formatter = CachedPhoneNumberFormatter()
        phone = sample_phone_numbers['valid_indian']
        
        # First call (cache miss)
        start_time = time.time()
        result1 = formatter.format_phone_number(phone, 'IN')
        first_call_time = time.time() - start_time
        
        # Second call (cache hit)
        start_time = time.time()
        result2 = formatter.format_phone_number(phone, 'IN')
        second_call_time = time.time() - start_time
        
        # Cache should provide significant speedup
        if first_call_time > 0.01:  # Only test if first call took measurable time
            speedup_ratio = first_call_time / second_call_time
            assert speedup_ratio > 2, f"Cache speedup ratio {speedup_ratio:.2f} insufficient"
    
    def test_persistent_cache_performance(self, temp_db_path):
        """Test persistent cache performance"""
        cache = PersistentCache(temp_db_path, ttl=3600)
        
        # Test write performance
        start_time = time.time()
        for i in range(100):
            cache.put(f"key_{i}", {"data": f"value_{i}", "timestamp": time.time()})
        write_time = time.time() - start_time
        
        # Test read performance
        start_time = time.time()
        for i in range(100):
            cache.get(f"key_{i}")
        read_time = time.time() - start_time
        
        # Performance should be reasonable
        assert write_time < 5.0, f"Persistent cache write time {write_time:.2f}s too slow"
        assert read_time < 2.0, f"Persistent cache read time {read_time:.2f}s too slow"


@pytest.mark.performance
class TestScalabilityPerformance:
    """Performance tests for scalability"""
    
    def test_performance_with_increasing_load(self, sample_phone_numbers):
        """Test performance scales reasonably with increasing load"""
        investigator = EnhancedPhoneInvestigator()
        
        # Test with different load levels
        load_levels = [1, 5, 10, 20]
        response_times = []
        
        for load in load_levels:
            start_time = time.time()
            
            # Simulate load
            for _ in range(load):
                investigator.investigate_phone_number(
                    sample_phone_numbers['valid_indian'], 'IN'
                )
            
            end_time = time.time()
            avg_time = (end_time - start_time) / load
            response_times.append(avg_time)
        
        # Response time shouldn't degrade too much with load
        # Allow some degradation but not exponential
        for i in range(1, len(response_times)):
            degradation_ratio = response_times[i] / response_times[0]
            assert degradation_ratio < 3.0, \
                f"Performance degradation ratio {degradation_ratio:.2f} too high at load level {load_levels[i]}"
    
    def test_database_performance_with_large_dataset(self, temp_db_path, sample_investigation_results):
        """Test database performance with large dataset"""
        from src.utils.historical_data_manager import HistoricalDataManager
        
        manager = HistoricalDataManager(temp_db_path)
        
        # Insert large dataset
        start_time = time.time()
        for i in range(1000):
            phone = f"987654{i:04d}"
            data = sample_investigation_results.copy()
            data['phone_number'] = phone
            manager.store_investigation_data(phone, data)
        insert_time = time.time() - start_time
        
        # Query performance with large dataset
        start_time = time.time()
        for i in range(100):
            phone = f"987654{i:04d}"
            manager.get_historical_data(phone)
        query_time = time.time() - start_time
        
        # Performance should remain reasonable
        assert insert_time < 30.0, f"Large dataset insert time {insert_time:.2f}s too slow"
        assert query_time < 5.0, f"Large dataset query time {query_time:.2f}s too slow"


@pytest.mark.performance
@pytest.mark.slow
class TestStressPerformance:
    """Stress tests for performance under extreme conditions"""
    
    def test_sustained_load_performance(self, sample_phone_numbers):
        """Test performance under sustained load"""
        investigator = EnhancedPhoneInvestigator()
        
        # Run sustained load for 30 seconds
        start_time = time.time()
        end_time = start_time + 30  # 30 seconds
        
        investigation_count = 0
        response_times = []
        
        while time.time() < end_time:
            investigation_start = time.time()
            
            result = investigator.investigate_phone_number(
                sample_phone_numbers['valid_indian'], 'IN'
            )
            
            investigation_end = time.time()
            response_times.append(investigation_end - investigation_start)
            investigation_count += 1
            
            # Brief pause to avoid overwhelming
            time.sleep(0.1)
        
        # Analyze performance
        avg_response_time = statistics.mean(response_times)
        max_response_time = max(response_times)
        
        assert avg_response_time < 5.0, f"Average response time {avg_response_time:.2f}s too slow under sustained load"
        assert max_response_time < 10.0, f"Max response time {max_response_time:.2f}s too slow under sustained load"
        assert investigation_count > 50, f"Too few investigations {investigation_count} completed in 30 seconds"
    
    def test_memory_stability_under_load(self, sample_phone_numbers):
        """Test memory stability under sustained load"""
        process = psutil.Process(os.getpid())
        investigator = EnhancedPhoneInvestigator()
        
        memory_samples = []
        
        # Sample memory usage over time
        for i in range(50):
            # Perform investigation
            investigator.investigate_phone_number(
                sample_phone_numbers['test_numbers'][i % len(sample_phone_numbers['test_numbers'])], 'IN'
            )
            
            # Sample memory every 10 investigations
            if i % 10 == 0:
                memory_mb = process.memory_info().rss / 1024 / 1024
                memory_samples.append(memory_mb)
        
        # Memory should be stable (not continuously growing)
        if len(memory_samples) > 2:
            # Check if memory is continuously growing
            memory_trend = statistics.linear_regression(range(len(memory_samples)), memory_samples)
            slope = memory_trend.slope
            
            # Slope should be small (not continuously growing)
            assert slope < 5.0, f"Memory continuously growing at {slope:.2f}MB per sample"


if __name__ == '__main__':
    pytest.main([__file__, '-v', '-m', 'performance'])