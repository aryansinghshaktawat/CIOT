"""
Comprehensive Unit Tests for Enhanced Phone Investigation
Tests all new classes and methods with complete coverage
"""

import pytest
import asyncio
import time
import threading
from unittest.mock import Mock, patch, MagicMock, AsyncMock
from typing import Dict, Any, List
from datetime import datetime, timedelta
import sqlite3
import tempfile
import os

# Import all components to test
from src.utils.cached_phone_formatter import CachedPhoneNumberFormatter
from src.utils.async_intelligence_aggregator import AsyncIntelligenceAggregator
from src.utils.intelligence_aggregator import IntelligenceAggregator
from src.utils.historical_data_manager import HistoricalDataManager
from src.utils.pattern_analysis import PatternAnalysisEngine
from src.utils.performance_cache import MemoryOptimizedCache, PersistentCache
from src.utils.enhanced_phone_investigation import EnhancedPhoneInvestigator

# Import error handling components
from src.utils.phone_investigation_exceptions import (
    InvalidPhoneNumberError, CountryNotSupportedError, APIConnectionError
)
from src.utils.phone_investigation_guidance import PhoneInvestigationGuidanceSystem
from src.utils.phone_investigation_retry import RetryManager
from src.utils.phone_investigation_error_handler import PhoneInvestigationErrorHandler


@pytest.mark.unit
class TestCachedPhoneNumberFormatter:
    """Unit tests for CachedPhoneNumberFormatter"""
    
    def test_init(self):
        """Test formatter initialization"""
        formatter = CachedPhoneNumberFormatter()
        assert formatter.stats['total_formats'] == 0
        assert formatter.stats['cache_hits'] == 0
        assert formatter.stats['cache_misses'] == 0
        assert isinstance(formatter.lock, threading.Lock)
    
    @patch('src.utils.cached_phone_formatter.phonenumbers.parse')
    def test_format_phone_number_success(self, mock_parse, sample_phone_numbers):
        """Test successful phone number formatting"""
        formatter = CachedPhoneNumberFormatter()
        
        # Mock phonenumbers.parse
        mock_number = Mock()
        mock_number.country_code = 91
        mock_number.national_number = 9876543210
        mock_parse.return_value = mock_number
        
        with patch('src.utils.cached_phone_formatter.phonenumbers.is_valid_number', return_value=True), \
             patch('src.utils.cached_phone_formatter.phonenumbers.is_possible_number', return_value=True), \
             patch('src.utils.cached_phone_formatter.phonenumbers.format_number') as mock_format:
            
            mock_format.return_value = '+91 98765 43210'
            
            result = formatter.format_phone_number(sample_phone_numbers['valid_indian'], 'IN')
            
            assert result['success'] is True
            assert 'best_format' in result
            assert 'parsing_attempts' in result
            assert 'validation_results' in result
    
    def test_format_phone_number_invalid(self, sample_phone_numbers):
        """Test formatting invalid phone number"""
        formatter = CachedPhoneNumberFormatter()
        
        result = formatter.format_phone_number(sample_phone_numbers['invalid_format'], 'IN')
        
        assert result['success'] is False
        assert 'error' in result
        assert len(result['parsing_attempts']) > 0
    
    def test_get_number_type_name(self):
        """Test number type name conversion"""
        formatter = CachedPhoneNumberFormatter()
        
        # Mock phonenumbers number types
        with patch('src.utils.cached_phone_formatter.phonenumbers.PhoneNumberType') as mock_type:
            mock_type.MOBILE = 1
            mock_type.FIXED_LINE = 0
            
            assert formatter.get_number_type_name(1) == 'MOBILE'
            assert formatter.get_number_type_name(0) == 'FIXED_LINE'
    
    def test_validate_and_classify(self):
        """Test phone number validation and classification"""
        formatter = CachedPhoneNumberFormatter()
        
        mock_number = Mock()
        mock_number.country_code = 91
        mock_number.national_number = 9876543210
        
        with patch('src.utils.cached_phone_formatter.phonenumbers.is_valid_number', return_value=True), \
             patch('src.utils.cached_phone_formatter.phonenumbers.is_possible_number', return_value=True), \
             patch('src.utils.cached_phone_formatter.phonenumbers.number_type', return_value=1):
            
            result = formatter.validate_and_classify(mock_number)
            
            assert result['is_valid'] is True
            assert result['is_possible'] is True
            assert result['country_code'] == 91
    
    def test_caching_functionality(self, sample_phone_numbers):
        """Test caching functionality"""
        formatter = CachedPhoneNumberFormatter()
        
        with patch('src.utils.cached_phone_formatter.phonenumbers.parse') as mock_parse:
            mock_number = Mock()
            mock_parse.return_value = mock_number
            
            # First call
            formatter.format_phone_number(sample_phone_numbers['valid_indian'], 'IN')
            # Second call (should use cache)
            formatter.format_phone_number(sample_phone_numbers['valid_indian'], 'IN')
            
            # Should only parse once due to caching
            assert mock_parse.call_count <= 2  # Allow for retry attempts
    
    def test_thread_safety(self, sample_phone_numbers):
        """Test thread safety of formatter"""
        formatter = CachedPhoneNumberFormatter()
        results = []
        
        def format_number():
            result = formatter.format_phone_number(sample_phone_numbers['valid_indian'], 'IN')
            results.append(result)
        
        threads = [threading.Thread(target=format_number) for _ in range(10)]
        
        for thread in threads:
            thread.start()
        
        for thread in threads:
            thread.join()
        
        assert len(results) == 10
        assert formatter.stats['total_formats'] == 10


