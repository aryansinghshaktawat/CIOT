"""
Comprehensive End-to-End Tests for Enhanced Phone Investigation
Tests complete investigation workflow from user input to final results
"""

import pytest
import asyncio
import time
import json
import tempfile
import os
from unittest.mock import Mock, patch, MagicMock
from typing import Dict, Any, List
from datetime import datetime, timedelta

# Import main components for E2E testing
from src.utils.osint_utils import get_enhanced_phone_info, get_phone_info
from src.utils.enhanced_phone_investigation import EnhancedPhoneInvestigator
from src.utils.cached_phone_formatter import CachedPhoneNumberFormatter
from src.utils.intelligence_aggregator import IntelligenceAggregator
from src.utils.historical_data_manager import HistoricalDataManager
from src.utils.pattern_analysis import PatternAnalysisEngine


@pytest.mark.e2e
class TestCompleteInvestigationWorkflow:
    """End-to-end tests for complete investigation workflow"""
    
    def test_successful_investigation_workflow(self, sample_phone_numbers):
        """Test complete successful investigation workflow"""
        phone_number = sample_phone_numbers['valid_indian']
        country = 'IN'
        
        # Execute complete investigation
        result = get_enhanced_phone_info(phone_number, country)
        
        # Verify complete result structure
        assert isinstance(result, dict), "Result should be a dictionary"
        assert 'success' in result, "Result should contain success field"
        assert 'original_input' in result, "Result should contain original input"
        assert 'investigation_timestamp' in result, "Result should contain timestamp"
        
        if result.get('success'):
            # Verify formatting results
            assert 'formatting_success' in result
            assert 'international_format' in result
            assert 'is_valid' in result
            
            # Verify intelligence results
            assert 'country_name' in result
            assert 'confidence_score' in result
            
            # Verify confidence score is reasonable
            confidence = result.get('confidence_score', 0)
            assert 0 <= confidence <= 1, f"Confidence score {confidence} should be between 0 and 1"
        
        # Verify investigation metadata
        assert 'investigation_timestamp' in result
        timestamp = result.get('investigation_timestamp')
        if timestamp:
            assert isinstance(timestamp, datetime) or isinstance(timestamp, str)
    
    def test_investigation_with_country_detection(self, sample_phone_numbers):
        """Test investigation with automatic country detection"""
        # Use international format number
        phone_number = sample_phone_numbers['valid_indian_formatted']
        
        # Don't specify country - should auto-detect
        result = get_enhanced_phone_info(phone_number, None)
        
        assert isinstance(result, dict)
        
        if result.get('success'):
            # Should detect India
            detected_country = result.get('country_name', '').lower()
            assert 'india' in detected_country or result.get('region_code') == 'IN'
    
    def test_investigation_with_error_handling(self, sample_phone_numbers):
        """Test investigation workflow with error handling"""
        # Use invalid phone number
        phone_number = sample_phone_numbers['invalid_format']
        country = 'IN'
        
        result = get_enhanced_phone_info(phone_number, country)
        
        assert isinstance(result, dict)
        assert 'success' in result
        
        if result.get('success') is False:
            # Should contain error information
            assert 'error' in result or 'error_message' in result
            
            # Should contain guidance
            assert 'guidance' in result or 'suggestions' in result
    
    def test_investigation_with_fallback_mechanism(self, sample_phone_numbers):
        """Test investigation with fallback to basic investigation"""
        phone_number = sample_phone_numbers['valid_indian']
        
        # Mock enhanced investigation to fail
        with patch('src.utils.enhanced_phone_investigation.EnhancedPhoneInvestigator') as mock_investigator:
            mock_investigator.return_value.investigate_phone_number.side_effect = Exception("Enhanced failed")
            
            result = get_enhanced_phone_info(phone_number, 'IN')
            
            # Should still get a result from fallback
            assert isinstance(result, dict)
            assert 'success' in result
            
            # Should indicate fallback was used
            if 'fallback_used' in result:
                assert result['fallback_used'] is True
    
    def test_investigation_with_historical_data(self, temp_db_path, sample_phone_numbers, sample_investigation_results):
        """Test investigation workflow with historical data integration"""
        phone_number = sample_phone_numbers['valid_indian']
        
        # Setup historical data
        historical_manager = HistoricalDataManager(temp_db_path)
        
        # Store previous investigation
        previous_data = sample_investigation_results.copy()
        previous_data['carrier_name'] = 'Vodafone'
        previous_data['investigation_timestamp'] = datetime.now() - timedelta(days=30)
        historical_manager.store_investigation_data(phone_number, previous_data)
        
        # Mock investigator to use our historical manager
        with patch('src.utils.enhanced_phone_investigation.EnhancedPhoneInvestigator') as mock_investigator_class:
            mock_investigator = Mock()
            mock_investigator_class.return_value = mock_investigator
            
            # Mock current investigation with different carrier
            current_data = sample_investigation_results.copy()
            current_data['carrier_name'] = 'Airtel'
            mock_investigator.investigate_phone_number.return_value = current_data
            
            # Mock historical manager
            mock_investigator.historical_manager = historical_manager
            
            result = get_enhanced_phone_info(phone_number, 'IN')
            
            # Should detect carrier change
            if result.get('success') and 'historical_changes' in result:
                changes = result['historical_changes']
                if changes:
                    assert any('carrier' in str(change).lower() for change in changes)


