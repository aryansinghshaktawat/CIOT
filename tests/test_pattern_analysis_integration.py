"""
Integration tests for Pattern Analysis Engine with Enhanced Phone Investigation

Tests the integration of pattern analysis with the enhanced phone investigation workflow.
"""

import unittest
from unittest.mock import patch, MagicMock
import sys
import os

# Add src directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from utils.intelligence_aggregator import IntelligenceAggregator, DataSource
from utils.pattern_analysis import PatternAnalysisEngine


class TestPatternAnalysisIntegration(unittest.TestCase):
    """Test cases for pattern analysis integration."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.aggregator = IntelligenceAggregator()
        self.pattern_engine = PatternAnalysisEngine()
        self.test_phone = "9876543210"
        self.test_country = "IN"
    
    def test_pattern_analysis_in_data_sources(self):
        """Test that pattern analysis is available as a data source."""
        self.assertIn(DataSource.PATTERN_ANALYSIS, DataSource)
        self.assertIn(DataSource.PATTERN_ANALYSIS, self.aggregator.source_weights)
        self.assertIn(DataSource.PATTERN_ANALYSIS, self.aggregator.source_timeouts)
    
    def test_pattern_analysis_source_configuration(self):
        """Test pattern analysis source configuration."""
        # Check source weight
        weight = self.aggregator.source_weights[DataSource.PATTERN_ANALYSIS]
        self.assertEqual(weight, 0.85)
        
        # Check timeout
        timeout = self.aggregator.source_timeouts[DataSource.PATTERN_ANALYSIS]
        self.assertEqual(timeout, 5.0)
        
        # Check field priorities
        pattern_fields = ['related_numbers', 'bulk_registration', 'sequential_patterns', 
                         'carrier_block', 'pattern_intelligence']
        for field in pattern_fields:
            self.assertIn(field, self.aggregator.field_priorities)
            self.assertIn(DataSource.PATTERN_ANALYSIS, self.aggregator.field_priorities[field])
    
    @patch('utils.pattern_analysis.phonenumbers.parse')
    def test_pattern_analysis_query_method(self, mock_parse):
        """Test the pattern analysis query method."""
        # Mock phonenumbers.parse
        mock_number = MagicMock()
        mock_number.national_number = 9876543210
        mock_parse.return_value = mock_number
        
        # Test pattern analysis query
        data, confidence = self.aggregator._query_pattern_analysis(
            self.test_phone, self.test_country, 5.0
        )
        
        self.assertIsInstance(data, dict)
        self.assertIsInstance(confidence, float)
        self.assertGreaterEqual(confidence, 0.0)
        self.assertLessEqual(confidence, 100.0)
        
        # Check required fields in response
        required_fields = ['related_numbers', 'bulk_registration', 'sequential_patterns', 
                          'carrier_block', 'total_related_numbers', 'investigation_priorities']
        for field in required_fields:
            self.assertIn(field, data)
    
    def test_intelligence_aggregation_with_pattern_analysis(self):
        """Test intelligence aggregation including pattern analysis."""
        # Test with pattern analysis as one of the sources
        sources = [DataSource.LIBPHONENUMBER, DataSource.PATTERN_ANALYSIS]
        
        with patch('utils.pattern_analysis.phonenumbers.parse') as mock_parse:
            mock_number = MagicMock()
            mock_number.national_number = 9876543210
            mock_number.country_code = 91
            mock_parse.return_value = mock_number
            
            with patch('phonenumbers.is_valid_number', return_value=True):
                with patch('phonenumbers.format_number', return_value='+919876543210'):
                    with patch('phonenumbers.geocoder.description_for_number', return_value='India'):
                        with patch('phonenumbers.carrier.name_for_number', return_value='Airtel'):
                            
                            result = self.aggregator.aggregate_intelligence(
                                phone_number=self.test_phone,
                                country_code=self.test_country,
                                sources=sources
                            )
        
        self.assertIsNotNone(result)
        self.assertEqual(result.phone_number, self.test_phone)
        self.assertEqual(result.country_code, self.test_country)
        self.assertGreater(len(result.results), 0)
        
        # Check that pattern analysis was included
        pattern_results = [r for r in result.results if r.source == DataSource.PATTERN_ANALYSIS]
        self.assertEqual(len(pattern_results), 1)
        
        pattern_result = pattern_results[0]
        self.assertTrue(pattern_result.success)
        self.assertIn('related_numbers', pattern_result.data)
        self.assertIn('bulk_registration', pattern_result.data)
    
    def test_pattern_analysis_error_handling(self):
        """Test error handling in pattern analysis integration."""
        # Test with invalid phone number
        data, confidence = self.aggregator._query_pattern_analysis("invalid", "XX", 5.0)
        
        self.assertIsInstance(data, dict)
        # Pattern analysis returns structured data even for invalid numbers
        self.assertIn('related_numbers', data)
        self.assertIn('bulk_registration', data)
        self.assertEqual(len(data['related_numbers']), 0)
        self.assertFalse(data['bulk_registration']['detected'])
    
    def test_pattern_analysis_confidence_calculation(self):
        """Test confidence calculation for pattern analysis results."""
        with patch('utils.pattern_analysis.phonenumbers.parse') as mock_parse:
            mock_number = MagicMock()
            mock_number.national_number = 9876543000  # Number ending in 000 for bulk detection
            mock_parse.return_value = mock_number
            
            data, confidence = self.aggregator._query_pattern_analysis(
                "9876543000", self.test_country, 5.0
            )
            
            # Should have higher confidence due to bulk registration detection
            self.assertGreater(confidence, 50.0)
            self.assertTrue(data['bulk_registration']['detected'])
    
    def test_investigation_priorities_integration(self):
        """Test investigation priorities in aggregated results."""
        with patch('utils.pattern_analysis.phonenumbers.parse') as mock_parse:
            mock_number = MagicMock()
            mock_number.national_number = 9876543000
            mock_parse.return_value = mock_number
            
            data, confidence = self.aggregator._query_pattern_analysis(
                "9876543000", self.test_country, 5.0
            )
            
            self.assertIn('investigation_priorities', data)
            self.assertIsInstance(data['investigation_priorities'], list)
            
            # Should have priorities due to bulk registration
            if len(data['investigation_priorities']) > 0:
                priority = data['investigation_priorities'][0]
                self.assertIn('priority', priority)
                self.assertIn('type', priority)
                self.assertIn('description', priority)
                self.assertIn('recommended_actions', priority)
    
    def test_related_numbers_data_structure(self):
        """Test the structure of related numbers data."""
        with patch('utils.pattern_analysis.phonenumbers.parse') as mock_parse:
            mock_number = MagicMock()
            mock_number.national_number = 9876543210
            mock_parse.return_value = mock_number
            
            data, confidence = self.aggregator._query_pattern_analysis(
                self.test_phone, self.test_country, 5.0
            )
            
            self.assertIn('related_numbers', data)
            self.assertIsInstance(data['related_numbers'], list)
            
            if len(data['related_numbers']) > 0:
                related = data['related_numbers'][0]
                required_fields = ['number', 'relationship_type', 'confidence_score', 
                                 'evidence', 'investigation_priority']
                for field in required_fields:
                    self.assertIn(field, related)
    
    def test_bulk_registration_data_structure(self):
        """Test the structure of bulk registration data."""
        with patch('utils.pattern_analysis.phonenumbers.parse') as mock_parse:
            mock_number = MagicMock()
            mock_number.national_number = 9876543000
            mock_parse.return_value = mock_number
            
            data, confidence = self.aggregator._query_pattern_analysis(
                "9876543000", self.test_country, 5.0
            )
            
            self.assertIn('bulk_registration', data)
            bulk_data = data['bulk_registration']
            
            required_fields = ['detected', 'confidence_score', 'indicators', 'risk_assessment']
            for field in required_fields:
                self.assertIn(field, bulk_data)
    
    def test_sequential_patterns_data_structure(self):
        """Test the structure of sequential patterns data."""
        with patch('utils.pattern_analysis.phonenumbers.parse') as mock_parse:
            mock_number = MagicMock()
            mock_number.national_number = 9876543210
            mock_parse.return_value = mock_number
            
            data, confidence = self.aggregator._query_pattern_analysis(
                self.test_phone, self.test_country, 5.0
            )
            
            self.assertIn('sequential_patterns', data)
            seq_data = data['sequential_patterns']
            
            required_fields = ['found', 'patterns', 'confidence_score', 
                             'business_likelihood', 'investigation_priority']
            for field in required_fields:
                self.assertIn(field, seq_data)
    
    def test_carrier_block_data_structure(self):
        """Test the structure of carrier block data."""
        with patch('utils.pattern_analysis.phonenumbers.parse') as mock_parse:
            mock_number = MagicMock()
            mock_number.national_number = 9876543210
            mock_parse.return_value = mock_number
            
            data, confidence = self.aggregator._query_pattern_analysis(
                self.test_phone, self.test_country, 5.0
            )
            
            self.assertIn('carrier_block', data)
            carrier_data = data['carrier_block']
            
            required_fields = ['detected', 'carrier_name', 'allocation_type', 
                             'confidence_score', 'characteristics']
            for field in required_fields:
                self.assertIn(field, carrier_data)


if __name__ == '__main__':
    unittest.main()