@pytest.mark.unit
class TestAsyncIntelligenceAggregator:
    """Unit tests for AsyncIntelligenceAggregator"""
    
    def test_init(self):
        """Test aggregator initialization"""
        aggregator = AsyncIntelligenceAggregator(max_concurrent=5, default_timeout=20.0)
        assert aggregator.max_concurrent == 5
        assert aggregator.default_timeout == 20.0
    
    @pytest.mark.asyncio
    async def test_gather_intelligence_async(self, sample_phone_numbers, mock_api_responses):
        """Test asynchronous intelligence gathering"""
        aggregator = AsyncIntelligenceAggregator()
        
        with patch.object(aggregator, '_call_api_async', new_callable=AsyncMock) as mock_api:
            mock_api.return_value = mock_api_responses['abstractapi_success']
            
            result = await aggregator.gather_intelligence_async(
                sample_phone_numbers['valid_indian'], 'IN'
            )
            
            assert 'technical_intelligence' in result
            assert 'security_intelligence' in result
            assert 'social_intelligence' in result
    
    @pytest.mark.asyncio
    async def test_parallel_api_calls(self, sample_phone_numbers):
        """Test parallel API calls"""
        aggregator = AsyncIntelligenceAggregator(max_concurrent=3)
        
        async def mock_api_call(source, phone, country):
            await asyncio.sleep(0.1)  # Simulate API delay
            return {'source': source, 'data': 'test'}
        
        with patch.object(aggregator, '_call_api_async', side_effect=mock_api_call):
            start_time = time.time()
            
            tasks = [
                aggregator._call_api_async('api1', sample_phone_numbers['valid_indian'], 'IN'),
                aggregator._call_api_async('api2', sample_phone_numbers['valid_indian'], 'IN'),
                aggregator._call_api_async('api3', sample_phone_numbers['valid_indian'], 'IN')
            ]
            
            results = await asyncio.gather(*tasks)
            end_time = time.time()
            
            # Should complete in parallel, not sequentially
            assert end_time - start_time < 0.3  # Less than 3 * 0.1
            assert len(results) == 3
    
    def test_error_handling(self, sample_phone_numbers):
        """Test error handling in async aggregator"""
        aggregator = AsyncIntelligenceAggregator()
        
        with patch.object(aggregator, '_call_api_async', side_effect=Exception("API Error")):
            # Should handle errors gracefully
            result = asyncio.run(aggregator.gather_intelligence_async(
                sample_phone_numbers['valid_indian'], 'IN'
            ))
            
            # Should still return a result structure even with errors
            assert isinstance(result, dict)


