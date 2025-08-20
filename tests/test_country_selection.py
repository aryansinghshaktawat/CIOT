"""
Unit tests for Country Selection Manager
Tests country selection UI components and functionality
"""

import unittest
import sys
import os

# Add src directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from utils.country_manager import CountrySelectionManager


class TestCountrySelectionManager(unittest.TestCase):
    """Test cases for CountrySelectionManager class"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.manager = CountrySelectionManager()
    
    def test_initialization(self):
        """Test CountrySelectionManager initialization"""
        self.assertIsInstance(self.manager, CountrySelectionManager)
        self.assertEqual(self.manager.get_default_country(), 'India')
        self.assertGreater(len(self.manager.get_country_names()), 5)
    
    def test_get_country_names(self):
        """Test getting list of country names"""
        countries = self.manager.get_country_names()
        self.assertIsInstance(countries, list)
        self.assertIn('India', countries)
        self.assertIn('United States', countries)
        self.assertIn('United Kingdom', countries)
        self.assertGreater(len(countries), 5)
    
    def test_get_country_codes(self):
        """Test getting list of country codes"""
        codes = self.manager.get_country_codes()
        self.assertIsInstance(codes, list)
        self.assertIn('IN', codes)
        self.assertIn('US', codes)
        self.assertIn('GB', codes)
        self.assertEqual(len(codes), len(self.manager.get_country_names()))
    
    def test_get_country_info(self):
        """Test getting country information"""
        # Test valid country
        india_info = self.manager.get_country_info('India')
        self.assertIsNotNone(india_info)
        self.assertEqual(india_info['code'], 'IN')
        self.assertEqual(india_info['country_code'], '+91')
        self.assertIn('examples', india_info)
        self.assertIn('placeholder', india_info)
        self.assertIn('format_guidance', india_info)
        self.assertIn('validation_tips', india_info)
        
        # Test invalid country
        invalid_info = self.manager.get_country_info('NonExistentCountry')
        self.assertIsNone(invalid_info)
    
    def test_get_country_by_code(self):
        """Test getting country by ISO code"""
        # Test valid code
        result = self.manager.get_country_by_code('IN')
        self.assertIsNotNone(result)
        country_name, country_info = result
        self.assertEqual(country_name, 'India')
        self.assertEqual(country_info['code'], 'IN')
        
        # Test case insensitive
        result = self.manager.get_country_by_code('in')
        self.assertIsNotNone(result)
        
        # Test invalid code
        result = self.manager.get_country_by_code('XX')
        self.assertIsNone(result)
    
    def test_get_format_examples(self):
        """Test getting format examples for countries"""
        # Test India
        india_examples = self.manager.get_format_examples('India')
        self.assertIsInstance(india_examples, list)
        self.assertGreater(len(india_examples), 3)
        self.assertIn('9876543210', india_examples)
        self.assertIn('+91 9876543210', india_examples)
        
        # Test US
        us_examples = self.manager.get_format_examples('United States')
        self.assertIsInstance(us_examples, list)
        self.assertGreater(len(us_examples), 3)
        
        # Test invalid country
        invalid_examples = self.manager.get_format_examples('InvalidCountry')
        self.assertEqual(invalid_examples, [])
    
    def test_get_placeholder_text(self):
        """Test getting placeholder text for countries"""
        # Test India
        india_placeholder = self.manager.get_placeholder_text('India')
        self.assertIsInstance(india_placeholder, str)
        self.assertIn('9876543210', india_placeholder)
        
        # Test US
        us_placeholder = self.manager.get_placeholder_text('United States')
        self.assertIsInstance(us_placeholder, str)
        self.assertIn('555', us_placeholder)
        
        # Test invalid country
        invalid_placeholder = self.manager.get_placeholder_text('InvalidCountry')
        self.assertEqual(invalid_placeholder, "e.g., phone number")
    
    def test_get_format_guidance(self):
        """Test getting format guidance for countries"""
        # Test India
        india_guidance = self.manager.get_format_guidance('India')
        self.assertIsInstance(india_guidance, str)
        self.assertIn('+91', india_guidance)
        self.assertIn('Format:', india_guidance)
        
        # Test US
        us_guidance = self.manager.get_format_guidance('United States')
        self.assertIsInstance(us_guidance, str)
        self.assertIn('+1', us_guidance)
        
        # Test invalid country
        invalid_guidance = self.manager.get_format_guidance('InvalidCountry')
        self.assertEqual(invalid_guidance, "Format: +XX XXXXXXXXX")
    
    def test_get_validation_tips(self):
        """Test getting validation tips for countries"""
        # Test India
        india_tips = self.manager.get_validation_tips('India')
        self.assertIsInstance(india_tips, list)
        self.assertGreater(len(india_tips), 2)
        
        # Test US
        us_tips = self.manager.get_validation_tips('United States')
        self.assertIsInstance(us_tips, list)
        self.assertGreater(len(us_tips), 2)
        
        # Test invalid country
        invalid_tips = self.manager.get_validation_tips('InvalidCountry')
        self.assertEqual(invalid_tips, [])
    
    def test_get_country_code_number(self):
        """Test getting country calling codes"""
        # Test India
        india_code = self.manager.get_country_code_number('India')
        self.assertEqual(india_code, '+91')
        
        # Test US
        us_code = self.manager.get_country_code_number('United States')
        self.assertEqual(us_code, '+1')
        
        # Test invalid country
        invalid_code = self.manager.get_country_code_number('InvalidCountry')
        self.assertEqual(invalid_code, "+XX")
    
    def test_validate_phone_format(self):
        """Test phone number format validation"""
        # Test valid Indian number
        result = self.manager.validate_phone_format('9876543210', 'India')
        self.assertIsInstance(result, dict)
        self.assertIn('is_valid', result)
        self.assertIn('country_code', result)
        
        # Test invalid Indian number
        result = self.manager.validate_phone_format('123', 'India')
        self.assertIsInstance(result, dict)
        self.assertFalse(result.get('is_valid', True))
        self.assertIn('suggestions', result)
        
        # Test valid US number
        result = self.manager.validate_phone_format('(555) 123-4567', 'United States')
        self.assertIsInstance(result, dict)
        
        # Test unsupported country
        result = self.manager.validate_phone_format('123456789', 'InvalidCountry')
        self.assertFalse(result['is_valid'])
        self.assertEqual(result['error'], 'Unsupported country')
    
    def test_get_help_text(self):
        """Test getting comprehensive help text"""
        # Test India
        india_help = self.manager.get_help_text('India')
        self.assertIsInstance(india_help, str)
        self.assertIn('India', india_help)
        self.assertIn('+91', india_help)
        self.assertIn('Format Examples:', india_help)
        self.assertIn('Validation Tips:', india_help)
        
        # Test invalid country
        invalid_help = self.manager.get_help_text('InvalidCountry')
        self.assertEqual(invalid_help, "Country not supported")
    
    def test_default_country_management(self):
        """Test default country management"""
        # Test getting default
        default = self.manager.get_default_country()
        self.assertEqual(default, 'India')
        
        # Test setting valid default
        result = self.manager.set_default_country('United States')
        self.assertTrue(result)
        self.assertEqual(self.manager.get_default_country(), 'United States')
        
        # Test setting invalid default
        result = self.manager.set_default_country('InvalidCountry')
        self.assertFalse(result)
        self.assertEqual(self.manager.get_default_country(), 'United States')  # Should remain unchanged
        
        # Reset to original
        self.manager.set_default_country('India')
    
    def test_get_supported_countries_summary(self):
        """Test getting summary of all supported countries"""
        summary = self.manager.get_supported_countries_summary()
        self.assertIsInstance(summary, dict)
        self.assertIn('India', summary)
        self.assertIn('United States', summary)
        
        # Check India summary structure
        india_summary = summary['India']
        self.assertIn('code', india_summary)
        self.assertIn('country_code', india_summary)
        self.assertIn('description', india_summary)
        self.assertIn('example', india_summary)
        self.assertEqual(india_summary['code'], 'IN')
        self.assertEqual(india_summary['country_code'], '+91')
    
    def test_country_data_consistency(self):
        """Test consistency of country data"""
        countries = self.manager.get_country_names()
        codes = self.manager.get_country_codes()
        
        # Same number of countries and codes
        self.assertEqual(len(countries), len(codes))
        
        # Each country has complete data
        for country in countries:
            info = self.manager.get_country_info(country)
            self.assertIsNotNone(info)
            
            # Required fields
            required_fields = ['code', 'country_code', 'examples', 'placeholder', 
                             'format_guidance', 'description', 'validation_tips']
            for field in required_fields:
                self.assertIn(field, info, f"Missing {field} in {country}")
                self.assertIsNotNone(info[field], f"None value for {field} in {country}")
            
            # Examples should be non-empty list
            self.assertIsInstance(info['examples'], list)
            self.assertGreater(len(info['examples']), 0)
            
            # Validation tips should be non-empty list
            self.assertIsInstance(info['validation_tips'], list)
            self.assertGreater(len(info['validation_tips']), 0)


class TestCountrySelectionIntegration(unittest.TestCase):
    """Integration tests for country selection with phone formatting"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.manager = CountrySelectionManager()
    
    def test_indian_phone_validation_integration(self):
        """Test integration with Indian phone validation"""
        test_numbers = [
            ('9876543210', True),
            ('+91 9876543210', True),
            ('09876543210', True),
            ('123', False),
            ('abcd', False)
        ]
        
        for number, should_be_valid in test_numbers:
            result = self.manager.validate_phone_format(number, 'India')
            if should_be_valid:
                self.assertTrue(result.get('is_valid') or result.get('is_possible'), 
                              f"Number {number} should be valid/possible")
            else:
                self.assertFalse(result.get('is_valid', False), 
                               f"Number {number} should be invalid")
    
    def test_us_phone_validation_integration(self):
        """Test integration with US phone validation"""
        test_numbers = [
            ('(555) 123-4567', True),
            ('+1 555 123 4567', True),
            ('5551234567', True),
            ('123', False),
            ('0001234567', False)  # Invalid area code
        ]
        
        for number, should_be_valid in test_numbers:
            result = self.manager.validate_phone_format(number, 'United States')
            if should_be_valid:
                self.assertTrue(result.get('is_valid') or result.get('is_possible'), 
                              f"Number {number} should be valid/possible")
            else:
                self.assertFalse(result.get('is_valid', False), 
                               f"Number {number} should be invalid")


if __name__ == '__main__':
    unittest.main()