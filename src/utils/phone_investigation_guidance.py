"""
Phone Investigation User Guidance System
Provides country-specific guidance, format examples, and best practices
"""

from typing import Dict, List, Any, Optional
import re
from dataclasses import dataclass


@dataclass
class CountryGuidance:
    """Country-specific guidance information"""
    country_code: str
    country_name: str
    display_name: str
    format_examples: List[str]
    common_mistakes: List[str]
    validation_tips: List[str]
    carrier_info: Dict[str, Any]
    investigation_notes: List[str]


class PhoneInvestigationGuidanceSystem:
    """
    Comprehensive guidance system for phone number investigation
    """
    
    def __init__(self):
        self.country_guidance = self._initialize_country_guidance()
        self.general_best_practices = self._initialize_best_practices()
        self.error_help = self._initialize_error_help()
    
    def _initialize_country_guidance(self) -> Dict[str, CountryGuidance]:
        """Initialize country-specific guidance data"""
        return {
            'IN': CountryGuidance(
                country_code='IN',
                country_name='India',
                display_name='India (IN)',
                format_examples=[
                    '9876543210 (10-digit mobile)',
                    '+91 9876543210 (international format)',
                    '09876543210 (with leading zero)',
                    '(+91) 98765-43210 (formatted)',
                    '91 9876543210 (country code without +)'
                ],
                common_mistakes=[
                    'Including +91 twice (e.g., +91+919876543210)',
                    'Using wrong country code (e.g., +1 instead of +91)',
                    'Including extra digits or characters',
                    'Missing digits (less than 10 digits)',
                    'Starting with wrong digit (must start with 6, 7, 8, or 9)'
                ],
                validation_tips=[
                    'Indian mobile numbers are exactly 10 digits',
                    'Must start with 6, 7, 8, or 9',
                    'Landline numbers vary by city (6-8 digits + area code)',
                    'Toll-free numbers start with 1800',
                    'Premium numbers start with 186x'
                ],
                carrier_info={
                    'major_operators': ['Airtel', 'Jio', 'Vi (Vodafone Idea)', 'BSNL', 'MTNL'],
                    'mobile_series': {
                        'Jio': '70x, 71x, 72x, 73x, 74x, 75x, 76x, 77x, 78x, 79x, 88x, 89x',
                        'Airtel': '98765xxxxx, 99999xxxxx, 97xxx, 96xxx, 95xxx, 94xxx',
                        'Vi': '99xxx, 98xxx, 97xxx, 96xxx, 95xxx, 94xxx, 93xxx, 92xxx',
                        'BSNL': '94xxx, 95xxx, 96xxx, 97xxx, 98xxx, 99xxx'
                    },
                    'porting_info': 'Mobile Number Portability (MNP) is available - carrier may not match original allocation'
                },
                investigation_notes=[
                    'India has extensive mobile coverage with high smartphone penetration',
                    'WhatsApp usage is very high - most numbers likely have WhatsApp',
                    'Privacy settings are typically high on social media',
                    'Telecom circles determine regional allocation',
                    'MNP (Mobile Number Portability) is common - original carrier may differ'
                ]
            ),
            'US': CountryGuidance(
                country_code='US',
                country_name='United States',
                display_name='United States (US)',
                format_examples=[
                    '(555) 123-4567 (standard format)',
                    '+1 555 123 4567 (international)',
                    '5551234567 (10-digit)',
                    '1-555-123-4567 (with country code)',
                    '555.123.4567 (dot notation)'
                ],
                common_mistakes=[
                    'Using invalid area codes (starting with 0 or 1)',
                    'Including +1 twice',
                    'Wrong number of digits (not exactly 10)',
                    'Using 555-01xx (reserved for fiction)',
                    'Confusing with Canadian numbers'
                ],
                validation_tips=[
                    'Area code cannot start with 0 or 1',
                    'Exchange code (middle 3 digits) cannot start with 0 or 1',
                    'Total of 10 digits (excluding country code)',
                    'Toll-free: 800, 833, 844, 855, 866, 877, 888',
                    'Premium: 900 area code'
                ],
                carrier_info={
                    'major_operators': ['Verizon', 'AT&T', 'T-Mobile', 'Sprint'],
                    'mvnos': ['Mint Mobile', 'Cricket', 'Metro', 'Boost'],
                    'porting_info': 'Number portability is common between carriers'
                },
                investigation_notes=[
                    'High social media usage across platforms',
                    'Strong privacy regulations (varies by state)',
                    'Extensive spam/robocall databases available',
                    'Business numbers often in public directories'
                ]
            ),
            'GB': CountryGuidance(
                country_code='GB',
                country_name='United Kingdom',
                display_name='United Kingdom (GB)',
                format_examples=[
                    '+44 20 7946 0958 (London landline)',
                    '020 7946 0958 (national format)',
                    '+44 7911 123456 (mobile)',
                    '07911 123456 (national mobile)',
                    '+44 800 123 4567 (toll-free)'
                ],
                common_mistakes=[
                    'Including leading zero with country code',
                    'Wrong mobile prefix (not 07xxx)',
                    'Confusing landline area codes',
                    'Using old numbering formats',
                    'Missing digits in mobile numbers'
                ],
                validation_tips=[
                    'Mobile numbers start with 07',
                    'London landlines: 020 (8 digits total)',
                    'Remove leading 0 when using +44',
                    'Landline area codes vary by region',
                    'Premium rate: 09xx numbers'
                ],
                carrier_info={
                    'major_operators': ['EE', 'O2', 'Three', 'Vodafone'],
                    'mvnos': ['Tesco Mobile', 'giffgaff', 'Lebara'],
                    'porting_info': 'Number portability available between networks'
                },
                investigation_notes=[
                    'GDPR compliance affects data availability',
                    'Strong privacy protections',
                    'TPS (Telephone Preference Service) for opt-outs',
                    'Ofcom regulates telecommunications'
                ]
            ),
            'CA': CountryGuidance(
                country_code='CA',
                country_name='Canada',
                display_name='Canada (CA)',
                format_examples=[
                    '(416) 555-0123 (Toronto)',
                    '+1 416 555 0123 (international)',
                    '4165550123 (10-digit)',
                    '1-416-555-0123 (with country code)',
                    '(604) 555-0123 (Vancouver)'
                ],
                common_mistakes=[
                    'Confusing with US numbers (same +1 code)',
                    'Using invalid area codes',
                    'Wrong exchange codes',
                    'Including country code twice',
                    'Not recognizing Canadian area codes'
                ],
                validation_tips=[
                    'Same format as US numbers (+1)',
                    'Distinct Canadian area codes (e.g., 416, 604, 514)',
                    '10 digits total (excluding country code)',
                    'Area code cannot start with 0 or 1',
                    'Exchange code cannot start with 0 or 1'
                ],
                carrier_info={
                    'major_operators': ['Rogers', 'Bell', 'Telus', 'Freedom Mobile'],
                    'regional': ['SaskTel', 'MTS', 'Eastlink'],
                    'porting_info': 'Local number portability available'
                },
                investigation_notes=[
                    'PIPEDA privacy laws apply',
                    'Similar social media usage to US',
                    'French language considerations in Quebec',
                    'CRTC regulates telecommunications'
                ]
            ),
            'AU': CountryGuidance(
                country_code='AU',
                country_name='Australia',
                display_name='Australia (AU)',
                format_examples=[
                    '+61 4 1234 5678 (mobile)',
                    '04 1234 5678 (national mobile)',
                    '+61 2 9876 5432 (Sydney landline)',
                    '(02) 9876 5432 (national landline)',
                    '+61 1800 123 456 (toll-free)'
                ],
                common_mistakes=[
                    'Including leading zero with country code',
                    'Wrong mobile prefix (not 04xx)',
                    'Confusing state area codes',
                    'Using old numbering formats',
                    'Wrong number of digits'
                ],
                validation_tips=[
                    'Mobile numbers start with 04',
                    'Remove leading 0 when using +61',
                    'Landline area codes: 02 (NSW), 03 (VIC), 07 (QLD), 08 (WA/SA)',
                    'Toll-free: 1800 numbers',
                    'Premium: 190x numbers'
                ],
                carrier_info={
                    'major_operators': ['Telstra', 'Optus', 'Vodafone'],
                    'mvnos': ['Boost', 'Belong', 'Amaysim'],
                    'porting_info': 'Mobile number portability available'
                },
                investigation_notes=[
                    'Privacy Act 1988 applies',
                    'Do Not Call Register for marketing',
                    'ACMA regulates telecommunications',
                    'High mobile penetration rate'
                ]
            )
        }
    
    def _initialize_best_practices(self) -> Dict[str, List[str]]:
        """Initialize general best practices"""
        return {
            'input_formatting': [
                'Copy and paste numbers when possible to avoid typos',
                'Remove extra spaces, brackets, and dashes - the system will handle formatting',
                'Include country code for international numbers',
                'Double-check the country selection matches the number',
                'Use the most complete format available (international preferred)'
            ],
            'investigation_approach': [
                'Start with basic validation before running full investigation',
                'Use multiple sources to verify information',
                'Be aware of privacy laws in the target country',
                'Consider time zones when interpreting "last seen" data',
                'Cross-reference results with other investigation methods'
            ],
            'result_interpretation': [
                'Higher confidence scores indicate more reliable data',
                'Carrier information may be outdated due to number portability',
                'Social media presence depends on privacy settings',
                'Spam reports may be false positives',
                'Historical data shows changes over time'
            ],
            'privacy_and_ethics': [
                'Only investigate numbers you have legitimate reason to research',
                'Respect privacy laws and regulations',
                'Do not use information for harassment or illegal activities',
                'Be aware of data protection requirements (GDPR, CCPA, etc.)',
                'Consider informing subjects of investigation when appropriate'
            ],
            'troubleshooting': [
                'Try different country selections if parsing fails',
                'Check for typos in the phone number',
                'Verify your internet connection for API calls',
                'Some features may be limited for certain number types',
                'Contact support if you encounter persistent issues'
            ]
        }
    
    def _initialize_error_help(self) -> Dict[str, Dict[str, Any]]:
        """Initialize error-specific help information"""
        return {
            'INVALID_PHONE_FORMAT': {
                'title': 'Invalid Phone Number Format',
                'description': 'The phone number could not be parsed in any recognized format.',
                'common_causes': [
                    'Incorrect country selection',
                    'Missing or extra digits',
                    'Invalid characters in the number',
                    'Wrong country code',
                    'Incomplete number'
                ],
                'solutions': [
                    'Verify the country selection matches the number',
                    'Check for typos or missing digits',
                    'Try different format variations',
                    'Use international format with country code',
                    'Remove any special characters except + and digits'
                ]
            },
            'COUNTRY_NOT_SUPPORTED': {
                'title': 'Country Not Supported',
                'description': 'The selected country is not currently supported for phone number investigation.',
                'common_causes': [
                    'Typo in country code',
                    'Country not in supported list',
                    'Using full country name instead of code'
                ],
                'solutions': [
                    'Check the supported countries list',
                    'Use Auto-Detect (Global) option',
                    'Try a similar country if appropriate',
                    'Contact support to request country addition'
                ]
            },
            'API_CONNECTION_ERROR': {
                'title': 'API Connection Error',
                'description': 'Unable to connect to external investigation services.',
                'common_causes': [
                    'Internet connectivity issues',
                    'API service temporarily unavailable',
                    'Rate limiting or quota exceeded',
                    'Invalid API configuration'
                ],
                'solutions': [
                    'Check your internet connection',
                    'Wait a few minutes and try again',
                    'Verify API key configuration',
                    'Try investigating a different number'
                ]
            },
            'RATE_LIMIT_EXCEEDED': {
                'title': 'Rate Limit Exceeded',
                'description': 'Too many requests have been made to the investigation services.',
                'common_causes': [
                    'Investigating too many numbers quickly',
                    'Shared API limits reached',
                    'Service quota exceeded'
                ],
                'solutions': [
                    'Wait before making another request',
                    'Reduce investigation frequency',
                    'Consider upgrading API plan',
                    'Focus on most important investigations'
                ]
            }
        }
    
    def get_country_guidance(self, country_code: str) -> Optional[CountryGuidance]:
        """Get guidance for specific country"""
        return self.country_guidance.get(country_code.upper())
    
    def get_format_examples(self, country_code: str) -> List[str]:
        """Get format examples for country"""
        guidance = self.get_country_guidance(country_code)
        if guidance:
            return guidance.format_examples
        return self.country_guidance['IN'].format_examples  # Default to India
    
    def get_validation_tips(self, country_code: str) -> List[str]:
        """Get validation tips for country"""
        guidance = self.get_country_guidance(country_code)
        if guidance:
            return guidance.validation_tips
        return []
    
    def get_common_mistakes(self, country_code: str) -> List[str]:
        """Get common mistakes for country"""
        guidance = self.get_country_guidance(country_code)
        if guidance:
            return guidance.common_mistakes
        return []
    
    def get_carrier_info(self, country_code: str) -> Dict[str, Any]:
        """Get carrier information for country"""
        guidance = self.get_country_guidance(country_code)
        if guidance:
            return guidance.carrier_info
        return {}
    
    def get_investigation_notes(self, country_code: str) -> List[str]:
        """Get investigation notes for country"""
        guidance = self.get_country_guidance(country_code)
        if guidance:
            return guidance.investigation_notes
        return []
    
    def get_best_practices(self, category: str = None) -> Dict[str, List[str]]:
        """Get best practices, optionally filtered by category"""
        if category:
            return {category: self.general_best_practices.get(category, [])}
        return self.general_best_practices
    
    def get_error_help(self, error_code: str) -> Optional[Dict[str, Any]]:
        """Get help information for specific error"""
        return self.error_help.get(error_code)
    
    def get_supported_countries(self) -> List[Dict[str, str]]:
        """Get list of supported countries"""
        return [
            {
                'code': guidance.country_code,
                'name': guidance.country_name,
                'display_name': guidance.display_name
            }
            for guidance in self.country_guidance.values()
        ]
    
    def suggest_country_from_number(self, phone_number: str) -> Optional[str]:
        """Suggest country based on phone number patterns"""
        clean_number = re.sub(r'[^\d+]', '', phone_number)
        
        # Check for country code patterns
        if clean_number.startswith('+91') or (clean_number.startswith('91') and len(clean_number) == 12):
            return 'IN'
        elif clean_number.startswith('+1') or (clean_number.startswith('1') and len(clean_number) == 11):
            # Could be US or CA - need more analysis
            if len(clean_number) == 11:
                area_code = clean_number[1:4]
                # Some distinctly Canadian area codes
                canadian_codes = ['204', '226', '236', '249', '250', '289', '306', '343', '365', '403', '416', '418', '431', '437', '438', '450', '506', '514', '519', '548', '579', '581', '587', '604', '613', '639', '647', '672', '705', '709', '742', '778', '780', '782', '807', '819', '825', '867', '873', '902', '905']
                if area_code in canadian_codes:
                    return 'CA'
            return 'US'  # Default to US for +1
        elif clean_number.startswith('+44'):
            return 'GB'
        elif clean_number.startswith('+61'):
            return 'AU'
        elif clean_number.startswith('+49'):
            return 'DE'
        elif clean_number.startswith('+33'):
            return 'FR'
        elif clean_number.startswith('+81'):
            return 'JP'
        elif clean_number.startswith('+86'):
            return 'CN'
        elif clean_number.startswith('+55'):
            return 'BR'
        
        # Check for patterns without country code
        if len(clean_number) == 10:
            # Could be Indian mobile (starts with 6,7,8,9)
            if clean_number[0] in ['6', '7', '8', '9']:
                return 'IN'
            # Could be US/CA number
            elif clean_number[0] in ['2', '3', '4', '5', '6', '7', '8', '9']:
                return 'US'
        elif len(clean_number) == 11 and clean_number.startswith('0'):
            # Could be Indian number with leading zero
            if clean_number[1] in ['6', '7', '8', '9']:
                return 'IN'
        
        return None
    
    def generate_input_guidance(self, phone_number: str, country_code: str = None) -> Dict[str, Any]:
        """Generate comprehensive input guidance for a phone number"""
        # Suggest country if not provided
        if not country_code:
            country_code = self.suggest_country_from_number(phone_number)
        
        if not country_code:
            country_code = 'IN'  # Default
        
        guidance = self.get_country_guidance(country_code)
        
        return {
            'suggested_country': country_code,
            'country_name': guidance.country_name if guidance else 'Unknown',
            'format_examples': self.get_format_examples(country_code),
            'validation_tips': self.get_validation_tips(country_code),
            'common_mistakes': self.get_common_mistakes(country_code),
            'carrier_info': self.get_carrier_info(country_code),
            'investigation_notes': self.get_investigation_notes(country_code)
        }
    
    def validate_number_format(self, phone_number: str, country_code: str) -> Dict[str, Any]:
        """Validate number format and provide specific guidance"""
        clean_number = re.sub(r'[^\d+]', '', phone_number)
        issues = []
        suggestions = []
        
        guidance = self.get_country_guidance(country_code)
        if not guidance:
            return {
                'is_valid_format': False,
                'issues': ['Country not supported'],
                'suggestions': ['Try Auto-Detect (Global) option']
            }
        
        # Country-specific validation
        if country_code == 'IN':
            if not clean_number.startswith(('+91', '91')) and len(clean_number) != 10:
                issues.append('Indian numbers should be 10 digits or include +91 country code')
                suggestions.append('Try: 9876543210 or +91 9876543210')
            
            if len(clean_number) == 10 and clean_number[0] not in ['6', '7', '8', '9']:
                issues.append('Indian mobile numbers must start with 6, 7, 8, or 9')
                suggestions.append('Check if this is a landline number or verify the first digit')
        
        elif country_code == 'US':
            if not clean_number.startswith(('+1', '1')) and len(clean_number) != 10:
                issues.append('US numbers should be 10 digits or include +1 country code')
                suggestions.append('Try: (555) 123-4567 or +1 555 123 4567')
            
            if len(clean_number) >= 10:
                area_code = clean_number[-10:-7] if len(clean_number) >= 10 else ''
                if area_code and area_code[0] in ['0', '1']:
                    issues.append('US area codes cannot start with 0 or 1')
                    suggestions.append('Verify the area code is correct')
        
        elif country_code == 'GB':
            if clean_number.startswith('+44') and clean_number[3] == '0':
                issues.append('Remove leading zero when using +44 country code')
                suggestions.append('Try: +44 20 7946 0958 instead of +44 020 7946 0958')
        
        return {
            'is_valid_format': len(issues) == 0,
            'issues': issues,
            'suggestions': suggestions,
            'format_examples': guidance.format_examples,
            'validation_tips': guidance.validation_tips
        }


# Global guidance system instance
guidance_system = PhoneInvestigationGuidanceSystem()


def get_country_guidance(country_code: str) -> Optional[CountryGuidance]:
    """Get country-specific guidance"""
    return guidance_system.get_country_guidance(country_code)


def get_format_examples(country_code: str) -> List[str]:
    """Get format examples for country"""
    return guidance_system.get_format_examples(country_code)


def get_input_guidance(phone_number: str, country_code: str = None) -> Dict[str, Any]:
    """Get comprehensive input guidance"""
    return guidance_system.generate_input_guidance(phone_number, country_code)


def get_error_help(error_code: str) -> Optional[Dict[str, Any]]:
    """Get help for specific error"""
    return guidance_system.get_error_help(error_code)


def get_best_practices(category: str = None) -> Dict[str, List[str]]:
    """Get best practices"""
    return guidance_system.get_best_practices(category)


def validate_number_format(phone_number: str, country_code: str) -> Dict[str, Any]:
    """Validate number format with guidance"""
    return guidance_system.validate_number_format(phone_number, country_code)