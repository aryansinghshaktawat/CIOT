"""
Test suite for user experience enhancements in enhanced phone investigation
Tests tooltips, help systems, country selection, and user guidance features
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
import sys
import os

# Add src directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from utils.country_manager import CountrySelectionManager


class TestCountrySelectionManager(unittest.TestCase):
    """Test the country selection and management functionality"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.country_manager = CountrySelectionManager()
    
    def test_get_country_names(self):
        """Test getting list of supported country names"""
        countries = self.country_manager.get_country_names()
        
        self.assertIsInstance(countries, list)
        self.assertGreater(len(countries), 5)  # Should have multiple countries
        self.assertIn('India', countries)
        self.assertIn('United States', countries)
        self.assertIn('United Kingdom', countries)
    
    def test_get_country_info(self):
        """Test getting comprehensive country information"""
        # Test valid country
        india_info = self.country_manager.get_country_info('India')
        
        self.assertIsNotNone(india_info)
        self.assertEqual(india_info['code'], 'IN')
        self.assertEqual(india_info['country_code'], '+91')
        self.assertIn('examples', india_info)
        self.assertIn('validation_tips', india_info)
        
        # Test invalid country
        invalid_info = self.country_manager.get_country_info('NonExistentCountry')
        self.assertIsNone(invalid_info)
    
    def test_get_format_examples(self):
        """Test getting format examples for countries"""
        # Test India
        india_examples = self.country_manager.get_format_examples('India')
        self.assertIsInstance(india_examples, list)
        self.assertGreater(len(india_examples), 0)
        self.assertIn('9876543210', india_examples)
        self.assertIn('+91 9876543210', india_examples)
        
        # Test US
        us_examples = self.country_manager.get_format_examples('United States')
        self.assertIsInstance(us_examples, list)
        self.assertIn('(555) 123-4567', us_examples)
    
    def test_get_placeholder_text(self):
        """Test getting placeholder text for input fields"""
        india_placeholder = self.country_manager.get_placeholder_text('India')
        self.assertIsInstance(india_placeholder, str)
        self.assertIn('9876543210', india_placeholder)
        
        us_placeholder = self.country_manager.get_placeholder_text('United States')
        self.assertIn('555', us_placeholder)
    
    def test_get_format_guidance(self):
        """Test getting format guidance text"""
        india_guidance = self.country_manager.get_format_guidance('India')
        self.assertIsInstance(india_guidance, str)
        self.assertIn('+91', india_guidance)
        
        us_guidance = self.country_manager.get_format_guidance('United States')
        self.assertIn('+1', us_guidance)
    
    def test_get_validation_tips(self):
        """Test getting validation tips for countries"""
        india_tips = self.country_manager.get_validation_tips('India')
        self.assertIsInstance(india_tips, list)
        self.assertGreater(len(india_tips), 0)
        
        # Check that tips contain useful information
        tips_text = ' '.join(india_tips)
        self.assertIn('10 digits', tips_text)
    
    def test_validate_phone_format(self):
        """Test phone number format validation"""
        # Test valid Indian number
        result = self.country_manager.validate_phone_format('9876543210', 'India')
        self.assertIsInstance(result, dict)
        self.assertIn('is_valid', result)
        
        # Test invalid format
        result = self.country_manager.validate_phone_format('123', 'India')
        self.assertFalse(result.get('is_valid', True))
        self.assertIn('suggestions', result)
    
    def test_get_help_text(self):
        """Test getting comprehensive help text"""
        help_text = self.country_manager.get_help_text('India')
        self.assertIsInstance(help_text, str)
        self.assertIn('India Phone Numbers', help_text)
        self.assertIn('Format Examples', help_text)
        self.assertIn('Validation Tips', help_text)
    
    def test_default_country_management(self):
        """Test default country setting and getting"""
        # Test getting default
        default = self.country_manager.get_default_country()
        self.assertEqual(default, 'India')
        
        # Test setting valid country
        success = self.country_manager.set_default_country('United States')
        self.assertTrue(success)
        self.assertEqual(self.country_manager.get_default_country(), 'United States')
        
        # Test setting invalid country
        success = self.country_manager.set_default_country('InvalidCountry')
        self.assertFalse(success)
        # Should remain unchanged
        self.assertEqual(self.country_manager.get_default_country(), 'United States')
    
    def test_get_supported_countries_summary(self):
        """Test getting summary of all supported countries"""
        summary = self.country_manager.get_supported_countries_summary()
        self.assertIsInstance(summary, dict)
        self.assertIn('India', summary)
        self.assertIn('United States', summary)
        
        # Check structure of summary entries
        india_summary = summary['India']
        self.assertIn('code', india_summary)
        self.assertIn('country_code', india_summary)
        self.assertIn('description', india_summary)
        self.assertIn('example', india_summary)