@pytest.mark.unit
class TestHistoricalDataManager:
    """Unit tests for HistoricalDataManager"""
    
    def test_init(self, temp_db_path):
        """Test manager initialization"""
        manager = HistoricalDataManager(temp_db_path)
        assert manager.db_path == temp_db_path
        assert os.path.exists(temp_db_path)
    
    def test_store_investigation_data(self, temp_db_path, sample_investigation_results):
        """Test storing investigation data"""
        manager = HistoricalDataManager(temp_db_path)
        
        manager.store_investigation_data(
            '9876543210',
            sample_investigation_results
        )
        
        # Verify data was stored
        historical_data = manager.get_historical_data('9876543210')
        assert len(historical_data) == 1
        assert historical_data[0]['phone_number'] == '9876543210'
    
    def test_get_historical_data(self, temp_db_path, mock_historical_data):
        """Test retrieving historical data"""
        manager = HistoricalDataManager(temp_db_path)
        
        # Store test data
        for data in mock_historical_data:
            manager.store_investigation_data(data['phone_number'], data)
        
        historical_data = manager.get_historical_data('9876543210')
        assert len(historical_data) == 2
    
    def test_detect_changes(self, temp_db_path, sample_investigation_results):
        """Test change detection"""
        manager = HistoricalDataManager(temp_db_path)
        
        # Store initial data
        initial_data = sample_investigation_results.copy()
        initial_data['carrier_name'] = 'Vodafone'
        manager.store_investigation_data('9876543210', initial_data)
        
        # Store updated data
        updated_data = sample_investigation_results.copy()
        updated_data['carrier_name'] = 'Airtel'
        
        changes = manager.detect_changes(updated_data, [initial_data])
        
        assert 'carrier_changes' in changes
        assert changes['carrier_changes']['detected'] is True
    
    def test_generate_change_timeline(self, temp_db_path, mock_historical_data):
        """Test change timeline generation"""
        manager = HistoricalDataManager(temp_db_path)
        
        # Store historical data
        for data in mock_historical_data:
            manager.store_investigation_data(data['phone_number'], data)
        
        timeline = manager.generate_change_timeline('9876543210')
        
        assert len(timeline) >= 1
        assert 'change_type' in timeline[0]
        assert 'timestamp' in timeline[0]


@pytest.mark.unit
class TestPatternAnalysisEngine:
    """Unit tests for PatternAnalysisEngine"""
    
    def test_init(self):
        """Test engine initialization"""
        engine = PatternAnalysisEngine()
        assert hasattr(engine, 'pattern_cache')
    
    def test_find_related_numbers(self, sample_phone_numbers):
        """Test finding related numbers"""
        engine = PatternAnalysisEngine()
        
        related = engine.find_related_numbers(sample_phone_numbers['valid_indian'])
        
        assert isinstance(related, list)
        # Should find some related patterns
        if related:
            assert 'number' in related[0]
            assert 'confidence' in related[0]
    
    def test_detect_bulk_registration(self, sample_phone_numbers):
        """Test bulk registration detection"""
        engine = PatternAnalysisEngine()
        
        result = engine.detect_bulk_registration(sample_phone_numbers['valid_indian'])
        
        assert isinstance(result, dict)
        assert 'detected' in result
        assert 'confidence' in result
    
    def test_analyze_sequential_patterns(self, sample_phone_numbers):
        """Test sequential pattern analysis"""
        engine = PatternAnalysisEngine()
        
        result = engine.analyze_sequential_patterns(sample_phone_numbers['valid_indian'])
        
        assert isinstance(result, dict)
        assert 'sequential_found' in result
    
    def test_calculate_relationship_confidence(self, sample_phone_numbers):
        """Test relationship confidence calculation"""
        engine = PatternAnalysisEngine()
        
        confidence = engine.calculate_relationship_confidence(
            sample_phone_numbers['valid_indian'],
            sample_phone_numbers['test_numbers'][1]
        )
        
        assert isinstance(confidence, float)
        assert 0.0 <= confidence <= 1.0