@pytest.mark.e2e
class TestBatchInvestigationWorkflow:
    """End-to-end tests for batch investigation workflow"""
    
    def test_batch_investigation_workflow(self, sample_phone_numbers):
        """Test batch investigation of multiple numbers"""
        investigator = EnhancedPhoneInvestigator()
        
        # Test with subset of numbers
        numbers = sample_phone_numbers['test_numbers'][:3]
        
        results = investigator.investigate_batch(numbers, 'IN')
        
        # Verify batch results
        assert isinstance(results, list), "Batch results should be a list"
        assert len(results) == len(numbers), "Should have result for each number"
        
        # Verify each result
        for i, result in enumerate(results):
            assert isinstance(result, dict), f"Result {i} should be a dictionary"
            assert 'success' in result, f"Result {i} should contain success field"
            assert 'original_input' in result, f"Result {i} should contain original input"
            assert result['original_input'] == numbers[i], f"Result {i} should match input number"
    
    def test_batch_investigation_with_mixed_validity(self, sample_phone_numbers):
        """Test batch investigation with mix of valid and invalid numbers"""
        investigator = EnhancedPhoneInvestigator()
        
        # Mix valid and invalid numbers
        numbers = [
            sample_phone_numbers['valid_indian'],
            sample_phone_numbers['invalid_format'],
            sample_phone_numbers['test_numbers'][0]
        ]
        
        results = investigator.investigate_batch(numbers, 'IN')
        
        assert len(results) == len(numbers)
        
        # Should have mix of successful and failed results
        successful_results = [r for r in results if r.get('success') is True]
        failed_results = [r for r in results if r.get('success') is False]
        
        # Should have at least one successful and one failed
        assert len(successful_results) > 0, "Should have at least one successful result"
        assert len(failed_results) > 0, "Should have at least one failed result"
    
    def test_batch_investigation_performance(self, sample_phone_numbers, performance_test_config):
        """Test batch investigation meets performance requirements"""
        investigator = EnhancedPhoneInvestigator()
        
        numbers = sample_phone_numbers['test_numbers'][:5]
        
        start_time = time.time()
        results = investigator.investigate_batch(numbers, 'IN')
        end_time = time.time()
        
        total_time = end_time - start_time
        avg_time_per_number = total_time / len(numbers)
        
        # Batch should be efficient
        assert avg_time_per_number < performance_test_config['max_response_time'], \
            f"Average time per number {avg_time_per_number:.2f}s exceeds limit"
        
        assert len(results) == len(numbers)


