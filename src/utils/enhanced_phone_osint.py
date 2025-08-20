#!/usr/bin/env python3
"""
Enhanced Phone OSINT Investigation
Provides comprehensive phone number investigation with multiple free sources
"""

import requests
import re
import json
import time
from typing import Dict, List, Any, Optional
import phonenumbers
from phonenumbers import geocoder, carrier, timezone
import logging

logger = logging.getLogger(__name__)

class EnhancedPhoneOSINT:
    """Enhanced Phone OSINT with multiple free investigation sources"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
    
    def investigate_phone(self, phone_number: str, country_code: str = 'IN') -> Dict[str, Any]:
        """Alias for investigate_phone_comprehensive for compatibility"""
        return self.investigate_phone_comprehensive(phone_number, country_code)
    
    def investigate_phone_comprehensive(self, phone_number: str, country_code: str = 'IN') -> Dict[str, Any]:
        """
        Comprehensive phone investigation using multiple free sources
        
        Args:
            phone_number: Phone number to investigate
            country_code: Country code for context
            
        Returns:
            Dict with comprehensive investigation results
        """
        results = {
            'phone_number': phone_number,
            'country_code': country_code,
            'investigation_timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
            'sources_used': [],
            'technical_analysis': {},
            'carrier_info': {},
            'location_info': {},
            'social_presence': {},
            'business_connections': {},
            'reputation_analysis': {},
            'osint_resources': [],
            'investigation_summary': '',
            'confidence_score': 0.0
        }
        
        try:
            # 1. Technical Analysis using libphonenumber
            tech_analysis = self._analyze_technical_details(phone_number, country_code)
            results['technical_analysis'] = tech_analysis
            results['sources_used'].append('libphonenumber')
            
            # 2. Carrier and Location Information
            carrier_info = self._get_carrier_location_info(phone_number, country_code)
            results['carrier_info'] = carrier_info
            results['location_info'] = carrier_info.get('location', {})
            
            # 3. Social Media Presence Check
            social_info = self._check_social_presence(phone_number)
            results['social_presence'] = social_info
            
            # 4. Business Connection Analysis
            business_info = self._analyze_business_connections(phone_number)
            results['business_connections'] = business_info
            
            # 5. Reputation and Spam Analysis
            reputation_info = self._analyze_reputation(phone_number)
            results['reputation_analysis'] = reputation_info
            
            # 6. Generate OSINT Resources
            osint_resources = self._generate_osint_resources(phone_number, country_code)
            results['osint_resources'] = osint_resources
            
            # 7. Calculate confidence score
            confidence = self._calculate_confidence_score(results)
            results['confidence_score'] = confidence
            
            # 8. Generate investigation summary
            summary = self._generate_investigation_summary(results)
            results['investigation_summary'] = summary
            
            return results
            
        except Exception as e:
            logger.error(f"Phone investigation error: {e}")
            results['error'] = str(e)
            return results
    
    def _analyze_technical_details(self, phone_number: str, country_code: str) -> Dict[str, Any]:
        """Analyze technical details using libphonenumber"""
        try:
            # Parse the phone number
            parsed = phonenumbers.parse(phone_number, country_code)
            
            # Get various details
            analysis = {
                'is_valid': phonenumbers.is_valid_number(parsed),
                'is_possible': phonenumbers.is_possible_number(parsed),
                'country_code': parsed.country_code,
                'national_number': parsed.national_number,
                'international_format': phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.INTERNATIONAL),
                'national_format': phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.NATIONAL),
                'e164_format': phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.E164),
                'number_type': self._get_number_type_description(phonenumbers.number_type(parsed)),
                'carrier': carrier.name_for_number(parsed, 'en'),
                'location': geocoder.description_for_number(parsed, 'en'),
                'timezones': timezone.time_zones_for_number(parsed)
            }
            
            return analysis
            
        except Exception as e:
            return {'error': str(e), 'is_valid': False}
    
    def _get_number_type_description(self, number_type) -> str:
        """Convert number type to readable description"""
        type_map = {
            0: 'Fixed Line',
            1: 'Mobile',
            2: 'Fixed Line or Mobile',
            3: 'Toll Free',
            4: 'Premium Rate',
            5: 'Shared Cost',
            6: 'VoIP',
            7: 'Personal Number',
            8: 'Pager',
            9: 'UAN',
            10: 'Voicemail',
            99: 'Unknown'
        }
        return type_map.get(number_type, 'Unknown')
    
    def _get_carrier_location_info(self, phone_number: str, country_code: str) -> Dict[str, Any]:
        """Get enhanced carrier and location information"""
        try:
            parsed = phonenumbers.parse(phone_number, country_code)
            
            info = {
                'carrier_name': carrier.name_for_number(parsed, 'en'),
                'location': {
                    'description': geocoder.description_for_number(parsed, 'en'),
                    'country': geocoder.country_name_for_number(parsed, 'en'),
                    'region': geocoder.description_for_number(parsed, 'en')
                },
                'timezones': list(timezone.time_zones_for_number(parsed)),
                'country_calling_code': f"+{parsed.country_code}"
            }
            
            # Add Indian-specific carrier analysis
            if country_code == 'IN':
                info.update(self._analyze_indian_carrier(str(parsed.national_number)))
            
            return info
            
        except Exception as e:
            return {'error': str(e)}
    
    def _analyze_indian_carrier(self, national_number: str) -> Dict[str, Any]:
        """Analyze Indian carrier patterns"""
        if len(national_number) != 10:
            return {}
        
        first_digit = national_number[0]
        first_three = national_number[:3]
        first_four = national_number[:4]
        
        # Indian carrier patterns
        carrier_patterns = {
            'Jio': {
                'patterns': ['70', '71', '72', '73', '74', '75', '76', '77', '78', '79', '88', '89'],
                'description': 'Reliance Jio - 4G Network'
            },
            'Airtel': {
                'patterns': ['98765', '99999', '97', '96', '95', '94', '93', '92', '91', '90'],
                'description': 'Bharti Airtel - Major Operator'
            },
            'Vi (Vodafone Idea)': {
                'patterns': ['99', '98', '97', '96', '95', '94', '93', '92'],
                'description': 'Vodafone Idea Limited'
            },
            'BSNL': {
                'patterns': ['94', '95', '96', '97', '98', '99'],
                'description': 'Bharat Sanchar Nigam Limited'
            }
        }
        
        detected_carrier = 'Unknown'
        for carrier_name, data in carrier_patterns.items():
            for pattern in data['patterns']:
                if national_number.startswith(pattern):
                    detected_carrier = carrier_name
                    break
            if detected_carrier != 'Unknown':
                break
        
        # Circle analysis for India
        circle_info = self._get_indian_circle_info(national_number)
        
        return {
            'indian_carrier': detected_carrier,
            'carrier_description': carrier_patterns.get(detected_carrier, {}).get('description', ''),
            'telecom_circle': circle_info,
            'mnp_possible': 'Yes' if detected_carrier in ['Jio', 'Airtel', 'Vi (Vodafone Idea)'] else 'Limited'
        }
    
    def _get_indian_circle_info(self, national_number: str) -> Dict[str, Any]:
        """Get Indian telecom circle information"""
        first_four = national_number[:4]
        
        # Major metro circles
        metro_circles = {
            'Delhi': ['9810', '9811', '9812', '9813', '9814', '9815', '7011', '7012'],
            'Mumbai': ['9820', '9821', '9822', '9823', '9824', '9825', '7021', '7022'],
            'Kolkata': ['9830', '9831', '9832', '9833', '9834', '9835', '7031', '7032'],
            'Chennai': ['9840', '9841', '9842', '9843', '9844', '9845', '7041', '7042'],
            'Bangalore': ['9880', '9881', '9882', '9883', '9884', '9885', '8080', '8081'],
            'Hyderabad': ['9848', '9849', '9850', '9851', '9852', '9853', '7048', '7049']
        }
        
        for circle, patterns in metro_circles.items():
            if first_four in patterns:
                return {
                    'circle': f'{circle} Metro',
                    'type': 'Metro Circle',
                    'confidence': 'High'
                }
        
        return {
            'circle': 'Other Circle',
            'type': 'State Circle',
            'confidence': 'Medium'
        }
    
    def _check_social_presence(self, phone_number: str) -> Dict[str, Any]:
        """Check social media presence indicators"""
        # This would normally check various social platforms
        # For now, providing structure for future implementation
        
        social_info = {
            'whatsapp_likely': True if phone_number.startswith(('+91', '91')) else False,
            'telegram_searchable': True,
            'social_platforms': {
                'whatsapp': {
                    'likely_present': True if phone_number.startswith(('+91', '91')) else False,
                    'reason': 'High WhatsApp adoption in India' if phone_number.startswith(('+91', '91')) else 'Unknown region'
                },
                'telegram': {
                    'searchable': True,
                    'method': 'Username search by phone'
                },
                'signal': {
                    'possible': True,
                    'privacy_focused': True
                }
            },
            'search_methods': [
                'WhatsApp Web contact check',
                'Telegram username discovery',
                'Social media reverse lookup',
                'People search engines'
            ]
        }
        
        return social_info
    
    def _analyze_business_connections(self, phone_number: str) -> Dict[str, Any]:
        """Analyze potential business connections"""
        business_info = {
            'business_likelihood': 'Low',
            'indicators': [],
            'search_resources': [
                'Google Business listings',
                'Yellow Pages India',
                'JustDial business directory',
                'LinkedIn company search',
                'Domain WHOIS records'
            ],
            'verification_methods': [
                'Google My Business lookup',
                'Company registration search',
                'Professional network analysis',
                'Website contact information'
            ]
        }
        
        # Analyze number patterns for business likelihood
        clean_number = re.sub(r'[^\d]', '', phone_number)
        
        # Business number patterns (heuristic)
        if len(clean_number) >= 10:
            last_four = clean_number[-4:]
            if last_four in ['0000', '1111', '2222', '3333', '4444', '5555', '6666', '7777', '8888', '9999']:
                business_info['business_likelihood'] = 'High'
                business_info['indicators'].append('Sequential/repeated digits pattern')
            elif last_four.endswith('00') or last_four.endswith('11'):
                business_info['business_likelihood'] = 'Medium'
                business_info['indicators'].append('Business-like number pattern')
        
        return business_info
    
    def _analyze_reputation(self, phone_number: str) -> Dict[str, Any]:
        """Analyze phone number reputation"""
        reputation_info = {
            'spam_likelihood': 'Unknown',
            'reputation_sources': [
                'Truecaller community reports',
                'Should I Answer database',
                'CallApp spam detection',
                'Hiya caller ID',
                'Community spam reports'
            ],
            'verification_methods': [
                'Multiple caller ID apps',
                'Community feedback',
                'Spam database lookup',
                'Call pattern analysis'
            ],
            'safety_score': 'Unknown',
            'recommendations': [
                'Check multiple caller ID apps',
                'Verify through official channels',
                'Be cautious with unknown numbers',
                'Report spam if confirmed'
            ]
        }
        
        return reputation_info
    
    def _generate_osint_resources(self, phone_number: str, country_code: str) -> List[Dict[str, Any]]:
        """Generate comprehensive OSINT resources for phone investigation"""
        clean_number = re.sub(r'[^\d+]', '', phone_number)
        
        resources = [
            {
                'category': 'Caller ID & Reputation',
                'tools': [
                    {
                        'name': 'Truecaller',
                        'url': f'https://www.truecaller.com/search/in/{clean_number}',
                        'description': 'Community-based caller ID and spam detection',
                        'free': True
                    },
                    {
                        'name': 'Should I Answer',
                        'url': f'https://www.shouldianswer.com/phone-number/{clean_number}',
                        'description': 'Crowd-sourced phone number reputation',
                        'free': True
                    },
                    {
                        'name': 'Sync.ME',
                        'url': f'https://sync.me/search/?q={clean_number}',
                        'description': 'Social profile finder by phone number',
                        'free': True
                    }
                ]
            },
            {
                'category': 'Reverse Phone Lookup',
                'tools': [
                    {
                        'name': 'FindAndTrace',
                        'url': f'https://www.findandtrace.com/trace-mobile-number-location',
                        'description': 'Mobile number location tracing',
                        'free': True
                    },
                    {
                        'name': 'Mobile Number Tracker',
                        'url': f'https://www.mobilenumbertracker.com/',
                        'description': 'Track mobile number location and operator',
                        'free': True
                    },
                    {
                        'name': 'Phone Number Lookup',
                        'url': f'https://www.phonevalidator.com/index.aspx',
                        'description': 'Validate and lookup phone numbers',
                        'free': True
                    }
                ]
            },
            {
                'category': 'Social Media Search',
                'tools': [
                    {
                        'name': 'WhatsApp Web',
                        'url': 'https://web.whatsapp.com/',
                        'description': 'Check if number has WhatsApp account',
                        'free': True,
                        'method': 'Add contact and check profile'
                    },
                    {
                        'name': 'Telegram',
                        'url': 'https://t.me/',
                        'description': 'Search for Telegram username by phone',
                        'free': True,
                        'method': 'Use @username search'
                    },
                    {
                        'name': 'Facebook People Search',
                        'url': f'https://www.facebook.com/search/people/?q={clean_number}',
                        'description': 'Search Facebook profiles by phone number',
                        'free': True
                    }
                ]
            },
            {
                'category': 'Business Directory',
                'tools': [
                    {
                        'name': 'JustDial',
                        'url': f'https://www.justdial.com/search/index/nct/{clean_number}',
                        'description': 'Indian business directory search',
                        'free': True
                    },
                    {
                        'name': 'Google My Business',
                        'url': f'https://www.google.com/search?q="{clean_number}"',
                        'description': 'Google search for business listings',
                        'free': True
                    },
                    {
                        'name': 'Yellow Pages',
                        'url': f'https://www.yellowpages.com/search?search_terms={clean_number}',
                        'description': 'Business directory lookup',
                        'free': True
                    }
                ]
            },
            {
                'category': 'Advanced OSINT',
                'tools': [
                    {
                        'name': 'Google Dorking',
                        'url': f'https://www.google.com/search?q="{clean_number}" OR "{phone_number}"',
                        'description': 'Google search with phone number',
                        'free': True,
                        'method': 'Use quotes for exact match'
                    },
                    {
                        'name': 'Bing Search',
                        'url': f'https://www.bing.com/search?q="{clean_number}"',
                        'description': 'Bing search engine lookup',
                        'free': True
                    },
                    {
                        'name': 'DuckDuckGo',
                        'url': f'https://duckduckgo.com/?q="{clean_number}"',
                        'description': 'Privacy-focused search engine',
                        'free': True
                    }
                ]
            }
        ]
        
        return resources
    
    def _calculate_confidence_score(self, results: Dict[str, Any]) -> float:
        """Calculate overall confidence score for the investigation"""
        score = 0.0
        max_score = 100.0
        
        # Technical analysis confidence
        if results['technical_analysis'].get('is_valid'):
            score += 30.0
        elif results['technical_analysis'].get('is_possible'):
            score += 15.0
        
        # Carrier information confidence
        if results['carrier_info'].get('carrier_name'):
            score += 20.0
        
        # Location information confidence
        if results['location_info'].get('description'):
            score += 15.0
        
        # Social presence indicators
        if results['social_presence'].get('whatsapp_likely'):
            score += 10.0
        
        # Business connection analysis
        if results['business_connections'].get('business_likelihood') != 'Low':
            score += 10.0
        
        # OSINT resources availability
        if len(results['osint_resources']) > 0:
            score += 15.0
        
        return min(score, max_score)
    
    def _generate_investigation_summary(self, results: Dict[str, Any]) -> str:
        """Generate a comprehensive investigation summary"""
        phone = results['phone_number']
        tech = results['technical_analysis']
        carrier = results['carrier_info']
        location = results['location_info']
        confidence = results['confidence_score']
        
        summary_parts = []
        
        # Basic validation
        if tech.get('is_valid'):
            summary_parts.append(f"✅ Valid phone number")
        elif tech.get('is_possible'):
            summary_parts.append(f"⚠️ Possibly valid phone number")
        else:
            summary_parts.append(f"❌ Invalid phone number format")
        
        # Carrier information
        if carrier.get('carrier_name'):
            summary_parts.append(f"📱 Carrier: {carrier['carrier_name']}")
        
        # Location information
        if location.get('description'):
            summary_parts.append(f"📍 Location: {location['description']}")
        
        # Number type
        if tech.get('number_type'):
            summary_parts.append(f"📞 Type: {tech['number_type']}")
        
        # Indian-specific information
        if carrier.get('indian_carrier'):
            summary_parts.append(f"🇮🇳 Indian Carrier: {carrier['indian_carrier']}")
        
        if carrier.get('telecom_circle', {}).get('circle'):
            summary_parts.append(f"🏙️ Circle: {carrier['telecom_circle']['circle']}")
        
        # Confidence score
        summary_parts.append(f"🎯 Confidence: {confidence:.1f}%")
        
        # Resource count
        resource_count = sum(len(cat['tools']) for cat in results['osint_resources'])
        summary_parts.append(f"🔍 OSINT Resources: {resource_count} tools available")
        
        return " | ".join(summary_parts)

# Global instance
enhanced_phone_osint = EnhancedPhoneOSINT()

def get_comprehensive_phone_info(phone_number: str, country_code: str = 'IN') -> Dict[str, Any]:
    """Get comprehensive phone information using enhanced OSINT"""
    return enhanced_phone_osint.investigate_phone_comprehensive(phone_number, country_code)