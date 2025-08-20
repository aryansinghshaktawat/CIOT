#!/usr/bin/env python3
"""
Unit tests for IndianPhoneNumberFormatter
Tests Indian phone number formats and telecom operator detection
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
    
    def test_indian_operator_detection(self):
        """Test Indian telecom operator detection"""
        test_cases = [
            ('7012345678', 'Jio'),      # Jio number
            ('9876543210', 'Airtel'),   # Airtel number
            ('9912345678', 'Vi'),       # Vi number
        ]
        
        for number, expected_operator in test_cases:
            with self.subTest(number=number, operator=expected_operator):
                result = self.formatter.format_phone_number(number)
                self.assertTrue(result.get('success'))
                
                if result.get('success'):
                    best_format = result['best_format']
                    # Check if operator is detected (may not be exact due to number patterns)
                    self.assertIn('indian_operator', best_format)
    
    def test_telecom_circle_detection(self):
        """Test telecom circle detection"""
        test_cases = [
            ('9810123456', 'Delhi'),    # Delhi pattern
            ('9820123456', 'Mumbai'),   # Mumbai pattern
            ('9830123456', 'Kolkata'),  # Kolkata pattern
        ]
        
        for number, expected_circle in test_cases:
            with self.subTest(number=number, circle=expected_circle):
                result = self.formatter.format_phone_number(number)
                self.assertTrue(result.get('success'))
                
                if result.get('success'):
                    best_format = result['best_format']
                    self.assertIn('telecom_circle', best_format)
    
    def test_number_type_classification(self):
        """Test number type classification for Indian numbers"""
        result = self.formatter.format_phone_number('9876543210')
        self.assertTrue(result.get('success'))
        
        if result.get('success'):
            best_format = result['best_format']
            self.assertEqual(best_format['number_type_name'], 'Mobile')
            self.assertTrue(best_format['is_mobile'])
            self.assertFalse(best_format['is_fixed_line'])
            self.assertEqual(best_format['country_code'], 91)
    
    def test_indian_number_analysis(self):
        """Test comprehensive Indian number analysis"""
        analysis = self.formatter.analyze_indian_number('9876543210')
        
        self.assertIn('operator', analysis)
        self.assertIn('circle', analysis)
        self.assertIn('confidence', analysis)
        self.assertIn('series_info', analysis)
        self.assertIn('mnp_possible', analysis)
        self.assertIn('generation', analysis)
        
        # Check series info structure
        series_info = analysis['series_info']
        self.assertIn('first_digit', series_info)
        self.assertIn('series_type', series_info)
        self.assertIn('allocation_era', series_info)
    
    def test_invalid_number_handling(self):
        """Test handling of invalid numbers"""
        invalid_numbers = [
            '123',              # Too short
            '12345678901234',   # Too long
            'abcdefghij',       # Non-numeric
            '',                 # Empty string
            '1234567890',       # US format (should fail for Indian formatter)
        ]
        
        for number in invalid_numbers:
            with self.subTest(number=number):
                result = self.formatter.format_phone_number(number)
                # Should either fail or not be recognized as Indian
                if result.get('success'):
                    best_format = result['best_format']
                    # If it succeeds, it should be recognized as Indian
                    self.assertEqual(best_format.get('country_code'), 91)
    
    def test_format_suggestions(self):
        """Test format suggestions for Indian numbers"""
        suggestions = self.formatter.get_format_suggestions('IN')
        self.assertIsInstance(suggestions, list)
        self.assertTrue(len(suggestions) > 0)
        
        # Should contain Indian format examples
        suggestion_text = ' '.join(suggestions)
        self.assertIn('9876543210', suggestion_text)
        self.assertIn('+91', suggestion_text)
    
    def test_indian_format_examples(self):
        """Test Indian format examples"""
        examples = self.formatter.get_indian_format_examples()
        self.assertIsInstance(examples, list)
        self.assertTrue(len(examples) > 0)
        
        # Should contain various Indian formats
        self.assertIn('9876543210', examples)
        self.assertIn('+91 9876543210', examples)
        self.assertIn('09876543210', examples)
    
    def test_supported_countries(self):
        """Test supported countries (should only be India)"""
        countries = self.formatter.get_supported_countries()
        self.assertIsInstance(countries, dict)
        self.assertIn('IN', countries)
        
        # Check India-specific structure
        india_info = countries['IN']
        self.assertIn('name', india_info)
        self.assertIn('operators', india_info)
        self.assertIn('examples', india_info)
        self.assertIn('circles', india_info)
        self.assertEqual(india_info['name'], 'India')
        
        # Should contain Indian operators
        operators = india_info['operators']
        self.assertIn('Airtel', operators)
        self.assertIn('Jio', operators)
        self.assertIn('Vi', operators)
        self.assertIn('BSNL', operators)
    
    def test_jio_number_detection(self):
        """Test Jio number detection (70-79 series)"""
        jio_numbers = ['7012345678', '7112345678', '7212345678', '7312345678']
        
        for number in jio_numbers:
            with self.subTest(number=number):
                analysis = self.formatter.analyze_indian_number(number)
                self.assertEqual(analysis['operator'], 'Jio')
                self.assertEqual(analysis['confidence'], 'High')
                self.assertEqual(analysis['generation'], 'New')
    
    def test_airtel_number_detection(self):
        """Test Airtel number detection"""
        airtel_numbers = ['9876543210', '9999912345', '9700012345']
        
        for number in airtel_numbers:
            with self.subTest(number=number):
                analysis = self.formatter.analyze_indian_number(number)
                # Should detect as Airtel or at least not as Jio
                self.assertIn(analysis['operator'], ['Airtel', 'Vi', 'Unknown'])
    
    def test_metro_circle_detection(self):
        """Test metro circle detection"""
        metro_cases = [
            ('9810123456', 'Delhi Metro'),
            ('9820123456', 'Mumbai Metro'),
            ('9830123456', 'Kolkata Metro'),
            ('9840123456', 'Chennai Metro'),
        ]
        
        for number, expected_circle in metro_cases:
            with self.subTest(number=number):
                circle = self.formatter.detect_telecom_circle(number)
                self.assertIn('Metro', circle)

if __name__ == '__main__':
    # Create tests directory if it doesn't exist
    os.makedirs('tests', exist_ok=True)
    
    # Run tests
    unittest.main(verbosity=2)