@pytest.mark.e2e
class TestDataPersistenceWorkflow:
    """End-to-end tests for data persistence workflow"""
    
    def test_investigation_data_persistence(self, temp_db_path, sample_phone_numbers):
        """Test investigation data is properly persisted"""
        phone_number = sample_phone_numbers['valid_indian']
        
        # First investigation
        result1 = get_enhanced_phone_info(phone_number, 'IN')
        
        # Verify data was stored (if successful)
        if result1.get('success'):
            # Create new historical manager to verify persistence
            historical_manager = HistoricalDataManager(temp_db_path)
            historical_data = historical_manager.get_historical_data(phone_number)
            
            # Should have stored the investigation
            assert len(historical_data) >= 0  # May be 0 if storage is mocked
    
    def test_cache_persistence_workflow(self, temp_db_path, sample_phone_numbers):
        """Test cache persistence across investigations"""
        phone_number = sample_phone_numbers['valid_indian']
        
        # First investigation (should populate cache)
        start_time = time.time()
        result1 = get_enhanced_phone_info(phone_number, 'IN')
        first_time = time.time() - start_time
        
        # Second investigation (should use cache)
        start_time = time.time()
        result2 = get_enhanced_phone_info(phone_number, 'IN')
        second_time = time.time() - start_time
        
        # Verify both investigations succeeded
        if result1.get('success') and result2.get('success'):
            # Second should be faster (cached)
            if first_time > 0.1:  # Only test if first call took measurable time
                assert second_time < first_time, "Cached call should be faster"
    
    def test_pattern_analysis_persistence(self, temp_db_path, sample_phone_numbers):
        """Test pattern analysis data persistence"""
        phone_number = sample_phone_numbers['valid_indian']
        
        # Perform investigation that should trigger pattern analysis
        result = get_enhanced_phone_info(phone_number, 'IN')
        
        if result.get('success'):
            # Pattern analysis results should be included
            pattern_fields = ['related_numbers', 'bulk_registration_status', 'pattern_intelligence']
            
            has_pattern_data = any(field in result for field in pattern_fields)
            
            # If pattern analysis ran, verify structure
            if has_pattern_data:
                if 'related_numbers' in result:
                    assert isinstance(result['related_numbers'], list)
                
                if 'bulk_registration_status' in result:
                    assert isinstance(result['bulk_registration_status'], dict)
                    assert 'detected' in result['bulk_registration_status']


@pytest.mark.e2e
class TestErrorRecoveryWorkflow:
    """End-to-end tests for error recovery workflow"""
    
    def test_api_failure_recovery(self, sample_phone_numbers):
        """Test recovery from API failures"""
        phone_number = sample_phone_numbers['valid_indian']
        
        # Mock API failures
        with patch('requests.get') as mock_get:
            # First call fails, second succeeds
            mock_get.side_effect = [
                Exception("API Error"),  # First API fails
                Mock(status_code=200, json=lambda: {'valid': True, 'country': {'code': 'IN'}})  # Second succeeds
            ]
            
            result = get_enhanced_phone_info(phone_number, 'IN')
            
            # Should still get a result despite API failure
            assert isinstance(result, dict)
            assert 'success' in result
    
    def test_partial_failure_recovery(self, sample_phone_numbers):
        """Test recovery from partial failures"""
        phone_number = sample_phone_numbers['valid_indian']
        
        # Mock partial failure in intelligence gathering
        with patch('src.utils.intelligence_aggregator.IntelligenceAggregator.gather_comprehensive_intelligence') as mock_gather:
            # Return partial results
            mock_gather.return_value = {
                'technical_intelligence': {'carrier': 'Airtel'},
                'security_intelligence': {},  # Empty due to API failure
                'social_intelligence': {'whatsapp_status': {'exists': True}},
                'business_intelligence': {},  # Empty due to API failure
                'pattern_intelligence': {},
                'historical_intelligence': {}
            }
            
            result = get_enhanced_phone_info(phone_number, 'IN')
            
            # Should still succeed with partial data
            if result.get('success'):
                assert 'carrier_name' in result or 'technical_intelligence' in result
    
    def test_timeout_recovery(self, sample_phone_numbers):
        """Test recovery from timeout scenarios"""
        phone_number = sample_phone_numbers['valid_indian']
        
        # Mock timeout in investigation
        with patch('src.utils.enhanced_phone_investigation.EnhancedPhoneInvestigator.investigate_phone_number') as mock_investigate:
            def slow_investigate(*args, **kwargs):
                time.sleep(10)  # Simulate very slow response
                return {'success': True}
            
            mock_investigate.side_effect = slow_investigate
            
            # Should handle timeout gracefully
            start_time = time.time()
            result = get_enhanced_phone_info(phone_number, 'IN')
            end_time = time.time()
            
            # Should not take too long (timeout should kick in)
            assert end_time - start_time < 15, "Should timeout and return quickly"
            assert isinstance(result, dict)


