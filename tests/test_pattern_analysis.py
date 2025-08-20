"""
Unit tests for Pattern Analysis Engine

Tests all pattern analysis functionality including:
- Related number detection
- Bulk registration detection
- Sequential pattern analysis
- Carrier block analysis
- Relationship confidence scoring
"""

import unittest
from unittest.mock import patch, MagicMock
import sys
import os

# Add src directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from utils.pattern_analysis import (
    PatternAnalysisEngine,
    RelatedNumber,
    BulkRegistrationBlock,
    SequentialPattern,
    CarrierBlock
)


class TestPatternAnalysisEngine(unittest.TestCase):
    """Test cases for PatternAnalysisEngine class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.engine = PatternAnalysisEngine()
        self.test_indian_number = "9876543210"
        self.test_us_number = "5551234567"
    
    def test_initialization(self):
        """Test PatternAnalysisEngine initialization."""
        self.assertIsInstance(self.engine, PatternAnalysisEngine)
        self.assertIn('IN', self.engine.carrier_prefixes)
        self.assertIn('US', self.engine.carrier_prefixes)
        self.assertTrue(len(self.engine.bulk_indicators) > 0)
    
    @patch('utils.pattern_analysis.phonenumbers.parse')
    def test_find_related_numbers_valid_input(self, mock_parse):
        """Test finding related numbers with valid input."""
        # Mock phonenumbers.parse
        mock_number = MagicMock()
        mock_number.national_number = 9876543210
        mock_parse.return_value = mock_number
        
        related = self.engine.find_related_numbers(self.test_indian_number, 'IN')
        
        self.assertIsInstance(related, list)
        self.assertTrue(len(related) > 0)
        
        # Check that results are RelatedNumber objects
        for item in related:
            self.assertIsInstance(item, RelatedNumber)
            self.assertIsInstance(item.confidence_score, float)
            self.assertGreaterEqual(item.confidence_score, 0.0)
            self.assertLessEqual(item.confidence_score, 1.0)
    
    @patch('utils.pattern_analysis.phonenumbers.parse')
    def test_find_related_numbers_invalid_input(self, mock_parse):
        """Test finding related numbers with invalid input."""
        mock_parse.side_effect = Exception("Invalid number")
        
        related = self.engine.find_related_numbers("invalid", 'IN')
        
        self.assertIsInstance(related, list)
        self.assertEqual(len(related), 0)
    
    @patch('utils.pattern_analysis.phonenumbers.parse')
    def test_detect_bulk_registration_positive_case(self, mock_parse):
        """Test bulk registration detection with positive case."""
        # Mock a number that should trigger bulk detection
        mock_number = MagicMock()
        mock_number.national_number = 9876543000  # Ends in 000
        mock_parse.return_value = mock_number
        
        result = self.engine.detect_bulk_registration("9876543000", 'IN')
        
        self.assertIsInstance(result, dict)
        self.assertIn('detected', result)
        self.assertIn('confidence_score', result)
        self.assertIn('indicators', result)
        self.assertIn('risk_assessment', result)
    
    @patch('utils.pattern_analysis.phonenumbers.parse')
    def test_detect_bulk_registration_negative_case(self, mock_parse):
        """Test bulk registration detection with negative case."""
        mock_number = MagicMock()
        mock_number.national_number = 9876543217  # Random ending
        mock_parse.return_value = mock_number
        
        result = self.engine.detect_bulk_registration("9876543217", 'IN')
        
        self.assertIsInstance(result, dict)
        self.assertIn('detected', result)
        # Should have low confidence for random number
        self.assertLessEqual(result.get('confidence_score', 0), 0.5)
    
    @patch('utils.pattern_analysis.phonenumbers.parse')
    def test_analyze_sequential_patterns(self, mock_parse):
        """Test sequential pattern analysis."""
        mock_number = MagicMock()
        mock_number.national_number = 9876543210
        mock_parse.return_value = mock_number
        
        result = self.engine.analyze_sequential_patterns(self.test_indian_number, 'IN')
        
        self.assertIsInstance(result, dict)
        self.assertIn('found', result)
        self.assertIn('patterns', result)
        self.assertIn('confidence_score', result)
        self.assertIn('business_likelihood', result)
        self.assertIn('investigation_priority', result)
        
        if result['found']:
            self.assertIsInstance(result['patterns'], list)
            for pattern in result['patterns']:
                self.assertIsInstance(pattern, SequentialPattern)
    
    @patch('utils.pattern_analysis.phonenumbers.parse')
    @patch('utils.pattern_analysis.carrier.name_for_number')
    def test_analyze_carrier_block(self, mock_carrier, mock_parse):
        """Test carrier block analysis."""
        mock_number = MagicMock()
        mock_number.national_number = 9876543210
        mock_parse.return_value = mock_number
        mock_carrier.return_value = "Airtel"
        
        result = self.engine.analyze_carrier_block(self.test_indian_number, 'IN')
        
        self.assertIsInstance(result, dict)
        self.assertIn('detected', result)
        self.assertIn('carrier_name', result)
        self.assertIn('allocation_type', result)
        self.assertIn('confidence_score', result)
        self.assertIn('characteristics', result)
    
    @patch('utils.pattern_analysis.phonenumbers.parse')
    @patch('utils.pattern_analysis.carrier.name_for_number')
    @patch('utils.pattern_analysis.geocoder.description_for_number')
    def test_calculate_relationship_confidence(self, mock_geocoder, mock_carrier, mock_parse):
        """Test relationship confidence calculation."""
        # Mock two similar numbers
        mock_number1 = MagicMock()
        mock_number1.national_number = 9876543210
        mock_number2 = MagicMock()
        mock_number2.national_number = 9876543211
        
        mock_parse.side_effect = [mock_number1, mock_number2]
        mock_carrier.return_value = "Airtel"
        mock_geocoder.return_value = "Mumbai"
        
        confidence = self.engine.calculate_relationship_confidence(
            "9876543210", "9876543211", 'IN'
        )
        
        self.assertIsInstance(confidence, float)
        self.assertGreaterEqual(confidence, 0.0)
        self.assertLessEqual(confidence, 1.0)
        
        # Sequential numbers should have high confidence
        self.assertGreater(confidence, 0.3)
    
    def test_suggest_investigation_priorities(self):
        """Test investigation priority suggestions."""
        # Mock analysis results
        analysis_results = {
            'bulk_registration': {
                'detected': True,
                'confidence_score': 0.8
            },
            'sequential_patterns': {
                'found': True,
                'business_likelihood': 0.7
            },
            'related_numbers': [
                RelatedNumber(
                    number="9876543211",
                    relationship_type="sequential",
                    confidence_score=0.8,
                    evidence=["Sequential offset: 1"],
                    investigation_priority="High"
                )
            ],
            'carrier_block': {
                'detected': True
            }
        }
        
        priorities = self.engine.suggest_investigation_priorities(analysis_results)
        
        self.assertIsInstance(priorities, list)
        self.assertTrue(len(priorities) > 0)
        
        for priority in priorities:
            self.assertIn('priority', priority)
            self.assertIn('type', priority)
            self.assertIn('description', priority)
            self.assertIn('recommended_actions', priority)
            self.assertIn(priority['priority'], ['High', 'Medium', 'Low'])
    
    def test_parse_number_valid(self):
        """Test phone number parsing with valid input."""
        with patch('utils.pattern_analysis.phonenumbers.parse') as mock_parse:
            mock_number = MagicMock()
            mock_parse.return_value = mock_number
            
            result = self.engine._parse_number(self.test_indian_number, 'IN')
            
            self.assertIsNotNone(result)
            mock_parse.assert_called_once_with(self.test_indian_number, 'IN')
    
    def test_parse_number_invalid(self):
        """Test phone number parsing with invalid input."""
        with patch('utils.pattern_analysis.phonenumbers.parse') as mock_parse:
            mock_parse.side_effect = Exception("Invalid number")
            
            result = self.engine._parse_number("invalid", 'IN')
            
            self.assertIsNone(result)
    
    def test_find_sequential_related(self):
        """Test finding sequentially related numbers."""
        related = self.engine._find_sequential_related("9876543210")
        
        self.assertIsInstance(related, list)
        self.assertTrue(len(related) > 0)
        
        # Check that we get numbers within expected range
        base_num = 9876543210
        for item in related:
            candidate_num = int(item.number)
            offset = abs(candidate_num - base_num)
            self.assertLessEqual(offset, 10)
            self.assertEqual(item.relationship_type, 'sequential')
    
    def test_detect_consecutive_block_positive(self):
        """Test consecutive block detection with positive case."""
        # Number ending in 000 should trigger detection
        result = self.engine._detect_consecutive_block("9876543000")
        
        self.assertIsNotNone(result)
        self.assertIsInstance(result, BulkRegistrationBlock)
        self.assertGreater(result.confidence_score, 0.5)
        self.assertIn('consecutive_pattern', result.indicators)
    
    def test_detect_consecutive_block_negative(self):
        """Test consecutive block detection with negative case."""
        # Random number should not trigger detection
        result = self.engine._detect_consecutive_block("9876543217")
        
        self.assertIsNone(result)
    
    def test_are_sequential_true(self):
        """Test sequential number detection - positive case."""
        result = self.engine._are_sequential("9876543210", "9876543211")
        self.assertTrue(result)
        
        result = self.engine._are_sequential("9876543210", "9876543205")
        self.assertTrue(result)
    
    def test_are_sequential_false(self):
        """Test sequential number detection - negative case."""
        result = self.engine._are_sequential("9876543210", "9876543250")
        self.assertFalse(result)
        
        result = self.engine._are_sequential("9876543210", "1234567890")
        self.assertFalse(result)
    
    def test_extract_digit_pattern(self):
        """Test digit pattern extraction."""
        # Test with repeating digits
        pattern = self.engine._extract_digit_pattern("1112223333")
        self.assertIsInstance(pattern, str)
        self.assertTrue(len(pattern) > 0)
        
        # Test with sequential digits
        pattern = self.engine._extract_digit_pattern("1234567890")
        self.assertIsInstance(pattern, str)
        self.assertTrue(len(pattern) > 0)
    
    def test_calculate_pattern_similarity(self):
        """Test pattern similarity calculation."""
        # Identical numbers
        similarity = self.engine._calculate_pattern_similarity("1234567890", "1234567890")
        self.assertEqual(similarity, 1.0)
        
        # Completely different numbers
        similarity = self.engine._calculate_pattern_similarity("1111111111", "2222222222")
        self.assertEqual(similarity, 0.0)
        
        # Partially similar numbers
        similarity = self.engine._calculate_pattern_similarity("1234567890", "1234567891")
        self.assertGreater(similarity, 0.8)
        self.assertLess(similarity, 1.0)
        
        # Different length numbers
        similarity = self.engine._calculate_pattern_similarity("123", "12345")
        self.assertEqual(similarity, 0.0)
    
    def test_generate_pattern_variations(self):
        """Test pattern variation generation."""
        variations = self.engine._generate_pattern_variations("9876543210", "test_pattern")
        
        self.assertIsInstance(variations, list)
        self.assertTrue(len(variations) > 0)
        
        # All variations should have same length as original
        for variation in variations:
            self.assertEqual(len(variation), len("9876543210"))
            self.assertNotEqual(variation, "9876543210")  # Should be different from original
    
    def test_assess_business_likelihood(self):
        """Test business likelihood assessment."""
        # Create test patterns
        patterns = [
            SequentialPattern(
                base_number="9876543000",
                sequence_type="consecutive",
                pattern_numbers=["9876543000", "9876543001", "9876543002"],
                confidence_score=0.8,
                business_likelihood=0.6
            )
        ]
        
        result = self.engine._assess_business_likelihood("9876543000", patterns)
        
        self.assertIsInstance(result, dict)
        self.assertIn('likelihood', result)
        self.assertIn('indicators', result)
        self.assertGreaterEqual(result['likelihood'], 0.0)
        self.assertLessEqual(result['likelihood'], 1.0)
    
    def test_detect_allocation_type_standard(self):
        """Test allocation type detection for standard numbers."""
        result = self.engine._detect_allocation_type("9876543210", 'IN')
        
        self.assertIsInstance(result, dict)
        self.assertIn('type', result)
        self.assertIn('characteristics', result)
        self.assertEqual(result['type'], 'standard')
    
    def test_detect_allocation_type_toll_free(self):
        """Test allocation type detection for toll-free numbers."""
        result = self.engine._detect_allocation_type("18001234567", 'IN')
        
        self.assertIsInstance(result, dict)
        self.assertEqual(result['type'], 'toll_free')
        self.assertIn('cost', result['characteristics'])
        self.assertEqual(result['characteristics']['cost'], 'free')
    
    def test_detect_allocation_type_premium(self):
        """Test allocation type detection for premium numbers."""
        result = self.engine._detect_allocation_type("9001234567", 'IN')
        
        self.assertIsInstance(result, dict)
        self.assertEqual(result['type'], 'premium')
        self.assertIn('cost', result['characteristics'])
        self.assertEqual(result['characteristics']['cost'], 'premium_rate')
    
    def test_find_consecutive_sequences(self):
        """Test consecutive sequence finding."""
        sequences = self.engine._find_consecutive_sequences("9876543210")
        
        self.assertIsInstance(sequences, list)
        
        for sequence in sequences:
            self.assertIsInstance(sequence, SequentialPattern)
            self.assertEqual(sequence.sequence_type, 'consecutive')
            self.assertIn("9876543210", sequence.pattern_numbers)
    
    def test_find_increment_patterns(self):
        """Test increment pattern finding."""
        patterns = self.engine._find_increment_patterns("9876543210")
        
        self.assertIsInstance(patterns, list)
        
        for pattern in patterns:
            self.assertIsInstance(pattern, SequentialPattern)
            self.assertEqual(pattern.sequence_type, 'increment_pattern')
            self.assertIn("9876543210", pattern.pattern_numbers)
    
    def test_find_alternating_patterns(self):
        """Test alternating pattern finding."""
        # Test with alternating pattern
        patterns = self.engine._find_alternating_patterns("1212121212")
        
        self.assertIsInstance(patterns, list)
        
        if patterns:  # Only check if patterns found
            for pattern in patterns:
                self.assertIsInstance(pattern, SequentialPattern)
                self.assertEqual(pattern.sequence_type, 'alternating')
    
    def test_error_handling(self):
        """Test error handling in various methods."""
        # Test with None input
        result = self.engine.find_related_numbers(None, 'IN')
        self.assertEqual(result, [])
        
        # Test with empty string
        result = self.engine.detect_bulk_registration("", 'IN')
        self.assertIn('detected', result)
        self.assertFalse(result['detected'])
        
        # Test confidence calculation with invalid numbers
        confidence = self.engine.calculate_relationship_confidence("invalid1", "invalid2", 'IN')
        self.assertEqual(confidence, 0.0)


class TestDataClasses(unittest.TestCase):
    """Test cases for data classes used in pattern analysis."""
    
    def test_related_number_creation(self):
        """Test RelatedNumber data class creation."""
        related = RelatedNumber(
            number="9876543211",
            relationship_type="sequential",
            confidence_score=0.8,
            evidence=["Sequential offset: 1"],
            investigation_priority="High"
        )
        
        self.assertEqual(related.number, "9876543211")
        self.assertEqual(related.relationship_type, "sequential")
        self.assertEqual(related.confidence_score, 0.8)
        self.assertEqual(related.investigation_priority, "High")
        self.assertIsInstance(related.evidence, list)
    
    def test_bulk_registration_block_creation(self):
        """Test BulkRegistrationBlock data class creation."""
        block = BulkRegistrationBlock(
            block_start="9876543000",
            block_end="9876543999",
            block_size=1000,
            confidence_score=0.7,
            indicators=["consecutive_pattern"],
            risk_assessment="Medium"
        )
        
        self.assertEqual(block.block_start, "9876543000")
        self.assertEqual(block.block_end, "9876543999")
        self.assertEqual(block.block_size, 1000)
        self.assertEqual(block.confidence_score, 0.7)
        self.assertEqual(block.risk_assessment, "Medium")
    
    def test_sequential_pattern_creation(self):
        """Test SequentialPattern data class creation."""
        pattern = SequentialPattern(
            base_number="9876543210",
            sequence_type="consecutive",
            pattern_numbers=["9876543210", "9876543211", "9876543212"],
            confidence_score=0.8,
            business_likelihood=0.6
        )
        
        self.assertEqual(pattern.base_number, "9876543210")
        self.assertEqual(pattern.sequence_type, "consecutive")
        self.assertEqual(pattern.confidence_score, 0.8)
        self.assertEqual(pattern.business_likelihood, 0.6)
        self.assertIsInstance(pattern.pattern_numbers, list)
    
    def test_carrier_block_creation(self):
        """Test CarrierBlock data class creation."""
        block = CarrierBlock(
            carrier_name="Airtel",
            block_prefix="987654",
            allocation_type="standard",
            block_characteristics={"region": "Mumbai"},
            confidence_score=0.8
        )
        
        self.assertEqual(block.carrier_name, "Airtel")
        self.assertEqual(block.block_prefix, "987654")
        self.assertEqual(block.allocation_type, "standard")
        self.assertEqual(block.confidence_score, 0.8)
        self.assertIsInstance(block.block_characteristics, dict)


if __name__ == '__main__':
    unittest.main()