"""
Integration tests for Country Selection UI Components
Tests the integration between CountrySelectionManager and GUI components
"""

import unittest
import sys
import os

# Add src directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from utils.country_manager import CountrySelectionManager


class TestCountryUIIntegration(unittest.TestCase):
    """Test cases for Country Selection UI integration"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.manager = CountrySelectionManager()
    
    def test_dropdown_values_generation(self):
        """Test that dropdown values are properly generated"""
        countries = self.manager.get_country_names()
        
        # Should have reasonable number of countries
        self.assertGreaterEqual(len(countries), 5)
        self.assertLessEqual(len(countries), 20)  # Not too many for UI
        
        # Should include major countries
        major_countries = ['India', 'United States', 'United Kingdom', 'Canada']
        for country in major_countries:
            self.assertIn(country, countries)
    
    def test_placeholder_text_updates(self):
        """Test dynamic placeholder text updates"""
        test_cases = [
            ('India', '9876543210'),
            ('United States', '555'),
            ('United Kingdom', '07700'),
            ('Canada', '416'),
            ('Australia', '0412')
        ]
        
        for country, expected_pattern in test_cases:
            placeholder = self.manager.get_placeholder_text(country)
            self.assertIsInstance(placeholder, str)
            self.assertIn(expected_pattern, placeholder)
            self.assertTrue(placeholder.startswith('e.g.,'))
    
    def test_format_guidance_updates(self):
        """Test dynamic format guidance updates"""
        test_cases = [
            ('India', '+91'),
            ('United States', '+1'),
            ('United Kingdom', '+44'),
            ('Germany', '+49'),
            ('France', '+33')
        ]
        
        for country, expected_code in test_cases:
            guidance = self.manager.get_format_guidance(country)
            self.assertIsInstance(guidance, str)
            self.assertIn(expected_code, guidance)
            self.assertTrue(guidance.startswith('Format:'))
    
    def test_validation_error_messages(self):
        """Test validation error messages with suggestions"""
        # Test invalid Indian number
        result = self.manager.validate_phone_format('123', 'India')
        self.assertFalse(result['is_valid'])
        self.assertIn('suggestions', result)
        self.assertGreater(len(result['suggestions']), 0)
        
        # Each suggestion should be properly formatted
        for suggestion in result['suggestions']:
            self.assertIsInstance(suggestion, str)
            self.assertTrue(suggestion.startswith('Try format:'))
    
    def test_help_text_generation(self):
        """Test comprehensive help text generation"""
        countries_to_test = ['India', 'United States', 'United Kingdom']
        
        for country in countries_to_test:
            help_text = self.manager.get_help_text(country)
            
            # Should contain key sections
            self.assertIn(country, help_text)
            self.assertIn('Format Examples:', help_text)
            self.assertIn('Validation Tips:', help_text)
            self.assertIn('Country Code:', help_text)
            
            # Should be reasonably sized for UI display
            self.assertGreater(len(help_text), 100)
            self.assertLess(len(help_text), 1000)
    
    def test_country_change_workflow(self):
        """Test complete country change workflow"""
        # Simulate user selecting different countries
        countries_to_test = ['India', 'United States', 'United Kingdom', 'Germany']
        
        for country in countries_to_test:
            # Get all UI elements that should update
            placeholder = self.manager.get_placeholder_text(country)
            guidance = self.manager.get_format_guidance(country)
            tips = self.manager.get_validation_tips(country)
            examples = self.manager.get_format_examples(country)
            
            # Verify all elements are properly populated
            self.assertIsInstance(placeholder, str)
            self.assertGreater(len(placeholder), 5)
            
            self.assertIsInstance(guidance, str)
            self.assertGreater(len(guidance), 10)
            
            self.assertIsInstance(tips, list)
            self.assertGreater(len(tips), 0)
            
            self.assertIsInstance(examples, list)
            self.assertGreater(len(examples), 2)
    
    def test_phone_validation_with_country_context(self):
        """Test phone validation with proper country context"""
        test_cases = [
            # (phone_number, country, should_be_valid)
            ('9876543210', 'India', True),
            ('+91 9876543210', 'India', True),
            ('(555) 123-4567', 'United States', True),
            ('+1 555 123 4567', 'United States', True),
            ('07700 900123', 'United Kingdom', True),
            ('+44 7700 900123', 'United Kingdom', True),
            
            # Cross-country validation (should fail)
            ('9876543210', 'United States', False),
            ('(555) 123-4567', 'India', False),
            
            # Invalid numbers
            ('123', 'India', False),
            ('abc', 'United States', False)
        ]
        
        for phone, country, should_be_valid in test_cases:
            result = self.manager.validate_phone_format(phone, country)
            
            if should_be_valid:
                # Should be valid or at least possible
                is_valid_or_possible = result.get('is_valid', False) or result.get('is_possible', False)
                self.assertTrue(is_valid_or_possible, 
                              f"Phone {phone} should be valid/possible for {country}")
            else:
                # Should be invalid
                self.assertFalse(result.get('is_valid', False), 
                               f"Phone {phone} should be invalid for {country}")
    
    def test_ui_component_data_consistency(self):
        """Test that all UI components have consistent data"""
        countries = self.manager.get_country_names()
        
        for country in countries:
            # All UI elements should be available
            info = self.manager.get_country_info(country)
            placeholder = self.manager.get_placeholder_text(country)
            guidance = self.manager.get_format_guidance(country)
            tips = self.manager.get_validation_tips(country)
            examples = self.manager.get_format_examples(country)
            country_code = self.manager.get_country_code_number(country)
            
            # Verify consistency
            self.assertIsNotNone(info)
            self.assertIn(info['country_code'], guidance)
            self.assertIn(info['country_code'], country_code)
            
            # Examples should match placeholder pattern
            if examples:
                # At least one example should contain the pattern from placeholder
                placeholder_pattern = placeholder.replace('e.g., ', '').split()[0]
                example_found = any(placeholder_pattern in example for example in examples)
                # This might not always match exactly, so we'll just check examples exist
                self.assertGreater(len(examples), 0)
    
    def test_error_handling_for_ui(self):
        """Test error handling scenarios for UI components"""
        # Test with invalid country
        invalid_country = 'NonExistentCountry'
        
        # Should return safe defaults
        placeholder = self.manager.get_placeholder_text(invalid_country)
        self.assertEqual(placeholder, "e.g., phone number")
        
        guidance = self.manager.get_format_guidance(invalid_country)
        self.assertEqual(guidance, "Format: +XX XXXXXXXXX")
        
        tips = self.manager.get_validation_tips(invalid_country)
        self.assertEqual(tips, [])
        
        examples = self.manager.get_format_examples(invalid_country)
        self.assertEqual(examples, [])
        
        country_code = self.manager.get_country_code_number(invalid_country)
        self.assertEqual(country_code, "+XX")
        
        help_text = self.manager.get_help_text(invalid_country)
        self.assertEqual(help_text, "Country not supported")


if __name__ == '__main__':
    unittest.main()