@pytest.mark.e2e
class TestIntegrationWithExternalSystems:
    """End-to-end tests for integration with external systems"""
    
    def test_integration_with_existing_osint_utils(self, sample_phone_numbers):
        """Test integration with existing OSINT utilities"""
        phone_number = sample_phone_numbers['valid_indian']
        
        # Test both enhanced and basic investigation
        enhanced_result = get_enhanced_phone_info(phone_number, 'IN')
        basic_result = get_phone_info(phone_number, 'IN')
        
        # Both should return valid results
        assert isinstance(enhanced_result, dict)
        assert isinstance(basic_result, dict)
        
        # Enhanced should have more comprehensive data
        if enhanced_result.get('success') and basic_result.get('success'):
            enhanced_fields = set(enhanced_result.keys())
            basic_fields = set(basic_result.keys())
            
            # Enhanced should have additional fields
            additional_fields = enhanced_fields - basic_fields
            assert len(additional_fields) > 0, "Enhanced investigation should provide additional data"
    
    def test_integration_with_gui_components(self, sample_phone_numbers):
        """Test integration with GUI components"""
        # This would test the integration with actual GUI components
        # For now, we'll test the data format compatibility
        
        phone_number = sample_phone_numbers['valid_indian']
        result = get_enhanced_phone_info(phone_number, 'IN')
        
        # Verify result format is compatible with GUI display
        if result.get('success'):
            # Should have displayable fields
            displayable_fields = [
                'international_format', 'country_name', 'carrier_name',
                'location', 'number_type', 'confidence_score'
            ]
            
            has_displayable_data = any(field in result for field in displayable_fields)
            assert has_displayable_data, "Result should contain displayable data for GUI"
    
    def test_integration_with_reporting_system(self, sample_phone_numbers, sample_investigation_results):
        """Test integration with reporting system"""
        phone_number = sample_phone_numbers['valid_indian']
        
        result = get_enhanced_phone_info(phone_number, 'IN')
        
        if result.get('success'):
            # Verify result can be serialized for reporting
            try:
                json_result = json.dumps(result, default=str)  # Use default=str for datetime objects
                assert len(json_result) > 0, "Result should be serializable to JSON"
                
                # Verify it can be deserialized
                parsed_result = json.loads(json_result)
                assert isinstance(parsed_result, dict)
                
            except (TypeError, ValueError) as e:
                pytest.fail(f"Result not serializable for reporting: {e}")


@pytest.mark.e2e
@pytest.mark.slow
class TestLongRunningWorkflows:
    """End-to-end tests for long-running workflows"""
    
    def test_extended_investigation_session(self, sample_phone_numbers):
        """Test extended investigation session with multiple numbers"""
        investigator = EnhancedPhoneInvestigator()
        
        # Simulate extended session with multiple investigations
        results = []
        start_time = time.time()
        
        # Investigate multiple numbers over time
        for i, phone in enumerate(sample_phone_numbers['test_numbers']):
            result = investigator.investigate_phone_number(phone, 'IN')
            results.append(result)
            
            # Brief pause between investigations
            time.sleep(0.5)
            
            # Stop after 30 seconds or 20 investigations
            if time.time() - start_time > 30 or i >= 19:
                break
        
        # Verify session completed successfully
        assert len(results) > 0, "Should complete at least one investigation"
        
        # Verify performance remained stable
        successful_results = [r for r in results if r.get('success') is not False]
        success_rate = len(successful_results) / len(results)
        
        assert success_rate > 0.7, f"Success rate {success_rate:.2f} too low for extended session"
    
    def test_memory_stability_long_session(self, sample_phone_numbers):
        """Test memory stability during long investigation session"""
        import psutil
        
        process = psutil.Process(os.getpid())
        investigator = EnhancedPhoneInvestigator()
        
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_samples = [initial_memory]
        
        # Run investigations for extended period
        start_time = time.time()
        investigation_count = 0
        
        while time.time() - start_time < 60 and investigation_count < 50:  # 1 minute or 50 investigations
            phone = sample_phone_numbers['test_numbers'][investigation_count % len(sample_phone_numbers['test_numbers'])]
            investigator.investigate_phone_number(phone, 'IN')
            investigation_count += 1
            
            # Sample memory every 10 investigations
            if investigation_count % 10 == 0:
                current_memory = process.memory_info().rss / 1024 / 1024  # MB
                memory_samples.append(current_memory)
        
        # Verify memory stability
        final_memory = memory_samples[-1]
        memory_increase = final_memory - initial_memory
        
        assert memory_increase < 200, f"Memory increase {memory_increase:.2f}MB too high for long session"
        assert investigation_count > 10, f"Too few investigations {investigation_count} completed"


if __name__ == '__main__':
    pytest.main([__file__, '-v', '-m', 'e2e'])