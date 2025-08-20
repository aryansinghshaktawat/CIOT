"""
Comprehensive Integration Tests for Enhanced Phone Investigation
Tests API interactions, component integration, and data flow
"""

import pytest
import asyncio
import time
import json
from unittest.mock import Mock, patch, MagicMock, AsyncMock
from typing import Dict, Any, List
import requests
import aiohttp

# Import components for integration testing
from src.utils.enhanced_phone_investigation import EnhancedPhoneInvestigator
from src.utils.intelligence_aggregator import IntelligenceAggregator
from src.utils.async_intelligence_aggregator import AsyncIntelligenceAggregator
from src.utils.cached_phone_formatter import CachedPhoneNumberFormatter
from src.utils.historical_data_manager import HistoricalDataManager
from src.utils.pattern_analysis import PatternAnalysisEngine
from src.utils.osint_utils import get_enhanced_phone_info


@pytest.mark.integration
class TestAPIIntegrations:
    """Integration tests for external API interactions"""
    
    @patch('requests.get')
    def test_abstractapi_integration(self, mock_get, sample_phone_numbers, mock_api_responses):
        """Test AbstractAPI integration"""
        # Mock successful API response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = mock_api_responses['abstractapi_success']
        mock_get.return_value = mock_response
        
        aggregator = IntelligenceAggregator()
        result = aggregator._call_abstractapi(sample_phone_numbers['valid_indian'])
        
        assert result['success'] is True
        assert result['data']['valid'] is True
        assert result['data']['country']['code'] == 'IN'
        
        # Verify API was called with correct parameters
        mock_get.assert_called_once()
        call_args = mock_get.call_args
        assert 'abstractapi.com' in call_args[0][0]
    
    @patch('requests.get')
    def test_neutrino_api_integration(self, mock_get, sample_phone_numbers, mock_api_responses):
        """Test Neutrino API integration"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = mock_api_responses['neutrino_success']
        mock_get.return_value = mock_response
        
        aggregator = IntelligenceAggregator()
        result = aggregator._call_neutrino_api(sample_phone_numbers['valid_indian'])
        
        assert result['success'] is True
        assert result['data']['valid'] is True
        assert result['data']['country'] == 'India'
    
    @patch('requests.get')
    def test_api_error_handling(self, mock_get, sample_phone_numbers, mock_api_responses):
        """Test API error handling"""
        # Mock API error response
        mock_response = Mock()
        mock_response.status_code = 429
        mock_response.json.return_value = mock_api_responses['api_error']
        mock_get.return_value = mock_response
        
        aggregator = IntelligenceAggregator()
        result = aggregator._call_abstractapi(sample_phone_numbers['valid_indian'])
        
        assert result['success'] is False
        assert 'error' in result
        assert result['error_code'] == 429
    
    @patch('requests.get')
    def test_api_timeout_handling(self, mock_get, sample_phone_numbers):
        """Test API timeout handling"""
        # Mock timeout exception
        mock_get.side_effect = requests.exceptions.Timeout("Request timeout")
        
        aggregator = IntelligenceAggregator()
        result = aggregator._call_abstractapi(sample_phone_numbers['valid_indian'])
        
        assert result['success'] is False
        assert 'timeout' in result['error'].lower()
    
    @patch('requests.get')
    def test_api_connection_error(self, mock_get, sample_phone_numbers):
        """Test API connection error handling"""
        # Mock connection error
        mock_get.side_effect = requests.exceptions.ConnectionError("Connection failed")
        
        aggregator = IntelligenceAggregator()
        result = aggregator._call_abstractapi(sample_phone_numbers['valid_indian'])
        
        assert result['success'] is False
        assert 'connection' in result['error'].lower()
    
    @pytest.mark.asyncio
    @patch('aiohttp.ClientSession.get')
    async def test_async_api_integration(self, mock_get, sample_phone_numbers, mock_api_responses):
        """Test asynchronous API integration"""
        # Mock async API response
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.json = AsyncMock(return_value=mock_api_responses['abstractapi_success'])
        mock_get.return_value.__aenter__.return_value = mock_response
        
        aggregator = AsyncIntelligenceAggregator()
        result = await aggregator._call_api_async('abstractapi', sample_phone_numbers['valid_indian'], 'IN')
        
        assert result['success'] is True
        assert result['data']['valid'] is True
    
    def test_multiple_api_aggregation(self, sample_phone_numbers):
        """Test aggregation from multiple APIs"""
        aggregator = IntelligenceAggregator()
        
        with patch.object(aggregator, '_call_abstractapi') as mock_abstract, \
             patch.object(aggregator, '_call_neutrino_api') as mock_neutrino, \
             patch.object(aggregator, '_call_findandtrace_api') as mock_findtrace:
            
            # Mock successful responses from all APIs
            mock_abstract.return_value = {
                'success': True,
                'data': {'carrier': 'Airtel', 'country': {'code': 'IN'}}
            }
            mock_neutrino.return_value = {
                'success': True,
                'data': {'carrier': 'Airtel', 'location': 'Mumbai'}
            }
            mock_findtrace.return_value = {
                'success': True,
                'data': {'carrier': 'Airtel', 'type': 'mobile'}
            }
            
            result = aggregator.gather_comprehensive_intelligence(
                sample_phone_numbers['valid_indian'], 'IN'
            )
            
            assert result['technical_intelligence']['carrier'] == 'Airtel'
            assert len(result['api_sources_used']) >= 3


@pytest.mark.integration
class TestComponentIntegration:
    """Integration tests for component interactions"""
    
    def test_formatter_aggregator_integration(self, sample_phone_numbers):
        """Test integration between formatter and aggregator"""
        formatter = CachedPhoneNumberFormatter()
        aggregator = IntelligenceAggregator()
        
        # Mock successful formatting
        with patch.object(formatter, 'format_phone_number') as mock_format:
            mock_format.return_value = {
                'success': True,
                'best_format': {
                    'international': '+91 98765 43210',
                    'e164': '+919876543210'
                },
                'validation_results': {
                    'is_valid': True,
                    'country_code': 91,
                    'carrier': 'Airtel'
                }
            }
            
            # Mock aggregator
            with patch.object(aggregator, 'gather_comprehensive_intelligence') as mock_gather:
                mock_gather.return_value = {
                    'technical_intelligence': {'carrier': 'Airtel'},
                    'security_intelligence': {'spam_risk_score': 0.2}
                }
                
                investigator = EnhancedPhoneInvestigator()
                investigator.formatter = formatter
                investigator.intelligence_aggregator = aggregator
                
                result = investigator.investigate_phone_number(
                    sample_phone_numbers['valid_indian'], 'IN'
                )
                
                assert result['success'] is True
                assert result['international_format'] == '+91 98765 43210'
                assert result['carrier_name'] == 'Airtel'
    
    def test_historical_data_integration(self, temp_db_path, sample_phone_numbers, sample_investigation_results):
        """Test integration with historical data manager"""
        historical_manager = HistoricalDataManager(temp_db_path)
        investigator = EnhancedPhoneInvestigator()
        investigator.historical_manager = historical_manager
        
        # Store initial investigation
        historical_manager.store_investigation_data(
            sample_phone_numbers['valid_indian'],
            sample_investigation_results
        )
        
        # Mock new investigation with changes
        new_results = sample_investigation_results.copy()
        new_results['carrier_name'] = 'Jio'  # Changed carrier
        
        with patch.object(investigator, '_perform_investigation') as mock_investigate:
            mock_investigate.return_value = new_results
            
            result = investigator.investigate_phone_number(
                sample_phone_numbers['valid_indian'], 'IN'
            )
            
            # Should detect carrier change
            assert 'historical_changes' in result
            if result['historical_changes']:
                assert any('carrier' in change.get('change_type', '') 
                          for change in result['historical_changes'])
    
    def test_pattern_analysis_integration(self, sample_phone_numbers):
        """Test integration with pattern analysis"""
        pattern_engine = PatternAnalysisEngine()
        investigator = EnhancedPhoneInvestigator()
        investigator.pattern_engine = pattern_engine
        
        with patch.object(pattern_engine, 'find_related_numbers') as mock_related, \
             patch.object(pattern_engine, 'detect_bulk_registration') as mock_bulk:
            
            mock_related.return_value = [
                {'number': '9876543211', 'confidence': 0.8, 'pattern_type': 'sequential'}
            ]
            mock_bulk.return_value = {
                'detected': True,
                'confidence': 0.7,
                'block_size': 100
            }
            
            result = investigator.investigate_phone_number(
                sample_phone_numbers['valid_indian'], 'IN'
            )
            
            assert 'related_numbers' in result
            assert 'bulk_registration_status' in result
            assert result['bulk_registration_status']['detected'] is True
    
    def test_error_handling_integration(self, sample_phone_numbers):
        """Test error handling integration across components"""
        investigator = EnhancedPhoneInvestigator()
        
        # Mock formatter to fail
        with patch.object(investigator.formatter, 'format_phone_number') as mock_format:
            mock_format.side_effect = Exception("Formatting failed")
            
            result = investigator.investigate_phone_number(
                sample_phone_numbers['invalid_format'], 'IN'
            )
            
            assert result['success'] is False
            assert 'error' in result
            assert 'guidance' in result
    
    def test_caching_integration(self, sample_phone_numbers):
        """Test caching integration across components"""
        investigator = EnhancedPhoneInvestigator()
        
        # First investigation
        result1 = investigator.investigate_phone_number(
            sample_phone_numbers['valid_indian'], 'IN'
        )
        
        # Second investigation (should use cache)
        start_time = time.time()
        result2 = investigator.investigate_phone_number(
            sample_phone_numbers['valid_indian'], 'IN'
        )
        end_time = time.time()
        
        # Second call should be faster due to caching
        assert end_time - start_time < 1.0  # Should be very fast
        assert result1['original_input'] == result2['original_input']


@pytest.mark.integration
class TestWorkflowIntegration:
    """Integration tests for complete workflow"""
    
    def test_complete_investigation_workflow(self, sample_phone_numbers):
        """Test complete investigation workflow from input to output"""
        # Test the main entry point
        result = get_enhanced_phone_info(sample_phone_numbers['valid_indian'], 'IN')
        
        # Verify complete result structure
        expected_fields = [
            'success', 'original_input', 'investigation_timestamp',
            'formatting_success', 'international_format', 'is_valid',
            'country_name', 'carrier_name', 'confidence_score'
        ]
        
        for field in expected_fields:
            assert field in result, f"Missing field: {field}"
        
        if result['success']:
            assert result['confidence_score'] > 0
            assert result['international_format'] is not None
    
    def test_fallback_mechanism_integration(self, sample_phone_numbers):
        """Test fallback mechanism when enhanced investigation fails"""
        with patch('src.utils.enhanced_phone_investigation.EnhancedPhoneInvestigator') as mock_investigator:
            # Mock enhanced investigator to fail
            mock_investigator.return_value.investigate_phone_number.side_effect = Exception("Enhanced failed")
            
            # Should fallback to basic investigation
            result = get_enhanced_phone_info(sample_phone_numbers['valid_indian'], 'IN')
            
            # Should still get a result (from fallback)
            assert 'success' in result
            assert 'fallback_used' in result
            if 'fallback_used' in result:
                assert result['fallback_used'] is True
    
    def test_country_selection_integration(self, sample_phone_numbers):
        """Test country selection integration"""
        # Test with different countries
        countries = ['IN', 'US', 'UK', 'AU']
        
        for country in countries:
            result = get_enhanced_phone_info(sample_phone_numbers['valid_indian'], country)
            
            assert 'success' in result
            # Country context should be preserved
            if result.get('success'):
                assert result.get('selected_country') == country or result.get('detected_country')
    
    def test_batch_processing_integration(self, sample_phone_numbers):
        """Test batch processing integration"""
        investigator = EnhancedPhoneInvestigator()
        
        numbers = sample_phone_numbers['test_numbers'][:3]
        results = investigator.investigate_batch(numbers, 'IN')
        
        assert len(results) == len(numbers)
        
        # All results should have consistent structure
        for result in results:
            assert 'success' in result
            assert 'original_input' in result
            assert 'investigation_timestamp' in result
    
    @pytest.mark.asyncio
    async def test_async_workflow_integration(self, sample_phone_numbers):
        """Test asynchronous workflow integration"""
        from src.utils.async_intelligence_aggregator import investigate_phone_async
        
        result = await investigate_phone_async(
            sample_phone_numbers['valid_indian'], 'IN'
        )
        
        assert 'success' in result
        assert 'investigation_timestamp' in result
        
        # Async result should have same structure as sync
        sync_result = get_enhanced_phone_info(sample_phone_numbers['valid_indian'], 'IN')
        
        # Compare key fields
        key_fields = ['success', 'original_input', 'is_valid']
        for field in key_fields:
            if field in sync_result and field in result:
                assert type(sync_result[field]) == type(result[field])


@pytest.mark.integration
class TestDatabaseIntegration:
    """Integration tests for database operations"""
    
    def test_historical_data_persistence(self, temp_db_path, sample_investigation_results):
        """Test historical data persistence across sessions"""
        # First session
        manager1 = HistoricalDataManager(temp_db_path)
        manager1.store_investigation_data('9876543210', sample_investigation_results)
        
        # Second session (new instance)
        manager2 = HistoricalDataManager(temp_db_path)
        historical_data = manager2.get_historical_data('9876543210')
        
        assert len(historical_data) == 1
        assert historical_data[0]['phone_number'] == '9876543210'
    
    def test_cache_persistence(self, temp_db_path):
        """Test cache persistence across sessions"""
        from src.utils.performance_cache import PersistentCache
        
        # First session
        cache1 = PersistentCache(temp_db_path, ttl=3600)
        cache1.put('test_key', {'data': 'test_value'})
        
        # Second session
        cache2 = PersistentCache(temp_db_path, ttl=3600)
        result = cache2.get('test_key')
        
        assert result is not None
        assert result['data'] == 'test_value'
    
    def test_concurrent_database_access(self, temp_db_path, sample_investigation_results):
        """Test concurrent database access"""
        import threading
        
        manager = HistoricalDataManager(temp_db_path)
        results = []
        errors = []
        
        def store_data(phone_number):
            try:
                data = sample_investigation_results.copy()
                data['phone_number'] = phone_number
                manager.store_investigation_data(phone_number, data)
                results.append(phone_number)
            except Exception as e:
                errors.append(e)
        
        # Create multiple threads
        threads = []
        for i in range(10):
            phone = f"987654321{i}"
            thread = threading.Thread(target=store_data, args=(phone,))
            threads.append(thread)
        
        # Start all threads
        for thread in threads:
            thread.start()
        
        # Wait for completion
        for thread in threads:
            thread.join()
        
        # Verify results
        assert len(errors) == 0, f"Database errors: {errors}"
        assert len(results) == 10
        
        # Verify all data was stored
        for i in range(10):
            phone = f"987654321{i}"
            historical_data = manager.get_historical_data(phone)
            assert len(historical_data) == 1


@pytest.mark.integration
@pytest.mark.slow
class TestPerformanceIntegration:
    """Integration tests for performance requirements"""
    
    def test_response_time_integration(self, sample_phone_numbers, performance_test_config):
        """Test response time meets requirements"""
        investigator = EnhancedPhoneInvestigator()
        
        start_time = time.time()
        result = investigator.investigate_phone_number(
            sample_phone_numbers['valid_indian'], 'IN'
        )
        end_time = time.time()
        
        response_time = end_time - start_time
        
        assert response_time < performance_test_config['max_response_time']
        assert result['success'] is not None  # Ensure we got a result
    
    def test_concurrent_investigations_integration(self, sample_phone_numbers, performance_test_config):
        """Test concurrent investigations performance"""
        import threading
        
        investigator = EnhancedPhoneInvestigator()
        results = []
        start_time = time.time()
        
        def investigate():
            result = investigator.investigate_phone_number(
                sample_phone_numbers['valid_indian'], 'IN'
            )
            results.append(result)
        
        # Create concurrent threads
        threads = []
        for _ in range(performance_test_config['concurrent_requests']):
            thread = threading.Thread(target=investigate)
            threads.append(thread)
        
        # Start all threads
        for thread in threads:
            thread.start()
        
        # Wait for completion
        for thread in threads:
            thread.join()
        
        end_time = time.time()
        total_time = end_time - start_time
        
        # Verify performance
        assert len(results) == performance_test_config['concurrent_requests']
        assert total_time < performance_test_config['max_response_time'] * 2  # Allow some overhead
    
    def test_memory_usage_integration(self, sample_phone_numbers):
        """Test memory usage during investigations"""
        import psutil
        import os
        
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        investigator = EnhancedPhoneInvestigator()
        
        # Perform multiple investigations
        for _ in range(50):
            investigator.investigate_phone_number(
                sample_phone_numbers['valid_indian'], 'IN'
            )
        
        final_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_increase = final_memory - initial_memory
        
        # Memory increase should be reasonable
        assert memory_increase < 100  # Less than 100MB increase


if __name__ == '__main__':
    pytest.main([__file__, '-v'])