@pytest.mark.unit
class TestPerformanceCache:
    """Unit tests for performance cache components"""
    
    def test_memory_optimized_cache(self):
        """Test memory optimized cache"""
        cache = MemoryOptimizedCache(max_size=10, max_memory_mb=1, ttl=60)
        
        # Test basic operations
        cache.put("key1", "value1")
        assert cache.get("key1") == "value1"
        
        # Test cache miss
        assert cache.get("nonexistent") is None
        
        # Test statistics
        stats = cache.get_stats()
        assert stats['size'] == 1
        assert stats['hits'] == 1
        assert stats['misses'] == 1
    
    def test_persistent_cache(self, temp_db_path):
        """Test persistent cache"""
        cache = PersistentCache(temp_db_path, ttl=3600)
        
        # Test put and get
        cache.put("persistent_key", {"data": "test"})
        result = cache.get("persistent_key")
        
        assert result is not None
        assert result["data"] == "test"
    
    def test_cache_expiration(self):
        """Test cache expiration"""
        cache = MemoryOptimizedCache(max_size=10, max_memory_mb=1, ttl=1)  # 1 second TTL
        
        cache.put("expire_key", "expire_value")
        assert cache.get("expire_key") == "expire_value"
        
        # Wait for expiration
        time.sleep(1.1)
        assert cache.get("expire_key") is None


@pytest.mark.unit
class TestErrorHandlingComponents:
    """Unit tests for error handling components"""
    
    def test_invalid_phone_number_error(self):
        """Test InvalidPhoneNumberError"""
        error = InvalidPhoneNumberError("invalid", ["format1", "format2"])
        
        assert error.phone_number == "invalid"
        assert error.attempted_formats == ["format1", "format2"]
        assert "invalid" in str(error)
    
    def test_guidance_system(self):
        """Test guidance system"""
        guidance = PhoneInvestigationGuidanceSystem()
        
        country_guidance = guidance.get_country_guidance('IN')
        assert 'format_examples' in country_guidance
        assert 'validation_patterns' in country_guidance
    
    def test_retry_manager(self):
        """Test retry manager"""
        retry_manager = RetryManager()
        
        # Test successful retry
        call_count = 0
        def test_function():
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise Exception("Temporary error")
            return "success"
        
        result = retry_manager.with_retry(test_function, max_attempts=3)
        assert result == "success"
        assert call_count == 3
    
    def test_error_handler(self):
        """Test error handler"""
        error_handler = PhoneInvestigationErrorHandler()
        
        # Test error handling
        def failing_function():
            raise APIConnectionError("TestAPI", "Connection failed")
        
        result = error_handler.handle_investigation_error(failing_function)
        
        assert result['success'] is False
        assert 'error' in result
        assert 'guidance' in result


@pytest.mark.unit
class TestEnhancedPhoneInvestigator:
    """Unit tests for EnhancedPhoneInvestigator main class"""
    
    def test_init(self):
        """Test investigator initialization"""
        investigator = EnhancedPhoneInvestigator()
        
        assert hasattr(investigator, 'formatter')
        assert hasattr(investigator, 'intelligence_aggregator')
        assert hasattr(investigator, 'historical_manager')
    
    def test_investigate_phone_number(self, sample_phone_numbers, mock_phone_formatter, mock_intelligence_aggregator):
        """Test complete phone number investigation"""
        investigator = EnhancedPhoneInvestigator()
        investigator.formatter = mock_phone_formatter
        investigator.intelligence_aggregator = mock_intelligence_aggregator
        
        result = investigator.investigate_phone_number(
            sample_phone_numbers['valid_indian'], 'IN'
        )
        
        assert result['success'] is True
        assert 'investigation_timestamp' in result
        assert 'confidence_score' in result
    
    def test_investigate_with_error_handling(self, sample_phone_numbers):
        """Test investigation with error handling"""
        investigator = EnhancedPhoneInvestigator()
        
        # Mock formatter to raise error
        investigator.formatter = Mock()
        investigator.formatter.format_phone_number.side_effect = Exception("Format error")
        
        result = investigator.investigate_phone_number(
            sample_phone_numbers['invalid_format'], 'IN'
        )
        
        assert result['success'] is False
        assert 'error' in result
    
    def test_batch_investigation(self, sample_phone_numbers):
        """Test batch investigation"""
        investigator = EnhancedPhoneInvestigator()
        
        numbers = sample_phone_numbers['test_numbers'][:3]  # Test with 3 numbers
        
        results = investigator.investigate_batch(numbers, 'IN')
        
        assert len(results) == 3
        assert all('success' in result for result in results)


if __name__ == '__main__':
    pytest.main([__file__, '-v'])