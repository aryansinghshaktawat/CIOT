"""
Country Selection Manager for Phone Number Investigation
Manages country selection, format examples, and validation guidance
"""

from typing import Dict, List, Optional, Tuple
import phonenumbers
from phonenumbers import PhoneNumberFormat


class CountrySelectionManager:
    """
    Manages country selection for phone number investigations
    Provides country-specific format examples and validation guidance
    """
    
    def __init__(self):
        # Major countries with their phone number examples and patterns
        self.countries = {
            'India': {
                'code': 'IN',
                'country_code': '+91',
                'examples': [
                    '9876543210',
                    '+91 9876543210', 
                    '09876543210',
                    '91 9876543210',
                    '(+91) 98765-43210'
                ],
                'placeholder': 'e.g., 9876543210',
                'format_guidance': 'Format: +91 9876543210',
                'description': 'Indian mobile numbers (10 digits)',
                'validation_tips': [
                    'Mobile numbers start with 6, 7, 8, or 9',
                    'Total 10 digits after country code',
                    'Can include or exclude +91 prefix'
                ]
            },
            'United States': {
                'code': 'US',
                'country_code': '+1',
                'examples': [
                    '(555) 123-4567',
                    '+1 555 123 4567',
                    '5551234567',
                    '1-555-123-4567',
                    '+1 (555) 123-4567'
                ],
                'placeholder': 'e.g., (555) 123-4567',
                'format_guidance': 'Format: +1 (555) 123-4567',
                'description': 'US phone numbers (10 digits)',
                'validation_tips': [
                    'Area code cannot start with 0 or 1',
                    'Total 10 digits after country code',
                    'Format: (XXX) XXX-XXXX'
                ]
            },
            'United Kingdom': {
                'code': 'GB',
                'country_code': '+44',
                'examples': [
                    '07700 900123',
                    '+44 7700 900123',
                    '447700900123',
                    '0044 7700 900123',
                    '+44 (0) 7700 900123'
                ],
                'placeholder': 'e.g., 07700 900123',
                'format_guidance': 'Format: +44 7700 900123',
                'description': 'UK mobile numbers',
                'validation_tips': [
                    'Mobile numbers start with 07',
                    'Total 11 digits including leading 0',
                    'Can include or exclude +44 prefix'
                ]
            },
            'Canada': {
                'code': 'CA',
                'country_code': '+1',
                'examples': [
                    '(416) 555-0123',
                    '+1 416 555 0123',
                    '4165550123',
                    '1-416-555-0123',
                    '+1 (416) 555-0123'
                ],
                'placeholder': 'e.g., (416) 555-0123',
                'format_guidance': 'Format: +1 (416) 555-0123',
                'description': 'Canadian phone numbers (10 digits)',
                'validation_tips': [
                    'Same format as US numbers',
                    'Area code cannot start with 0 or 1',
                    'Total 10 digits after country code'
                ]
            },
            'Australia': {
                'code': 'AU',
                'country_code': '+61',
                'examples': [
                    '0412 345 678',
                    '+61 412 345 678',
                    '61412345678',
                    '0061 412 345 678',
                    '+61 (0) 412 345 678'
                ],
                'placeholder': 'e.g., 0412 345 678',
                'format_guidance': 'Format: +61 412 345 678',
                'description': 'Australian mobile numbers',
                'validation_tips': [
                    'Mobile numbers start with 04',
                    'Total 10 digits including leading 0',
                    'Can include or exclude +61 prefix'
                ]
            },
            'Germany': {
                'code': 'DE',
                'country_code': '+49',
                'examples': [
                    '0151 12345678',
                    '+49 151 12345678',
                    '4915112345678',
                    '0049 151 12345678',
                    '+49 (0) 151 12345678'
                ],
                'placeholder': 'e.g., 0151 12345678',
                'format_guidance': 'Format: +49 151 12345678',
                'description': 'German mobile numbers',
                'validation_tips': [
                    'Mobile numbers start with 015, 016, 017',
                    'Variable length (10-12 digits)',
                    'Can include or exclude +49 prefix'
                ]
            },
            'France': {
                'code': 'FR',
                'country_code': '+33',
                'examples': [
                    '06 12 34 56 78',
                    '+33 6 12 34 56 78',
                    '33612345678',
                    '0033 6 12 34 56 78',
                    '+33 (0) 6 12 34 56 78'
                ],
                'placeholder': 'e.g., 06 12 34 56 78',
                'format_guidance': 'Format: +33 6 12 34 56 78',
                'description': 'French mobile numbers',
                'validation_tips': [
                    'Mobile numbers start with 06 or 07',
                    'Total 10 digits including leading 0',
                    'Can include or exclude +33 prefix'
                ]
            },
            'Japan': {
                'code': 'JP',
                'country_code': '+81',
                'examples': [
                    '090-1234-5678',
                    '+81 90 1234 5678',
                    '819012345678',
                    '0081 90 1234 5678',
                    '+81 (0) 90-1234-5678'
                ],
                'placeholder': 'e.g., 090-1234-5678',
                'format_guidance': 'Format: +81 90 1234 5678',
                'description': 'Japanese mobile numbers',
                'validation_tips': [
                    'Mobile numbers start with 070, 080, 090',
                    'Total 11 digits including leading 0',
                    'Can include or exclude +81 prefix'
                ]
            },
            'China': {
                'code': 'CN',
                'country_code': '+86',
                'examples': [
                    '138 0013 8000',
                    '+86 138 0013 8000',
                    '8613800138000',
                    '0086 138 0013 8000',
                    '+86 (0) 138-0013-8000'
                ],
                'placeholder': 'e.g., 138 0013 8000',
                'format_guidance': 'Format: +86 138 0013 8000',
                'description': 'Chinese mobile numbers',
                'validation_tips': [
                    'Mobile numbers start with 13, 14, 15, 17, 18, 19',
                    'Total 11 digits',
                    'Can include or exclude +86 prefix'
                ]
            },
            'Brazil': {
                'code': 'BR',
                'country_code': '+55',
                'examples': [
                    '(11) 91234-5678',
                    '+55 11 91234 5678',
                    '5511912345678',
                    '0055 11 91234 5678',
                    '+55 (11) 91234-5678'
                ],
                'placeholder': 'e.g., (11) 91234-5678',
                'format_guidance': 'Format: +55 11 91234 5678',
                'description': 'Brazilian mobile numbers',
                'validation_tips': [
                    'Mobile numbers have 9 digits after area code',
                    'Area code is 2 digits',
                    'Mobile numbers start with 9'
                ]
            }
        }
        
        # Default country (India for this application)
        self.default_country = 'India'
    
    def get_country_names(self) -> List[str]:
        """Get list of supported country names"""
        return list(self.countries.keys())
    
    def get_country_codes(self) -> List[str]:
        """Get list of supported country codes"""
        return [country['code'] for country in self.countries.values()]
    
    def get_country_info(self, country_name: str) -> Optional[Dict]:
        """
        Get comprehensive country information
        
        Args:
            country_name: Name of the country
            
        Returns:
            Dict with country information or None if not found
        """
        return self.countries.get(country_name)
    
    def get_country_by_code(self, country_code: str) -> Optional[Tuple[str, Dict]]:
        """
        Get country information by country code
        
        Args:
            country_code: ISO country code (e.g., 'IN', 'US')
            
        Returns:
            Tuple of (country_name, country_info) or None if not found
        """
        for name, info in self.countries.items():
            if info['code'] == country_code.upper():
                return name, info
        return None
    
    def get_format_examples(self, country_name: str) -> List[str]:
        """
        Get format examples for a specific country
        
        Args:
            country_name: Name of the country
            
        Returns:
            List of format examples
        """
        country_info = self.get_country_info(country_name)
        if country_info:
            return country_info['examples']
        return []
    
    def get_placeholder_text(self, country_name: str) -> str:
        """
        Get placeholder text for a specific country
        
        Args:
            country_name: Name of the country
            
        Returns:
            Placeholder text for input field
        """
        country_info = self.get_country_info(country_name)
        if country_info:
            return country_info['placeholder']
        return "e.g., phone number"
    
    def get_format_guidance(self, country_name: str) -> str:
        """
        Get format guidance text for a specific country
        
        Args:
            country_name: Name of the country
            
        Returns:
            Format guidance text
        """
        country_info = self.get_country_info(country_name)
        if country_info:
            return country_info['format_guidance']
        return "Format: +XX XXXXXXXXX"
    
    def get_validation_tips(self, country_name: str) -> List[str]:
        """
        Get validation tips for a specific country
        
        Args:
            country_name: Name of the country
            
        Returns:
            List of validation tips
        """
        country_info = self.get_country_info(country_name)
        if country_info:
            return country_info['validation_tips']
        return []
    
    def get_country_code_number(self, country_name: str) -> str:
        """
        Get country calling code for a specific country
        
        Args:
            country_name: Name of the country
            
        Returns:
            Country calling code (e.g., '+91', '+1')
        """
        country_info = self.get_country_info(country_name)
        if country_info:
            return country_info['country_code']
        return "+XX"
    
    def validate_phone_format(self, phone_number: str, country_name: str) -> Dict:
        """
        Validate phone number format for specific country
        
        Args:
            phone_number: Phone number to validate
            country_name: Country context for validation
            
        Returns:
            Dict with validation results
        """
        country_info = self.get_country_info(country_name)
        if not country_info:
            return {
                'is_valid': False,
                'error': 'Unsupported country',
                'suggestions': []
            }
        
        try:
            # Use libphonenumber for validation
            parsed_number = phonenumbers.parse(phone_number, country_info['code'])
            is_valid = phonenumbers.is_valid_number(parsed_number)
            is_possible = phonenumbers.is_possible_number(parsed_number)
            
            result = {
                'is_valid': is_valid,
                'is_possible': is_possible,
                'country_code': country_info['code'],
                'country_name': country_name,
                'formatted_international': None,
                'formatted_national': None,
                'suggestions': []
            }
            
            if is_valid:
                result['formatted_international'] = phonenumbers.format_number(
                    parsed_number, PhoneNumberFormat.INTERNATIONAL
                )
                result['formatted_national'] = phonenumbers.format_number(
                    parsed_number, PhoneNumberFormat.NATIONAL
                )
            else:
                # Provide format suggestions
                result['suggestions'] = [
                    f"Try format: {example}" for example in country_info['examples'][:3]
                ]
            
            return result
            
        except Exception as e:
            return {
                'is_valid': False,
                'is_possible': False,
                'error': str(e),
                'suggestions': [
                    f"Try format: {example}" for example in country_info['examples'][:3]
                ]
            }
    
    def get_help_text(self, country_name: str) -> str:
        """
        Get comprehensive help text for a specific country
        
        Args:
            country_name: Name of the country
            
        Returns:
            Formatted help text with examples and tips
        """
        country_info = self.get_country_info(country_name)
        if not country_info:
            return "Country not supported"
        
        help_text = f"📱 {country_name} Phone Numbers\n"
        help_text += f"{'─' * 30}\n"
        help_text += f"Country Code: {country_info['country_code']}\n"
        help_text += f"Description: {country_info['description']}\n\n"
        
        help_text += "📋 Format Examples:\n"
        for i, example in enumerate(country_info['examples'][:3], 1):
            help_text += f"  {i}. {example}\n"
        
        help_text += "\n💡 Validation Tips:\n"
        for i, tip in enumerate(country_info['validation_tips'], 1):
            help_text += f"  {i}. {tip}\n"
        
        return help_text
    
    def get_default_country(self) -> str:
        """Get default country name"""
        return self.default_country
    
    def set_default_country(self, country_name: str) -> bool:
        """
        Set default country
        
        Args:
            country_name: Name of the country to set as default
            
        Returns:
            True if successful, False if country not supported
        """
        if country_name in self.countries:
            self.default_country = country_name
            return True
        return False
    
    def get_supported_countries_summary(self) -> Dict:
        """
        Get summary of all supported countries
        
        Returns:
            Dict with country summaries
        """
        summary = {}
        for name, info in self.countries.items():
            summary[name] = {
                'code': info['code'],
                'country_code': info['country_code'],
                'description': info['description'],
                'example': info['examples'][0] if info['examples'] else 'N/A'
            }
        return summary