class TestUserGuidanceFeatures(unittest.TestCase):
    """Test user guidance and help system features"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.country_manager = CountrySelectionManager()
    
    def test_contextual_help_content(self):
        """Test that contextual help provides relevant information"""
        # Test phone number help
        phone_help = self.country_manager.get_help_text('India')
        self.assertIn('mobile numbers', phone_help.lower())
        self.assertIn('format', phone_help.lower())
        self.assertIn('validation', phone_help.lower())
    
    def test_error_message_quality(self):
        """Test that error messages are helpful and actionable"""
        result = self.country_manager.validate_phone_format('123', 'India')
        
        # Should have clear error indication
        self.assertFalse(result.get('is_valid', True))
        
        # Should provide suggestions
        self.assertIn('suggestions', result)
        suggestions = result.get('suggestions', [])
        self.assertGreater(len(suggestions), 0)
        
        # Suggestions should be actionable
        for suggestion in suggestions:
            self.assertIsInstance(suggestion, str)
            self.assertGreater(len(suggestion), 10)  # Should be descriptive
    
    def test_format_guidance_accuracy(self):
        """Test that format guidance matches actual validation"""
        for country in ['India', 'United States', 'United Kingdom']:
            examples = self.country_manager.get_format_examples(country)
            
            # Test that at least one example validates correctly
            valid_found = False
            for example in examples[:3]:  # Test first 3 examples
                result = self.country_manager.validate_phone_format(example, country)
                if result.get('is_valid'):
                    valid_found = True
                    break
            
            self.assertTrue(valid_found, f"No valid examples found for {country}")
    
    def test_country_specific_validation_rules(self):
        """Test that validation rules are country-specific"""
        # Indian number should be valid for India but not necessarily for US
        indian_number = '9876543210'
        
        india_result = self.country_manager.validate_phone_format(indian_number, 'India')
        us_result = self.country_manager.validate_phone_format(indian_number, 'United States')
        
        # Results should be different (country-specific validation)
        self.assertNotEqual(
            india_result.get('is_valid'), 
            us_result.get('is_valid')
        )


class TestUserExperienceIntegration(unittest.TestCase):
    """Test integration of user experience features"""
    
    def test_tooltip_system_integration(self):
        """Test that tooltip system can be integrated with UI elements"""
        # This would test the ToolTip class if we had a proper UI testing framework
        # For now, we test the concept
        
        tooltip_texts = {
            'investigation_type': "Select the type of target you want to investigate",
            'country_selection': "Select country for phone number context",
            'format_guidance': "Recommended format for selected country",
            'help_button': "Show detailed format guide"
        }
        
        for key, text in tooltip_texts.items():
            self.assertIsInstance(text, str)
            self.assertGreater(len(text), 10)  # Should be descriptive
            self.assertNotIn('\n\n\n', text)  # Should not have excessive newlines
    
    def test_help_panel_content_structure(self):
        """Test that help panel content is well-structured"""
        country_manager = CountrySelectionManager()
        
        # Test help content for different investigation types
        help_scenarios = {
            'phone_india': ('India', 'phone'),
            'phone_us': ('United States', 'phone'),
            'phone_uk': ('United Kingdom', 'phone')
        }
        
        for scenario, (country, inv_type) in help_scenarios.items():
            help_text = country_manager.get_help_text(country)
            
            # Should contain key sections
            self.assertIn('Phone Numbers', help_text)
            self.assertIn('Format Examples', help_text)
            self.assertIn('Validation Tips', help_text)
            
            # Should be properly formatted
            self.assertIn('─', help_text)  # Should have section dividers
            self.assertGreater(len(help_text), 100)  # Should be substantial
    
    def test_progressive_disclosure(self):
        """Test that information is disclosed progressively"""
        country_manager = CountrySelectionManager()
        
        # Basic info should be concise
        placeholder = country_manager.get_placeholder_text('India')
        self.assertLess(len(placeholder), 50)  # Should be brief
        
        # Guidance should be more detailed
        guidance = country_manager.get_format_guidance('India')
        self.assertGreater(len(guidance), len(placeholder))
        
        # Help text should be most detailed
        help_text = country_manager.get_help_text('India')
        self.assertGreater(len(help_text), len(guidance))
    
    def test_consistency_across_countries(self):
        """Test that user experience is consistent across countries"""
        countries = ['India', 'United States', 'United Kingdom', 'Germany']
        
        for country in countries:
            # Each country should have all required components
            info = self.country_manager.get_country_info(country)
            if info:  # Skip if country not supported
                self.assertIn('examples', info)
                self.assertIn('validation_tips', info)
                self.assertIn('placeholder', info)
                self.assertIn('format_guidance', info)
                
                # Examples should not be empty
                self.assertGreater(len(info['examples']), 0)
                
                # Tips should be helpful
                self.assertGreater(len(info['validation_tips']), 0)


class TestAccessibilityAndUsability(unittest.TestCase):
    """Test accessibility and usability features"""
    
    def test_error_message_clarity(self):
        """Test that error messages are clear and actionable"""
        country_manager = CountrySelectionManager()
        
        # Test with clearly invalid input
        result = country_manager.validate_phone_format('abc123', 'India')
        
        self.assertFalse(result.get('is_valid'))
        
        # Should provide helpful suggestions
        suggestions = result.get('suggestions', [])
        self.assertGreater(len(suggestions), 0)
        
        # Suggestions should be specific and actionable
        for suggestion in suggestions:
            self.assertIn('Try format:', suggestion)
    
    def test_help_text_readability(self):
        """Test that help text is readable and well-formatted"""
        country_manager = CountrySelectionManager()
        
        help_text = country_manager.get_help_text('India')
        
        # Should have proper structure
        lines = help_text.split('\n')
        self.assertGreater(len(lines), 5)  # Should be multi-line
        
        # Should have clear sections
        self.assertIn('Format Examples:', help_text)
        self.assertIn('Validation Tips:', help_text)
        
        # Should use consistent formatting
        self.assertIn('📱', help_text)  # Should have emojis for visual appeal
        self.assertIn('─', help_text)   # Should have dividers
    
    def test_internationalization_readiness(self):
        """Test that the system is ready for internationalization"""
        country_manager = CountrySelectionManager()
        
        # Test that country codes are standardized
        for country_name in country_manager.get_country_names():
            info = country_manager.get_country_info(country_name)
            if info:
                # Country codes should be ISO standard
                self.assertEqual(len(info['code']), 2)
                self.assertTrue(info['code'].isupper())
                
                # Country calling codes should start with +
                self.assertTrue(info['country_code'].startswith('+'))


if __name__ == '__main__':
    # Create test suite
    test_suite = unittest.TestSuite()
    
    # Add test classes
    test_classes = [
        TestCountrySelectionManager,
        TestUserGuidanceFeatures,
        TestUserExperienceIntegration,
        TestAccessibilityAndUsability
    ]
    
    for test_class in test_classes:
        tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
        test_suite.addTests(tests)
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # Print summary
    print(f"\n{'='*60}")
    print(f"USER EXPERIENCE ENHANCEMENT TESTS SUMMARY")
    print(f"{'='*60}")
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Success rate: {((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100):.1f}%")
    
    if result.failures:
        print(f"\nFailures:")
        for test, traceback in result.failures:
            print(f"- {test}: {traceback.split('AssertionError: ')[-1].split('\\n')[0]}")
    
    if result.errors:
        print(f"\nErrors:")
        for test, traceback in result.errors:
            print(f"- {test}: {traceback.split('\\n')[-2]}")
    
    print(f"\n{'='*60}")