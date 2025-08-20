"""
Unit tests for Intelligence Aggregator
Tests multi-source intelligence coordination, confidence scoring, and data merging
"""

import unittest
import sys
import os
from unittest.mock import Mock, patch, MagicMock
import time

# Add src directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from utils.intelligence_aggregator import (
    IntelligenceAggregator, 
    DataSource, 
    ConfidenceLevel, 
    IntelligenceResult, 
    AggregatedIntelligence
)


class TestIntelligenceResult(unittest.TestCase):
    """Test cases for IntelligenceResult dataclass"""
    
    def test_intelligence_result_creation(self):
        """Test IntelligenceResult creation and validation"""
        result = IntelligenceResult(
            source=DataSource.LIBPHONENUMBER,
            data={'is_valid': True, 'country': 'India'},
            confidence=85.0,
            timestamp=time.time(),
            success=True
        )
        
        self.assertEqual(result.source, DataSource.LIBPHONENUMBER)
        self.assertTrue(result.success)
        self.assertEqual(result.confidence, 85.0)
        self.assertIsNone(result.error)
    
    def test_confidence_validation(self):
        """Test confidence score validation"""
        # Valid confidence scores
        for confidence in [0, 50, 100]:
            result = IntelligenceResult(
                source=DataSource.ABSTRACTAPI,
                data={},
                confidence=confidence,
                timestamp=time.time(),
                success=True
            )
            self.assertEqual(result.confidence, confidence)
        
        # Invalid confidence scores
        for invalid_confidence in [-10, 150]:
            with self.assertRaises(ValueError):
                IntelligenceResult(
                    source=DataSource.ABSTRACTAPI,
                    data={},
                    confidence=invalid_confidence,
                    timestamp=time.time(),
                    success=True
                )


