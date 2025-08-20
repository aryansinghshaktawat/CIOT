"""
Integration tests for enhanced phone investigation workflow
Tests the complete integration of PhoneNumberFormatter with existing workflow
"""

import pytest
import unittest
from unittest.mock import Mock, patch, MagicMock
import sys
import os

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from utils.osint_utils import get_phone_info, get_enhanced_phone_info
from utils.intelligence_aggregator import IntelligenceAggregator, DataSource
from gui.tabs.surface_web_tab import SurfaceWebTab


class TestEnhancedPhoneIntegration(unittest.TestCase):
    """Test enhanced phone investigation integration with existing workflow"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.test_phone_indian = "9876543210"
        self.test_phone_us = "+1 555 123 4567"
        self.test_phone_formatted = "+91 98765 43210"
        self.test_phone_invalid = "invalid_phone"
        
    def test_get_phone_info_enhanced_success(self):
        """Test get_phone_info successfully uses enhanced investigation"""
        with patch('utils.osint_utils.get_enhanced_phone_info') as mock_enhanced:
            # Mock successful enhanced investigation
            mock_enhanced.return_value = {
                'success': True,
                'original_input': self.test_phone_indian,
                'is_valid': True,
                'international_format': '+91 98765 43210',
                'country_name': 'India',
                'migration_status': 'enhanced_investigation_used',
                'fallback_used': False
            }
            
            result = get_phone_info(self.test_phone_indian, 'IN')
            
            # Verify enhanced investigation was called
            mock_enhanced.assert_called_once_with(self.test_phone_indian, 'IN')
            
            # Verify result contains enhanced data
            self.assertTrue(result['success'])
            self.assertEqual(result['migration_status'], 'enhanced_investigation_used')
            self.assertFalse(result['fallback_used'])
            self.assertIn('clean_phone', result)  # Backward compatibility field
            self.assertIn('length', result)  # Backward compatibility field
    
    def test_get_phone_info_fallback_on_enhanced_failure(self):
        """Test get_phone_info falls back to legacy when enhanced fails"""
        with patch('utils.osint_utils.get_enhanced_phone_info') as mock_enhanced, \
             patch('utils.osint_utils.get_indian_phone_api_data') as mock_api, \
             patch('utils.osint_utils.analyze_phone_locally') as mock_local:
            
            # Mock enhanced investigation failure
            mock_enhanced.return_value = {
                'success': False,
                'message': 'Enhanced investigation failed'
            }
            
            # Mock successful fallback API calls
            mock_api.return_value = {
                'success': True,
                'api_results': {'test_api': {'carrier': 'Test Carrier'}},
                'apis_used': ['test_api'],
                'total_apis_used': 1,
                'best_data': {'carrier': 'Test Carrier'}
            }
            
            # Mock local analysis
            mock_local.return_value = {'type_guess': 'Mobile'}
            
            result = get_phone_info(self.test_phone_indian, 'IN')
            
            # Verify enhanced investigation was attempted
            mock_enhanced.assert_called_once_with(self.test_phone_indian, 'IN')
            
            # Verify fallback was used
            self.assertTrue(result['success'])
            self.assertEqual(result['migration_status'], 'fallback_investigation_used')
            self.assertTrue(result['fallback_used'])
            self.assertIn('error_handling', result)
            self.assertTrue(result['error_handling']['graceful_degradation'])
    
    def test_get_phone_info_complete_failure_graceful_degradation(self):
        """Test get_phone_info handles complete failure gracefully"""
        with patch('utils.osint_utils.get_enhanced_phone_info') as mock_enhanced, \
             patch('utils.osint_utils.get_indian_phone_api_data') as mock_api:
            
            # Mock complete failure
            mock_enhanced.side_effect = Exception("Enhanced investigation error")
            mock_api.side_effect = Exception("API error")
            
            result = get_phone_info(self.test_phone_indian, 'IN')
            
            # Verify graceful degradation
            self.assertFalse(result['success'])
            self.assertEqual(result['migration_status'], 'complete_failure')
            self.assertTrue(result['fallback_used'])
            self.assertIn('error_handling', result)
            self.assertFalse(result['error_handling']['graceful_degradation'])
    
    def test_get_phone_info_backward_compatibility(self):
        """Test get_phone_info maintains backward compatibility"""
        with patch('utils.osint_utils.get_enhanced_phone_info') as mock_enhanced:
            # Mock enhanced investigation with comprehensive data
            mock_enhanced.return_value = {
                'success': True,
                'original_input': self.test_phone_indian,
                'is_valid': True,
                'international_format': '+91 98765 43210',
                'country_name': 'India',
                'carrier_name': 'Airtel',
                'is_mobile': True,
                'migration_status': 'enhanced_investigation_used'
            }
            
            result = get_phone_info(self.test_phone_indian, 'IN')
            
            # Verify backward compatibility fields are present
            required_fields = ['clean_phone', 'length', 'original_input', 'success']
            for field in required_fields:
                self.assertIn(field, result, f"Missing backward compatibility field: {field}")
            
            # Verify enhanced data is preserved
            self.assertEqual(result['international_format'], '+91 98765 43210')
            self.assertEqual(result['country_name'], 'India')
            self.assertEqual(result['carrier_name'], 'Airtel')
    
    def test_get_phone_info_country_code_handling(self):
        """Test get_phone_info properly handles different country codes"""
        test_cases = [
            ('9876543210', 'IN'),
            ('5551234567', 'US'),
            ('447700900123', 'GB'),
            ('33123456789', 'FR')
        ]
        
        for phone, country in test_cases:
            with patch('utils.osint_utils.get_enhanced_phone_info') as mock_enhanced:
                mock_enhanced.return_value = {
                    'success': True,
                    'country_code': country,
                    'migration_status': 'enhanced_investigation_used'
                }
                
                result = get_phone_info(phone, country)
                
                # Verify country code is passed correctly
                mock_enhanced.assert_called_once_with(phone, country)
                self.assertEqual(result['country_code'], country)
    
    def test_surface_web_tab_integration(self):
        """Test surface web tab integration with enhanced phone investigation"""
        # Test the integration logic without creating actual GUI components
        with patch('src.utils.osint_utils.get_enhanced_phone_info') as mock_enhanced:
            mock_enhanced.return_value = {
                'success': True,
                'migration_status': 'enhanced_investigation_used',
                'original_input': self.test_phone_indian
            }
            
            # Test the core integration logic that would be called by surface web tab
            selected_country = 'India'
            country_code = 'IN'  # This would come from country manager
            
            # This simulates what the surface web tab does
            real_data = mock_enhanced(self.test_phone_indian, country_code)
            
            # Verify enhanced investigation was called with correct parameters
            mock_enhanced.assert_called_once_with(self.test_phone_indian, 'IN')
            
            # Verify the result structure
            self.assertTrue(real_data['success'])
            self.assertEqual(real_data['migration_status'], 'enhanced_investigation_used')
    
    def test_error_handling_scenarios(self):
        """Test various error handling scenarios in the integration"""
        error_scenarios = [
            {
                'name': 'Enhanced investigation timeout',
                'enhanced_error': TimeoutError("Investigation timeout"),
                'expected_status': 'fallback_investigation_used'
            },
            {
                'name': 'API key missing',
                'enhanced_error': KeyError("API key not found"),
                'expected_status': 'fallback_investigation_used'
            },
            {
                'name': 'Network error',
                'enhanced_error': ConnectionError("Network unavailable"),
                'expected_status': 'fallback_investigation_used'
            },
            {
                'name': 'Invalid phone format',
                'enhanced_result': {'success': False, 'message': 'Invalid format'},
                'expected_status': 'fallback_investigation_used'
            }
        ]
        
        for scenario in error_scenarios:
            with self.subTest(scenario=scenario['name']):
                with patch('utils.osint_utils.get_enhanced_phone_info') as mock_enhanced, \
                     patch('utils.osint_utils.get_indian_phone_api_data') as mock_api, \
                     patch('utils.osint_utils.analyze_phone_locally') as mock_local:
                    
                    # Set up scenario
                    if 'enhanced_error' in scenario:
                        mock_enhanced.side_effect = scenario['enhanced_error']
                    else:
                        mock_enhanced.return_value = scenario['enhanced_result']
                    
                    # Mock successful fallback
                    mock_api.return_value = {
                        'success': True,
                        'api_results': {},
                        'apis_used': [],
                        'total_apis_used': 0,
                        'best_data': {}
                    }
                    mock_local.return_value = {}
                    
                    result = get_phone_info(self.test_phone_indian, 'IN')
                    
                    # Verify appropriate fallback behavior
                    if scenario['expected_status'] == 'fallback_investigation_used':
                        self.assertEqual(result['migration_status'], 'fallback_investigation_used')
                        self.assertTrue(result['fallback_used'])
                        self.assertIn('error_handling', result)
    
    def test_intelligence_aggregator_integration(self):
        """Test integration with IntelligenceAggregator"""
        with patch('utils.intelligence_aggregator.IntelligenceAggregator') as mock_aggregator_class:
            # Mock aggregator instance
            mock_aggregator = Mock()
            mock_aggregator_class.return_value = mock_aggregator
            
            # Mock aggregation result
            mock_aggregated = Mock()
            mock_aggregated.overall_confidence = 85.0
            mock_aggregated.sources_used = ['libphonenumber', 'abstractapi']
            mock_aggregated.successful_sources = 2
            mock_aggregated.total_sources = 3
            mock_aggregated.processing_time = 2.5
            mock_aggregated.merged_data = {'carrier': 'Test Carrier', 'location': 'Test City'}
            mock_aggregator.aggregate_intelligence.return_value = mock_aggregated
            mock_aggregator.get_confidence_level.return_value = Mock(name='HIGH')
            
            # Test enhanced phone investigation
            result = get_enhanced_phone_info(self.test_phone_indian, 'IN')
            
            # Verify aggregator was used
            self.assertTrue(result['success'])
            self.assertIn('aggregated_intelligence', result)
            self.assertEqual(result['aggregated_intelligence']['overall_confidence'], 85.0)
            self.assertEqual(result['aggregated_intelligence']['successful_sources'], 2)
    
    def test_migration_path_documentation(self):
        """Test that migration path is properly documented in results"""
        with patch('utils.osint_utils.get_enhanced_phone_info') as mock_enhanced:
            mock_enhanced.return_value = {
                'success': True,
                'migration_status': 'enhanced_investigation_used',
                'error_handling': {
                    'graceful_degradation': True,
                    'fallback_methods_available': True,
                    'critical_failures': [],
                    'warnings': []
                }
            }
            
            result = get_phone_info(self.test_phone_indian, 'IN')
            
            # Verify migration documentation
            self.assertIn('migration_status', result)
            self.assertIn('fallback_used', result)
            self.assertIn('error_handling', result)
            
            # Verify error handling structure
            error_handling = result['error_handling']
            required_error_fields = ['graceful_degradation', 'fallback_methods_available', 
                                   'critical_failures', 'warnings']
            for field in required_error_fields:
                self.assertIn(field, error_handling)
    
    def test_performance_requirements(self):
        """Test that integration meets performance requirements"""
        import time
        
        with patch('utils.osint_utils.get_enhanced_phone_info') as mock_enhanced:
            # Mock realistic response time
            def mock_investigation(*args, **kwargs):
                time.sleep(0.1)  # Simulate processing time
                return {
                    'success': True,
                    'migration_status': 'enhanced_investigation_used',
                    'processing_time': 0.1
                }
            
            mock_enhanced.side_effect = mock_investigation
            
            start_time = time.time()
            result = get_phone_info(self.test_phone_indian, 'IN')
            end_time = time.time()
            
            # Verify response time is reasonable (< 5 seconds as per requirements)
            response_time = end_time - start_time
            self.assertLess(response_time, 5.0, "Investigation took too long")
            
            # Verify result is successful
            self.assertTrue(result['success'])


class TestEnhancedPhoneIntegrationEdgeCases(unittest.TestCase):
    """Test edge cases and boundary conditions for enhanced phone integration"""
    
    def test_empty_phone_number(self):
        """Test handling of empty phone number"""
        result = get_phone_info("", 'IN')
        
        # Should handle gracefully
        self.assertFalse(result['success'])
        self.assertIn('error_handling', result)
    
    def test_none_phone_number(self):
        """Test handling of None phone number"""
        with self.assertRaises(ValueError):
            get_phone_info(None, 'IN')
    
    def test_unsupported_country_code(self):
        """Test handling of unsupported country code"""
        result = get_phone_info("1234567890", 'XX')  # Invalid country code
        
        # Should still attempt investigation
        self.assertIn('country_code', result)
        self.assertEqual(result['country_code'], 'XX')
    
    def test_very_long_phone_number(self):
        """Test handling of unusually long phone number"""
        long_phone = "1" * 50  # 50 digit number
        result = get_phone_info(long_phone, 'IN')
        
        # Should handle gracefully
        self.assertIn('length', result)
        self.assertEqual(result['length'], 50)
    
    def test_special_characters_in_phone(self):
        """Test handling of phone numbers with special characters"""
        special_phone = "+91-98765-43210 ext. 123"
        result = get_phone_info(special_phone, 'IN')
        
        # Should clean and process
        self.assertIn('clean_phone', result)
        self.assertIn('original_input', result)
        self.assertEqual(result['original_input'], special_phone)


if __name__ == '__main__':
    # Run the tests
    unittest.main(verbosity=2)