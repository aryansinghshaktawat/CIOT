#!/usr/bin/env python3
"""
Unit tests for PhoneNumberFormatter
Tests multiple input formats and validation functionality
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import unittest
from src.utils.osint_utils import IndianPhoneNumberFormatter

class TestIndianPhoneNumberFormatter(unittest.TestCase):
    """Test cases for IndianPhoneNumberFormatter class"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.formatter = IndianPhoneNumberFormatter()
    
    def test_indian_mobile_formats(self):
        """Test various Indian mobile number formats"""
        test_cases = [
            '9876543210',           # Local format
            '+91 9876543210',       # International with space
            '+919876543210',        # International without space
            '09876543210',          # With leading zero
            '91 9876543210',        # Country code without +
            '(+91) 98765-43210',    # Formatted with brackets and dash
        ]
        
        for number in test_cases:
            with self.subTest(number=number):
                result = self.formatter.format_phone_number(number)
                self.assertTrue(result.get('success'), f"Failed to parse {number}")
                
                if result.get('success'):
                    best_format = result['best_format']
                    self.assertEqual(best_format['country_name'], 'India')
                    self.assertEqual(best_format['region_code'], 'IN')
                    self.assertEqual(best_format['international'], '+91 98765 43210')
                    self.assertTrue(best_format['is_valid'])
                    self.assertTrue(best_format['is_mobile'])
    
    def test_number_type_classification(self):
        """Test number type classification"""
        # Test mobile number
        result = self.formatter.format_phone_number('9876543210')
        self.assertTrue(result.get('success'))
        
        if result.get('success'):
            best_format = result['best_format']
            self.assertEqual(best_format['number_type_name'], 'Mobile')
            self.assertTrue(best_format['is_mobile'])
            self.assertFalse(best_format['is_fixed_line'])
    
    def test_validation_and_classification(self):
        """Test comprehensive validation and classification"""
        result = self.formatter.validate_and_classify('9876543210', 'IN')
        
        self.assertTrue(result['is_valid'])
        self.assertTrue(result['is_possible'])
        self.assertEqual(result['number_type'], 'Mobile')
        self.assertTrue(result['is_mobile'])
        self.assertEqual(result['country'], 'India')
        self.assertEqual(result['region'], 'IN')
        
        # Check formatted versions
        formatted = result['formatted_versions']
        self.assertIn('international', formatted)
        self.assertIn('national', formatted)
        self.assertIn('e164', formatted)
        self.assertIn('rfc3966', formatted)
    
    def test_invalid_number_handling(self):
        """Test handling of invalid numbers"""
        invalid_numbers = [
            '123',              # Too short
            '12345678901234',   # Too long
            'abcdefghij',       # Non-numeric
            '',                 # Empty string
        ]
        
        for number in invalid_numbers:
            with self.subTest(number=number):
                result = self.formatter.format_phone_number(number)
                self.assertFalse(result.get('success'), f"Should fail for {number}")
    
    def test_format_suggestions(self):
        """Test format suggestions for different countries"""
        suggestions_in = self.formatter.get_format_suggestions('IN')
        self.assertIsInstance(suggestions_in, list)
        self.assertTrue(len(suggestions_in) > 0)
        
        suggestions_us = self.formatter.get_format_suggestions('US')
        self.assertIsInstance(suggestions_us, list)
        self.assertTrue(len(suggestions_us) > 0)
    
    def test_supported_countries(self):
        """Test supported countries functionality"""
        countries = self.formatter.get_supported_countries()
        self.assertIsInstance(countries, dict)
        self.assertIn('IN', countries)
        # This is an Indian-specific formatter, so it only supports India
        
        # Check country structure
        india_info = countries['IN']
        self.assertIn('name', india_info)
        self.assertIn('examples', india_info)
        self.assertEqual(india_info['name'], 'India')
    
    def test_number_type_name_mapping(self):
        """Test number type name mapping"""
        import phonenumbers
        
        # Test known mappings
        self.assertEqual(
            self.formatter.get_number_type_name(phonenumbers.PhoneNumberType.MOBILE),
            'Mobile'
        )
        self.assertEqual(
            self.formatter.get_number_type_name(phonenumbers.PhoneNumberType.FIXED_LINE),
            'Fixed Line'
        )
        self.assertEqual(
            self.formatter.get_number_type_name(phonenumbers.PhoneNumberType.TOLL_FREE),
            'Toll Free'
        )
    
    def test_multiple_parsing_attempts(self):
        """Test that multiple parsing attempts are recorded"""
        result = self.formatter.format_phone_number('9876543210')
        self.assertTrue(result.get('success'))
        
        parsing_attempts = result.get('parsing_attempts', [])
        self.assertTrue(len(parsing_attempts) > 0)
        
        # Should have at least one successful attempt
        successful_attempts = [attempt for attempt in parsing_attempts if attempt.get('success')]
        self.assertTrue(len(successful_attempts) > 0)
    
    def test_edge_cases(self):
        """Test edge cases and special formats"""
        edge_cases = [
            ('  9876543210  ', 'IN'),    # With spaces
            ('98-765-432-10', 'IN'),     # With dashes
            ('(987) 654-3210', 'IN'),    # With parentheses
        ]
        
        for number, country in edge_cases:
            with self.subTest(number=number, country=country):
                result = self.formatter.format_phone_number(number)
                # Should either succeed or fail gracefully
                self.assertIsInstance(result, dict)
                self.assertIn('success', result)

if __name__ == '__main__':
    # Create tests directory if it doesn't exist
    os.makedirs('tests', exist_ok=True)
    
    # Run tests
    unittest.main(verbosity=2)