"""
Cached Phone Number Formatter
Enhanced phone number formatting with performance optimization and caching
"""

import time
import hashlib
import threading
from typing import Dict, Any, Optional, List
import phonenumbers
from phonenumbers import geocoder, carrier, timezone
from .performance_cache import cached, PerformanceMetrics, performance_optimizer
import logging

logger = logging.getLogger(__name__)


class CachedPhoneNumberFormatter:
    """
    Enhanced phone number formatter with caching and performance optimization
    """
    
    def __init__(self):
        self.stats = {
            'total_formats': 0,
            'cache_hits': 0,
            'cache_misses': 0,
            'parsing_errors': 0,
            'total_time': 0.0
        }
        self.lock = threading.Lock()
    
    @cached("phone_number_parsing", ttl=3600)  # Cache for 1 hour
    def format_phone_number(self, phone_input: str, default_country: str = 'IN') -> Dict[str, Any]:
        """
        Format phone number with caching and multiple parsing attempts
        
        Args:
            phone_input: Raw phone number input
            default_country: ISO country code for parsing context
            
        Returns:
            Dict containing formatting results and validation data
        """
        start_time = time.time()
        
        try:
            with self.lock:
                self.stats['total_formats'] += 1
            
            # Clean input - remove all non-digits except +
            import re
            clean_input = re.sub(r'[^\d+]', '', phone_input)
            
            # Multiple parsing attempts with different strategies
            parsing_attempts = [
                # Direct parsing with country
                {'input': phone_input, 'country': default_country, 'method': f'Direct {default_country} format'},
                # Clean digits with country
                {'input': clean_input, 'country': default_country, 'method': f'Clean digits {default_country}'},
                # Add country code for 10-digit numbers
                {'input': self._add_country_code(clean_input, default_country), 'country': default_country, 'method': f'Add {default_country} prefix'},
                # Remove leading 0 for 11-digit numbers
                {'input': clean_input[1:] if clean_input.startswith('0') and len(clean_input) == 11 else clean_input, 'country': default_country, 'method': 'Remove leading zero'},
                # Global parsing without country context
                {'input': phone_input, 'country': None, 'method': 'Global auto-detect'},
                {'input': clean_input, 'country': None, 'method': 'Global clean digits'}
            ]
            
            formatted_results = {
                'success': False,
                'original_input': phone_input,
                'parsing_attempts': [],
                'best_format': None,
                'country_used': default_country,
                'processing_time': 0.0
            }
            
            best_result = None
            
            for attempt in parsing_attempts:
                try:
                    parsed_number = phonenumbers.parse(attempt['input'], attempt['country'])
                    
                    if phonenumbers.is_valid_number(parsed_number):
                        # Get comprehensive phone number data
                        result = self._extract_phone_data(parsed_number, attempt['method'])
                        formatted_results['parsing_attempts'].append(result)
                        
                        # Use first valid result as best
                        if not best_result:
                            best_result = result
                            formatted_results['success'] = True
                            formatted_results['best_format'] = result
                    else:
                        formatted_results['parsing_attempts'].append({
                            'success': False,
                            'method': attempt['method'],
                            'error': 'Invalid number format',
                            'is_possible': phonenumbers.is_possible_number(parsed_number)
                        })
                        
                except Exception as e:
                    formatted_results['parsing_attempts'].append({
                        'success': False,
                        'method': attempt['method'],
                        'error': str(e)
                    })
            
            # Calculate processing time
            processing_time = time.time() - start_time
            formatted_results['processing_time'] = processing_time
            
            with self.lock:
                self.stats['total_time'] += processing_time
                if not formatted_results['success']:
                    self.stats['parsing_errors'] += 1
            
            return formatted_results
            
        except Exception as e:
            with self.lock:
                self.stats['parsing_errors'] += 1
                self.stats['total_time'] += time.time() - start_time
            
            return {
                'success': False,
                'original_input': phone_input,
                'error': f'Phone formatting error: {str(e)}',
                'processing_time': time.time() - start_time
            }
    
    def _add_country_code(self, clean_input: str, country: str) -> str:
        """Add appropriate country code to phone number"""
        if not clean_input or clean_input.startswith('+'):
            return clean_input
        
        # Country code mapping
        country_codes = {
            'IN': '+91',
            'US': '+1',
            'GB': '+44',
            'CA': '+1',
            'AU': '+61',
            'DE': '+49',
            'FR': '+33',
            'JP': '+81',
            'CN': '+86',
            'BR': '+55'
        }
        
        country_code = country_codes.get(country, '+91')  # Default to India
        
        # Add country code for numbers that appear to be local
        if country == 'IN' and len(clean_input) == 10 and clean_input[0] in ['6', '7', '8', '9']:
            return f'{country_code}{clean_input}'
        elif country == 'US' and len(clean_input) == 10:
            return f'{country_code}{clean_input}'
        elif len(clean_input) >= 10 and not clean_input.startswith(country_code.replace('+', '')):
            return f'{country_code}{clean_input}'
        
        return clean_input
    
    @cached("phone_data_extraction", ttl=7200)  # Cache for 2 hours
    def _extract_phone_data(self, parsed_number, method: str) -> Dict[str, Any]:
        """
        Extract comprehensive data from parsed phone number
        
        Args:
            parsed_number: Parsed phonenumbers object
            method: Parsing method used
            
        Returns:
            Dict with comprehensive phone number data
        """
        try:
            # Basic validation
            is_valid = phonenumbers.is_valid_number(parsed_number)
            is_possible = phonenumbers.is_possible_number(parsed_number)
            
            # Formatted versions
            international = phonenumbers.format_number(parsed_number, phonenumbers.PhoneNumberFormat.INTERNATIONAL)
            national = phonenumbers.format_number(parsed_number, phonenumbers.PhoneNumberFormat.NATIONAL)
            e164 = phonenumbers.format_number(parsed_number, phonenumbers.PhoneNumberFormat.E164)
            rfc3966 = phonenumbers.format_number(parsed_number, phonenumbers.PhoneNumberFormat.RFC3966)
            
            # Geographic information
            country_name = geocoder.description_for_number(parsed_number, 'en')
            location = geocoder.description_for_number(parsed_number, 'en')
            region_code = phonenumbers.region_code_for_number(parsed_number)
            
            # Carrier information
            carrier_name = carrier.name_for_number(parsed_number, 'en')
            
            # Timezone information
            timezones = timezone.time_zones_for_number(parsed_number)
            
            # Number type classification
            number_type = phonenumbers.number_type(parsed_number)
            number_type_name = self._get_number_type_name(number_type)
            
            # Enhanced classification
            is_mobile = number_type == phonenumbers.PhoneNumberType.MOBILE
            is_fixed_line = number_type == phonenumbers.PhoneNumberType.FIXED_LINE
            is_voip = number_type == phonenumbers.PhoneNumberType.VOIP
            is_toll_free = number_type == phonenumbers.PhoneNumberType.TOLL_FREE
            
            return {
                'success': True,
                'method': method,
                'parsed_number': parsed_number,
                'is_valid': is_valid,
                'is_possible': is_possible,
                
                # Formatted versions
                'international': international,
                'national': national,
                'e164': e164,
                'rfc3966': rfc3966,
                
                # Geographic information
                'country_code': parsed_number.country_code,
                'national_number': parsed_number.national_number,
                'country_name': country_name,
                'location': location,
                'region_code': region_code,
                
                # Carrier information
                'carrier_name': carrier_name,
                
                # Timezone information
                'timezones': list(timezones),
                
                # Number type classification
                'number_type': number_type,
                'number_type_name': number_type_name,
                'is_mobile': is_mobile,
                'is_fixed_line': is_fixed_line,
                'is_voip': is_voip,
                'is_toll_free': is_toll_free,
                
                # Additional metadata
                'confidence_score': self._calculate_confidence_score(
                    is_valid, is_possible, carrier_name, location
                ),
                'data_completeness': self._calculate_data_completeness(
                    carrier_name, location, timezones
                )
            }
            
        except Exception as e:
            return {
                'success': False,
                'method': method,
                'error': f'Data extraction error: {str(e)}'
            }
    
    def _get_number_type_name(self, number_type) -> str:
        """Convert phonenumbers number type to readable name"""
        type_mapping = {
            phonenumbers.PhoneNumberType.FIXED_LINE: 'Fixed Line',
            phonenumbers.PhoneNumberType.MOBILE: 'Mobile',
            phonenumbers.PhoneNumberType.FIXED_LINE_OR_MOBILE: 'Fixed Line or Mobile',
            phonenumbers.PhoneNumberType.TOLL_FREE: 'Toll Free',
            phonenumbers.PhoneNumberType.PREMIUM_RATE: 'Premium Rate',
            phonenumbers.PhoneNumberType.SHARED_COST: 'Shared Cost',
            phonenumbers.PhoneNumberType.VOIP: 'VoIP',
            phonenumbers.PhoneNumberType.PERSONAL_NUMBER: 'Personal Number',
            phonenumbers.PhoneNumberType.PAGER: 'Pager',
            phonenumbers.PhoneNumberType.UAN: 'Universal Access Number',
            phonenumbers.PhoneNumberType.VOICEMAIL: 'Voicemail',
            phonenumbers.PhoneNumberType.UNKNOWN: 'Unknown'
        }
        return type_mapping.get(number_type, 'Unknown')
    
    def _calculate_confidence_score(self, is_valid: bool, is_possible: bool, 
                                  carrier_name: str, location: str) -> float:
        """Calculate confidence score for phone number data"""
        score = 0.0
        
        if is_valid:
            score += 40.0
        elif is_possible:
            score += 20.0
        
        if carrier_name and carrier_name.strip():
            score += 25.0
        
        if location and location.strip():
            score += 20.0
        
        # Base score for successful parsing
        score += 15.0
        
        return min(score, 100.0)
    
    def _calculate_data_completeness(self, carrier_name: str, location: str, 
                                   timezones: List[str]) -> float:
        """Calculate data completeness percentage"""
        completeness = 0.0
        total_fields = 3
        
        if carrier_name and carrier_name.strip():
            completeness += 1
        
        if location and location.strip():
            completeness += 1
        
        if timezones:
            completeness += 1
        
        return (completeness / total_fields) * 100.0
    
    @cached("phone_validation", ttl=1800)  # Cache for 30 minutes
    def validate_and_classify(self, phone_input: str, country_code: str = 'IN') -> Dict[str, Any]:
        """
        Comprehensive validation and classification of phone number with caching
        
        Args:
            phone_input: Phone number to validate
            country_code: Country context for validation
            
        Returns:
            Dict with validation results and classification
        """
        formatting_result = self.format_phone_number(phone_input, country_code)
        
        if not formatting_result.get('success'):
            return {
                'is_valid': False,
                'is_possible': False,
                'error': formatting_result.get('error', 'Invalid format'),
                'suggestions': self._get_format_suggestions(country_code),
                'processing_time': formatting_result.get('processing_time', 0.0)
            }
        
        best_format = formatting_result['best_format']
        
        return {
            'is_valid': best_format['is_valid'],
            'is_possible': best_format['is_possible'],
            'number_type': best_format['number_type_name'],
            'is_mobile': best_format['is_mobile'],
            'is_fixed_line': best_format['is_fixed_line'],
            'is_voip': best_format['is_voip'],
            'is_toll_free': best_format['is_toll_free'],
            'country': best_format['country_name'],
            'region': best_format['region_code'],
            'carrier': best_format['carrier_name'],
            'location': best_format['location'],
            'timezones': best_format['timezones'],
            'confidence_score': best_format['confidence_score'],
            'data_completeness': best_format['data_completeness'],
            'formatted_versions': {
                'international': best_format['international'],
                'national': best_format['national'],
                'e164': best_format['e164'],
                'rfc3966': best_format['rfc3966']
            },
            'processing_time': formatting_result['processing_time']
        }
    
    def _get_format_suggestions(self, country_code: str) -> List[str]:
        """Get format suggestions based on country"""
        suggestions = {
            'IN': [
                '9876543210 (10-digit mobile)',
                '+91 9876543210 (international)',
                '09876543210 (with leading zero)',
                '(+91) 98765-43210 (formatted)'
            ],
            'US': [
                '(555) 123-4567',
                '+1 555 123 4567',
                '5551234567',
                '1-555-123-4567'
            ],
            'GB': [
                '+44 20 7946 0958',
                '020 7946 0958',
                '07911 123456',
                '+44 7911 123456'
            ]
        }
        
        return suggestions.get(country_code, suggestions['IN'])
    
    def get_stats(self) -> Dict[str, Any]:
        """Get formatter statistics"""
        with self.lock:
            total_formats = self.stats['total_formats']
            if total_formats == 0:
                return {
                    'total_formats': 0,
                    'cache_hit_rate': 0.0,
                    'error_rate': 0.0,
                    'average_processing_time': 0.0
                }
            
            cache_hit_rate = self.stats['cache_hits'] / total_formats
            error_rate = self.stats['parsing_errors'] / total_formats
            avg_processing_time = self.stats['total_time'] / total_formats
            
            return {
                'total_formats': total_formats,
                'cache_hits': self.stats['cache_hits'],
                'cache_misses': self.stats['cache_misses'],
                'cache_hit_rate': cache_hit_rate,
                'parsing_errors': self.stats['parsing_errors'],
                'error_rate': error_rate,
                'total_processing_time': self.stats['total_time'],
                'average_processing_time': avg_processing_time
            }
    
    def clear_cache(self):
        """Clear formatter cache"""
        performance_optimizer.clear_caches()
        
        with self.lock:
            self.stats = {
                'total_formats': 0,
                'cache_hits': 0,
                'cache_misses': 0,
                'parsing_errors': 0,
                'total_time': 0.0
            }


# Global cached formatter instance
cached_phone_formatter = CachedPhoneNumberFormatter()


def get_cached_phone_info(phone_number: str, country_code: str = 'IN') -> Dict[str, Any]:
    """
    Get cached phone information with performance optimization
    
    Args:
        phone_number: Phone number to investigate
        country_code: Country context for parsing
        
    Returns:
        Dict with comprehensive phone information
    """
    return cached_phone_formatter.format_phone_number(phone_number, country_code)


def validate_phone_cached(phone_number: str, country_code: str = 'IN') -> Dict[str, Any]:
    """
    Validate phone number with caching
    
    Args:
        phone_number: Phone number to validate
        country_code: Country context for validation
        
    Returns:
        Dict with validation results
    """
    return cached_phone_formatter.validate_and_classify(phone_number, country_code)


def get_formatter_stats() -> Dict[str, Any]:
    """Get phone formatter statistics"""
    return cached_phone_formatter.get_stats()