class TestIntelligenceAggregator(unittest.TestCase):
    """Test cases for IntelligenceAggregator class"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.aggregator = IntelligenceAggregator()
        self.test_phone = '+919876543210'
        self.test_country = 'IN'
    
    def test_initialization(self):
        """Test IntelligenceAggregator initialization"""
        self.assertIsInstance(self.aggregator, IntelligenceAggregator)
        self.assertIn(DataSource.LIBPHONENUMBER, self.aggregator.source_weights)
        self.assertIn('is_valid', self.aggregator.field_priorities)
        self.assertIn(DataSource.ABSTRACTAPI, self.aggregator.source_timeouts)
    
    def test_confidence_level_mapping(self):
        """Test confidence level enum mapping"""
        test_cases = [
            (98, ConfidenceLevel.CRITICAL),
            (85, ConfidenceLevel.HIGH),
            (65, ConfidenceLevel.MEDIUM),
            (45, ConfidenceLevel.LOW),
            (25, ConfidenceLevel.VERY_LOW),
            (10, ConfidenceLevel.UNRELIABLE)
        ]
        
        for confidence, expected_level in test_cases:
            level = self.aggregator.get_confidence_level(confidence)
            self.assertEqual(level, expected_level)
    
    @patch('src.utils.intelligence_aggregator.phonenumbers')
    def test_query_libphonenumber_success(self, mock_phonenumbers):
        """Test successful libphonenumber query"""
        # Mock phonenumbers responses
        mock_parsed = Mock()
        mock_parsed.country_code = 91
        mock_parsed.national_number = 9876543210
        
        mock_phonenumbers.parse.return_value = mock_parsed
        mock_phonenumbers.is_valid_number.return_value = True
        mock_phonenumbers.is_possible_number.return_value = True
        mock_phonenumbers.format_number.return_value = '+91 98765 43210'
        mock_phonenumbers.number_type.return_value.name = 'MOBILE'
        mock_phonenumbers.region_code_for_number.return_value = 'IN'
        
        # Mock geocoder and carrier
        with patch('src.utils.intelligence_aggregator.geocoder') as mock_geocoder, \
             patch('src.utils.intelligence_aggregator.carrier') as mock_carrier, \
             patch('src.utils.intelligence_aggregator.timezone') as mock_timezone:
            
            mock_geocoder.description_for_number.return_value = 'India'
            mock_carrier.name_for_number.return_value = 'Airtel'
            mock_timezone.time_zones_for_number.return_value = ['Asia/Kolkata']
            
            data, confidence = self.aggregator._query_libphonenumber(self.test_phone, self.test_country)
            
            self.assertIsInstance(data, dict)
            self.assertTrue(data['is_valid'])
            self.assertEqual(data['country'], 'India')
            self.assertEqual(data['carrier'], 'Airtel')
            self.assertGreaterEqual(confidence, 85.0)
    
    @patch('src.utils.intelligence_aggregator.phonenumbers')
    def test_query_libphonenumber_invalid(self, mock_phonenumbers):
        """Test libphonenumber query with invalid number"""
        mock_parsed = Mock()
        mock_phonenumbers.parse.return_value = mock_parsed
        mock_phonenumbers.is_valid_number.return_value = False
        
        data, confidence = self.aggregator._query_libphonenumber('invalid', self.test_country)
        
        self.assertIsInstance(data, dict)
        self.assertEqual(confidence, 20.0)  # Low confidence for invalid numbers
    
    @patch('requests.get')
    @patch('src.utils.osint_utils.load_api_keys')
    def test_query_abstractapi_success(self, mock_load_keys, mock_get):
        """Test successful AbstractAPI query"""
        # Mock API keys
        mock_load_keys.return_value = {
            'abstractapi': {'api_key': 'test_key'}
        }
        
        # Mock successful API response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'valid': True,
            'country': {'code': 'IN', 'name': 'India'},
            'carrier': 'Airtel',
            'type': 'mobile'
        }
        mock_get.return_value = mock_response
        
        data, confidence = self.aggregator._query_abstractapi(self.test_phone, 10.0)
        
        self.assertIsInstance(data, dict)
        self.assertTrue(data['valid'])
        self.assertGreaterEqual(confidence, 85.0)
    
    @patch('requests.get')
    @patch('src.utils.osint_utils.load_api_keys')
    def test_query_abstractapi_no_key(self, mock_load_keys, mock_get):
        """Test AbstractAPI query without API key"""
        mock_load_keys.return_value = {}
        
        data, confidence = self.aggregator._query_abstractapi(self.test_phone, 10.0)
        
        self.assertIn('error', data)
        self.assertEqual(confidence, 0.0)
    
    @patch('requests.post')
    @patch('src.utils.osint_utils.load_api_keys')
    def test_query_neutrino_success(self, mock_load_keys, mock_post):
        """Test successful Neutrino API query"""
        # Mock API keys
        mock_load_keys.return_value = {
            'neutrino': {'user_id': 'test_user', 'api_key': 'test_key'}
        }
        
        # Mock successful API response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'valid': True,
            'country-code': 'IN',
            'prefix-network': 'Airtel',
            'type': 'mobile'
        }
        mock_post.return_value = mock_response
        
        data, confidence = self.aggregator._query_neutrino(self.test_phone, self.test_country, 10.0)
        
        self.assertIsInstance(data, dict)
        self.assertTrue(data['valid'])
        self.assertGreaterEqual(confidence, 80.0)
    
    def test_merge_intelligence_data_empty(self):
        """Test data merging with empty results"""
        results = []
        merged = self.aggregator._merge_intelligence_data(results)
        self.assertEqual(merged, {})
    
    def test_merge_intelligence_data_single_source(self):
        """Test data merging with single source"""
        result = IntelligenceResult(
            source=DataSource.LIBPHONENUMBER,
            data={'is_valid': True, 'country': 'India', 'carrier': 'Airtel'},
            confidence=90.0,
            timestamp=time.time(),
            success=True
        )
        
        merged = self.aggregator._merge_intelligence_data([result])
        
        self.assertTrue(merged['is_valid'])
        self.assertEqual(merged['country'], 'India')
        self.assertEqual(merged['carrier'], 'Airtel')
        self.assertIn('is_valid_confidence', merged)
        self.assertIn('is_valid_source', merged)
    
    def test_merge_intelligence_data_multiple_sources(self):
        """Test data merging with multiple sources"""
        results = [
            IntelligenceResult(
                source=DataSource.LIBPHONENUMBER,
                data={'is_valid': True, 'country': 'India', 'carrier': 'Unknown'},
                confidence=95.0,
                timestamp=time.time(),
                success=True
            ),
            IntelligenceResult(
                source=DataSource.NEUTRINO,
                data={'is_valid': True, 'country': 'India', 'carrier': 'Airtel'},
                confidence=80.0,
                timestamp=time.time(),
                success=True
            ),
            IntelligenceResult(
                source=DataSource.ABSTRACTAPI,
                data={'is_valid': True, 'country': 'India', 'carrier': 'Jio'},
                confidence=85.0,
                timestamp=time.time(),
                success=True
            )
        ]
        
        merged = self.aggregator._merge_intelligence_data(results)
        
        # Should prefer libphonenumber for is_valid (highest priority)
        self.assertTrue(merged['is_valid'])
        self.assertEqual(merged['is_valid_source'], 'libphonenumber')
        
        # Should prefer the highest confidence carrier value
        # Since libphonenumber has highest weight and confidence, it should win even with 'Unknown'
        # But let's check what actually gets selected
        self.assertIn('carrier', merged)
        self.assertIn('carrier_source', merged)
        
        # Should have alternatives for critical fields
        self.assertIn('carrier_alternatives', merged)
    
    def test_calculate_overall_confidence_empty(self):
        """Test confidence calculation with empty results"""
        confidence = self.aggregator._calculate_overall_confidence([])
        self.assertEqual(confidence, 0.0)
    
    def test_calculate_overall_confidence_single_success(self):
        """Test confidence calculation with single successful result"""
        result = IntelligenceResult(
            source=DataSource.LIBPHONENUMBER,
            data={'is_valid': True},
            confidence=90.0,
            timestamp=time.time(),
            success=True
        )
        
        confidence = self.aggregator._calculate_overall_confidence([result])
        
        # Should be penalized for single source but still reasonable
        self.assertGreater(confidence, 70.0)
        self.assertLess(confidence, 90.0)
    
    def test_calculate_overall_confidence_multiple_success(self):
        """Test confidence calculation with multiple successful results"""
        results = [
            IntelligenceResult(
                source=DataSource.LIBPHONENUMBER,
                data={'is_valid': True},
                confidence=95.0,
                timestamp=time.time(),
                success=True
            ),
            IntelligenceResult(
                source=DataSource.ABSTRACTAPI,
                data={'is_valid': True},
                confidence=85.0,
                timestamp=time.time(),
                success=True
            ),
            IntelligenceResult(
                source=DataSource.NEUTRINO,
                data={'is_valid': True},
                confidence=80.0,
                timestamp=time.time(),
                success=True
            )
        ]
        
        confidence = self.aggregator._calculate_overall_confidence(results)
        
        # Should be high with multiple successful sources
        self.assertGreater(confidence, 85.0)
    
    def test_calculate_overall_confidence_mixed_results(self):
        """Test confidence calculation with mixed success/failure results"""
        results = [
            IntelligenceResult(
                source=DataSource.LIBPHONENUMBER,
                data={'is_valid': True},
                confidence=95.0,
                timestamp=time.time(),
                success=True
            ),
            IntelligenceResult(
                source=DataSource.ABSTRACTAPI,
                data={},
                confidence=0.0,
                timestamp=time.time(),
                success=False,
                error='API key invalid'
            ),
            IntelligenceResult(
                source=DataSource.NEUTRINO,
                data={'is_valid': True},
                confidence=80.0,
                timestamp=time.time(),
                success=True
            )
        ]
        
        confidence = self.aggregator._calculate_overall_confidence(results)
        
        # Should be reduced due to failures but still reasonable
        self.assertGreater(confidence, 70.0)
        self.assertLess(confidence, 95.0)
    
    @patch.object(IntelligenceAggregator, '_query_source')
    def test_aggregate_intelligence_success(self, mock_query):
        """Test successful intelligence aggregation"""
        # Mock successful source queries
        mock_results = [
            IntelligenceResult(
                source=DataSource.LIBPHONENUMBER,
                data={'is_valid': True, 'country': 'India'},
                confidence=95.0,
                timestamp=time.time(),
                success=True
            ),
            IntelligenceResult(
                source=DataSource.ABSTRACTAPI,
                data={'valid': True, 'carrier': 'Airtel'},
                confidence=85.0,
                timestamp=time.time(),
                success=True
            )
        ]
        
        mock_query.side_effect = mock_results
        
        sources = [DataSource.LIBPHONENUMBER, DataSource.ABSTRACTAPI]
        aggregated = self.aggregator.aggregate_intelligence(
            self.test_phone, self.test_country, sources
        )
        
        self.assertIsInstance(aggregated, AggregatedIntelligence)
        self.assertEqual(aggregated.phone_number, self.test_phone)
        self.assertEqual(aggregated.country_code, self.test_country)
        self.assertEqual(aggregated.total_sources, 2)
        self.assertEqual(aggregated.successful_sources, 2)
        self.assertGreater(aggregated.overall_confidence, 80.0)
        self.assertEqual(len(aggregated.results), 2)
        self.assertGreater(len(aggregated.merged_data), 0)
    
    @patch.object(IntelligenceAggregator, '_query_source')
    def test_aggregate_intelligence_with_failures(self, mock_query):
        """Test intelligence aggregation with some source failures"""
        # Mock mixed results
        mock_results = [
            IntelligenceResult(
                source=DataSource.LIBPHONENUMBER,
                data={'is_valid': True, 'country': 'India'},
                confidence=95.0,
                timestamp=time.time(),
                success=True
            ),
            IntelligenceResult(
                source=DataSource.ABSTRACTAPI,
                data={},
                confidence=0.0,
                timestamp=time.time(),
                success=False,
                error='API timeout'
            )
        ]
        
        mock_query.side_effect = mock_results
        
        sources = [DataSource.LIBPHONENUMBER, DataSource.ABSTRACTAPI]
        aggregated = self.aggregator.aggregate_intelligence(
            self.test_phone, self.test_country, sources
        )
        
        self.assertEqual(aggregated.total_sources, 2)
        self.assertEqual(aggregated.successful_sources, 1)
        self.assertEqual(len(aggregated.errors), 1)
        self.assertIn('abstractapi: API timeout', aggregated.errors[0])
    
    def test_generate_intelligence_report(self):
        """Test intelligence report generation"""
        # Create mock aggregated intelligence
        results = [
            IntelligenceResult(
                source=DataSource.LIBPHONENUMBER,
                data={'is_valid': True, 'country': 'India'},
                confidence=95.0,
                timestamp=time.time(),
                success=True,
                response_time=0.1
            ),
            IntelligenceResult(
                source=DataSource.ABSTRACTAPI,
                data={'valid': True, 'carrier': 'Airtel'},
                confidence=85.0,
                timestamp=time.time(),
                success=True,
                response_time=2.5
            )
        ]
        
        aggregated = AggregatedIntelligence(
            phone_number=self.test_phone,
            country_code=self.test_country,
            results=results,
            merged_data={'is_valid': True, 'country': 'India', 'carrier': 'Airtel'},
            overall_confidence=90.0,
            sources_used=['libphonenumber', 'abstractapi'],
            total_sources=2,
            successful_sources=2,
            processing_time=3.0
        )
        
        report = self.aggregator.generate_intelligence_report(aggregated)
        
        self.assertIsInstance(report, str)
        self.assertIn('MULTI-SOURCE INTELLIGENCE REPORT', report)
        self.assertIn(self.test_phone, report)
        self.assertIn('90.0%', report)
        self.assertIn('SUCCESS', report)
        self.assertIn('libphonenumber', report)
        self.assertIn('abstractapi', report)


class TestIntelligenceAggregatorIntegration(unittest.TestCase):
    """Integration tests for IntelligenceAggregator"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.aggregator = IntelligenceAggregator()
    
    def test_source_priority_system(self):
        """Test that source priority system works correctly"""
        # Test field priorities
        self.assertIn(DataSource.LIBPHONENUMBER, self.aggregator.field_priorities['is_valid'])
        self.assertIn(DataSource.NEUTRINO, self.aggregator.field_priorities['carrier'])
        
        # Test source weights
        self.assertGreater(
            self.aggregator.source_weights[DataSource.LIBPHONENUMBER],
            self.aggregator.source_weights[DataSource.FINDANDTRACE]
        )
    
    def test_timeout_configuration(self):
        """Test that timeout configuration is reasonable"""
        # Local processing should be fast
        self.assertLess(
            self.aggregator.source_timeouts[DataSource.LIBPHONENUMBER],
            self.aggregator.source_timeouts[DataSource.ABSTRACTAPI]
        )
        
        # Web scraping should have longer timeout
        self.assertGreater(
            self.aggregator.source_timeouts[DataSource.FINDANDTRACE],
            self.aggregator.source_timeouts[DataSource.ABSTRACTAPI]
        )
    
    def test_confidence_level_boundaries(self):
        """Test confidence level boundary conditions"""
        boundary_tests = [
            (94.9, ConfidenceLevel.HIGH),
            (95.0, ConfidenceLevel.CRITICAL),
            (79.9, ConfidenceLevel.MEDIUM),
            (80.0, ConfidenceLevel.HIGH),
            (59.9, ConfidenceLevel.LOW),
            (60.0, ConfidenceLevel.MEDIUM),
            (39.9, ConfidenceLevel.VERY_LOW),
            (40.0, ConfidenceLevel.LOW),
            (19.9, ConfidenceLevel.UNRELIABLE),
            (20.0, ConfidenceLevel.VERY_LOW)
        ]
        
        for confidence, expected_level in boundary_tests:
            level = self.aggregator.get_confidence_level(confidence)
            self.assertEqual(level, expected_level, 
                           f"Confidence {confidence} should map to {expected_level}, got {level}")


if __name__ == '__main__':
    unittest.main()