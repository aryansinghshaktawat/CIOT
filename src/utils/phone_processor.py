#!/usr/bin/env python3
"""
Phone Number Processing Utility for CIOT
Handles multiple input formats using Google's libphonenumber
"""

import phonenumbers
from phonenumbers import geocoder, carrier, timezone
from phonenumbers.phonenumberutil import NumberParseException
import re
from typing import Dict, Optional, List

class PhoneNumberProcessor:
    """Professional phone number processing using Google's libphonenumber"""
    
    def __init__(self):
        self.default_region = "IN"  # Default to India
    
    def parse_and_format_phone(self, phone_input: str, region: str = None) -> Dict:
        """Parse and format phone number from multiple input formats"""
        try:
            if region is None:
                region = self.default_region
            
            # Clean input
            original_input = phone_input.strip()
            
            # Handle various input formats
            formatted_inputs = self._generate_format_variations(original_input)
            
            parsed_number = None
            successful_format = None
            
            # Try parsing with different formats
            for format_attempt in formatted_inputs:
                try:
                    parsed_number = phonenumbers.parse(format_attempt, region)
                    if phonenumbers.is_valid_number(parsed_number):
                        successful_format = format_attempt
                        break
                except NumberParseException:
                    continue
            
            if parsed_number is None:
                return {
                    'success': False,
                    'error': 'Could not parse phone number in any recognized format',
                    'original_input': original_input,
                    'attempted_formats': formatted_inputs
                }
            
            # Extract comprehensive information
            result = {
                'success': True,
                'original_input': original_input,
                'successful_format': successful_format,
                'parsed_successfully': True
            }
            
            # Basic number information
            result.update(self._extract_basic_info(parsed_number))
            
            # Geographic information
            result.update(self._extract_geographic_info(parsed_number))
            
            # Carrier information
            result.update(self._extract_carrier_info(parsed_number))
            
            # Technical information
            result.update(self._extract_technical_info(parsed_number))
            
            # Validation information
            result.update(self._extract_validation_info(parsed_number))
            
            return result
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Phone processing error: {str(e)}',
                'original_input': phone_input
            }
    
    def _generate_format_variations(self, phone_input: str) -> List[str]:
        """Generate different format variations to try parsing"""
        variations = [phone_input]  # Original input first
        
        # Clean version (digits only)
        clean = re.sub(r'[^\d]', '', phone_input)
        if clean != phone_input:
            variations.append(clean)
        
        # Add country code variations for Indian numbers
        if len(clean) == 10 and clean[0] in ['6', '7', '8', '9']:
            variations.extend([
                f"+91{clean}",
                f"91{clean}",
                f"0{clean}",
                f"+91 {clean}",
                f"+91 {clean[:5]} {clean[5:]}",
                f"91 {clean[:5]} {clean[5:]}"
            ])
        
        # Add US/Canada variations
        elif len(clean) == 10 and clean[0] in ['2', '3', '4', '5', '6', '7', '8', '9']:
            variations.extend([
                f"+1{clean}",
                f"1{clean}",
                f"+1 {clean}",
                f"+1 ({clean[:3]}) {clean[3:6]}-{clean[6:]}",
                f"({clean[:3]}) {clean[3:6]}-{clean[6:]}"
            ])
        
        # Handle already formatted numbers
        if '+' in phone_input:
            # Try without spaces and formatting
            no_spaces = re.sub(r'[\s\-\(\)]', '', phone_input)
            if no_spaces not in variations:
                variations.append(no_spaces)
        
        return variations
    
    def _extract_basic_info(self, parsed_number) -> Dict:
        """Extract basic phone number information"""
        return {
            'country_code': parsed_number.country_code,
            'national_number': parsed_number.national_number,
            'international_format': phonenumbers.format_number(parsed_number, phonenumbers.PhoneNumberFormat.INTERNATIONAL),
            'national_format': phonenumbers.format_number(parsed_number, phonenumbers.PhoneNumberFormat.NATIONAL),
            'e164_format': phonenumbers.format_number(parsed_number, phonenumbers.PhoneNumberFormat.E164),
            'rfc3966_format': phonenumbers.format_number(parsed_number, phonenumbers.PhoneNumberFormat.RFC3966)
        }
    
    def _extract_geographic_info(self, parsed_number) -> Dict:
        """Extract geographic information"""
        try:
            # Get country information
            country_name = geocoder.country_name_for_number(parsed_number, "en")
            region_code = geocoder.region_code_for_number(parsed_number)
            
            # Get location description
            location_description = geocoder.description_for_number(parsed_number, "en")
            
            # Get timezone information
            timezones = timezone.time_zones_for_number(parsed_number)
            
            return {
                'country_name': country_name or 'Unknown',
                'region_code': region_code or 'Unknown',
                'location_description': location_description or 'Unknown',
                'timezones': list(timezones) if timezones else ['Unknown'],
                'primary_timezone': list(timezones)[0] if timezones else 'Unknown'
            }
        except Exception as e:
            return {
                'country_name': 'Unknown',
                'region_code': 'Unknown', 
                'location_description': 'Unknown',
                'timezones': ['Unknown'],
                'primary_timezone': 'Unknown',
                'geo_error': str(e)
            }
    
    def _extract_carrier_info(self, parsed_number) -> Dict:
        """Extract carrier information"""
        try:
            # Get carrier information
            carrier_name = carrier.name_for_number(parsed_number, "en")
            
            return {
                'carrier_name': carrier_name or 'Unknown',
                'carrier_available': bool(carrier_name)
            }
        except Exception as e:
            return {
                'carrier_name': 'Unknown',
                'carrier_available': False,
                'carrier_error': str(e)
            }
    
    def _extract_technical_info(self, parsed_number) -> Dict:
        """Extract technical phone number information"""
        try:
            number_type = phonenumbers.number_type(parsed_number)
            
            # Map number types to readable strings
            type_mapping = {
                phonenumbers.PhoneNumberType.MOBILE: 'Mobile',
                phonenumbers.PhoneNumberType.FIXED_LINE: 'Fixed Line',
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
            
            return {
                'number_type': type_mapping.get(number_type, 'Unknown'),
                'number_type_code': number_type,
                'is_mobile': number_type == phonenumbers.PhoneNumberType.MOBILE,
                'is_fixed_line': number_type == phonenumbers.PhoneNumberType.FIXED_LINE,
                'is_toll_free': number_type == phonenumbers.PhoneNumberType.TOLL_FREE,
                'is_premium': number_type == phonenumbers.PhoneNumberType.PREMIUM_RATE
            }
        except Exception as e:
            return {
                'number_type': 'Unknown',
                'number_type_code': None,
                'is_mobile': False,
                'is_fixed_line': False,
                'is_toll_free': False,
                'is_premium': False,
                'technical_error': str(e)
            }
    
    def _extract_validation_info(self, parsed_number) -> Dict:
        """Extract validation information"""
        try:
            is_valid = phonenumbers.is_valid_number(parsed_number)
            is_possible = phonenumbers.is_possible_number(parsed_number)
            
            # Get validation result details
            validation_result = phonenumbers.is_valid_number_for_region(parsed_number, self.default_region)
            
            return {
                'is_valid': is_valid,
                'is_possible': is_possible,
                'is_valid_for_region': validation_result,
                'validation_status': 'Valid' if is_valid else ('Possible' if is_possible else 'Invalid')
            }
        except Exception as e:
            return {
                'is_valid': False,
                'is_possible': False,
                'is_valid_for_region': False,
                'validation_status': 'Error',
                'validation_error': str(e)
            }
    
    def get_supported_formats_example(self) -> Dict:
        """Get examples of supported input formats"""
        return {
            'indian_formats': [
                '9876543210',
                '+91 9876543210', 
                '91 9876543210',
                '09876543210',
                '+91 98765 43210',
                '91-98765-43210',
                '(+91) 9876543210'
            ],
            'us_formats': [
                '5551234567',
                '+1 5551234567',
                '1 5551234567',
                '(555) 123-4567',
                '+1 (555) 123-4567',
                '555-123-4567'
            ],
            'international_formats': [
                '+44 20 7946 0958',  # UK
                '+33 1 42 86 83 26',  # France
                '+49 30 12345678',    # Germany
                '+86 138 0013 8000'   # China
            ]
        }

def process_phone_number(phone_input: str, region: str = "IN") -> Dict:
    """Main function to process phone number with multiple format support"""
    processor = PhoneNumberProcessor()
    return processor.parse_and_format_phone(phone_input, region)