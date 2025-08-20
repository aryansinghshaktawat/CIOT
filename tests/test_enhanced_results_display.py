"""
Tests for Enhanced Investigation Results Display System
Tests the enhanced phone investigation results display with organized intelligence sections
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
import sys
import os

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))


class TestEnhancedResultsDisplay(unittest.TestCase):
    """Test enhanced investigation results display functionality"""
    
    def setUp(self):
        """Set up test fixtures"""
        # Create a mock tab instance with just the methods we need to test
        self.tab = Mock()
        
        # Import the actual methods we want to test
        from gui.tabs.surface_web_tab import SurfaceWebTab
        
        # Bind the actual methods to our mock instance
        self.tab._format_technical_intelligence = SurfaceWebTab._format_technical_intelligence.__get__(self.tab)
        self.tab._format_security_intelligence = SurfaceWebTab._format_security_intelligence.__get__(self.tab)
        self.tab._format_social_intelligence = SurfaceWebTab._format_social_intelligence.__get__(self.tab)
        self.tab._format_business_intelligence = SurfaceWebTab._format_business_intelligence.__get__(self.tab)
        self.tab._format_pattern_intelligence = SurfaceWebTab._format_pattern_intelligence.__get__(self.tab)
        self.tab._format_historical_intelligence = SurfaceWebTab._format_historical_intelligence.__get__(self.tab)
        self.tab._format_confidence_assessment = SurfaceWebTab._format_confidence_assessment.__get__(self.tab)
        self.tab._format_osint_resources = SurfaceWebTab._format_osint_resources.__get__(self.tab)
        self.tab._format_investigation_methodology = SurfaceWebTab._format_investigation_methodology.__get__(self.tab)
        self.tab._format_legal_compliance = SurfaceWebTab._format_legal_compliance.__get__(self.tab)
        self.tab._format_enhanced_phone_results = SurfaceWebTab._format_enhanced_phone_results.__get__(self.tab)
        self.tab.format_comprehensive_results = SurfaceWebTab.format_comprehensive_results.__get__(self.tab)
        self.tab._format_standard_results = SurfaceWebTab._format_standard_results.__get__(self.tab)
    
    def test_format_enhanced_phone_results_structure(self):
        """Test that enhanced phone results have proper structure"""
        target = "+91 9876543210"
        links = [
            {'name': 'Test Link', 'url': 'https://example.com', 'category': 'Search Engines'}
        ]
        real_data = {
            'success': True,
            'original_input': '+91 9876543210',
            'international_format': '+91 98765 43210',
            'national_format': '98765 43210',
            'e164_format': '+919876543210',
            'rfc3966_format': 'tel:+91-98765-43210',
            'country_name': 'India',
            'country_code': 91,
            'region_code': 'IN',
            'location': 'India',
            'timezones': ['Asia/Kolkata'],
            'number_type': 'Mobile',
            'is_mobile': True,
            'is_fixed_line': False,
            'is_valid': True,
            'is_possible': True,
            'carrier_name': 'Unknown',
            'formatting_method': 'libphonenumber',
            'aggregated_intelligence': {
                'overall_confidence': 85.5,
                'confidence_level': 'HIGH',
                'sources_used': ['libphonenumber', 'abstractapi'],
                'successful_sources': 2,
                'total_sources': 3,
                'processing_time': 2.5,
                'merged_data': {
                    'carrier': 'Airtel',
                    'operator': 'Bharti Airtel',
                    'line_type': 'Mobile'
                }
            }
        }
        
        result = self.tab._format_enhanced_phone_results(target, links, real_data)
        
        # Check main structure
        self.assertIn("ENHANCED PHONE NUMBER INVESTIGATION", result)
        self.assertIn("TECHNICAL INTELLIGENCE", result)
        self.assertIn("SECURITY INTELLIGENCE", result)
        self.assertIn("SOCIAL INTELLIGENCE", result)
        self.assertIn("BUSINESS INTELLIGENCE", result)
        self.assertIn("PATTERN INTELLIGENCE", result)
        self.assertIn("HISTORICAL INTELLIGENCE", result)
        self.assertIn("INVESTIGATION CONFIDENCE & QUALITY ASSESSMENT", result)
        self.assertIn("OSINT RESOURCES & TOOLS", result)
        self.assertIn("INVESTIGATION METHODOLOGY & RECOMMENDATIONS", result)
        self.assertIn("LEGAL & ETHICAL COMPLIANCE", result)
    
    def test_format_technical_intelligence_section(self):
        """Test technical intelligence section formatting"""
        real_data = {
            'original_input': '+91 9876543210',
            'international_format': '+91 98765 43210',
            'national_format': '98765 43210',
            'e164_format': '+919876543210',
            'rfc3966_format': 'tel:+91-98765-43210',
            'country_name': 'India',
            'country_code': 91,
            'region_code': 'IN',
            'location': 'India',
            'timezones': ['Asia/Kolkata'],
            'number_type': 'Mobile',
            'is_mobile': True,
            'is_fixed_line': False,
            'is_valid': True,
            'is_possible': True,
            'carrier_name': 'Airtel',
            'formatting_method': 'libphonenumber for IN'
        }
        
        result = self.tab._format_technical_intelligence(real_data)
        
        # Check technical intelligence content
        self.assertIn("TECHNICAL INTELLIGENCE", result)
        self.assertIn("NUMBER FORMATTING:", result)
        self.assertIn("Original Input: +91 9876543210", result)
        self.assertIn("International: +91 98765 43210", result)
        self.assertIn("National: 98765 43210", result)
        self.assertIn("E164: +919876543210", result)
        self.assertIn("GEOGRAPHIC DATA:", result)
        self.assertIn("Country: India (91)", result)
        self.assertIn("Region: IN", result)
        self.assertIn("Location: India", result)
        self.assertIn("Timezones: Asia/Kolkata", result)
        self.assertIn("NUMBER CLASSIFICATION:", result)
        self.assertIn("Valid: ✅ Yes", result)
        self.assertIn("Type: Mobile", result)
        self.assertIn("Mobile: ✅ Yes", result)
        self.assertIn("Fixed Line: ❌ No", result)
        self.assertIn("CARRIER INFORMATION:", result)
        self.assertIn("libphonenumber Carrier: Airtel", result)
    
    def test_format_security_intelligence_section(self):
        """Test security intelligence section formatting"""
        real_data = {
            'aggregated_intelligence': {
                'merged_data': {
                    'spam_risk_score': 0.2,
                    'reputation_status': 'Clean',
                    'breach_count': 0
                }
            },
            'investigation_confidence': 'High'
        }
        
        result = self.tab._format_security_intelligence(real_data)
        
        # Check security intelligence content
        self.assertIn("SECURITY INTELLIGENCE", result)
        self.assertIn("REPUTATION ASSESSMENT:", result)
        self.assertIn("Investigation Confidence: High", result)
        self.assertIn("DATA BREACH ANALYSIS:", result)
        self.assertIn("Breach Status: ✅ No known data breaches", result)
    
    def test_format_social_intelligence_section(self):
        """Test social intelligence section formatting"""
        real_data = {
            'whatsapp_present': True,
            'whatsapp_privacy_level': 'Medium',
            'aggregated_intelligence': {
                'merged_data': {
                    'telegram_presence': False,
                    'facebook_presence': False,
                    'instagram_presence': False,
                    'linkedin_presence': False
                }
            }
        }
        
        result = self.tab._format_social_intelligence(real_data)
        
        # Check social intelligence content
        self.assertIn("SOCIAL INTELLIGENCE", result)
        self.assertIn("SOCIAL MEDIA PRESENCE:", result)
        self.assertIn("WhatsApp: ✅ Present", result)
        self.assertIn("Privacy Level: Medium", result)
        self.assertIn("Telegram: ❌ Not detected", result)
        self.assertIn("Facebook: ❌ Not detected", result)
        self.assertIn("Instagram: ❌ Not detected", result)
        self.assertIn("Linkedin: ❌ Not detected", result)
    
    def test_format_business_intelligence_section(self):
        """Test business intelligence section formatting"""
        real_data = {
            'aggregated_intelligence': {
                'merged_data': {
                    'domains_found': [
                        {'domain': 'example.com', 'status': 'active', 'registrar': 'GoDaddy'},
                        {'domain': 'test.org', 'status': 'expired', 'registrar': 'Namecheap'}
                    ],
                    'business_connections': [
                        {'organization': 'Test Corp', 'contact_type': 'Admin'},
                        {'organization': 'Example LLC', 'contact_type': 'Tech'}
                    ]
                }
            }
        }
        
        result = self.tab._format_business_intelligence(real_data)
        
        # Check business intelligence content
        self.assertIn("BUSINESS INTELLIGENCE", result)
        self.assertIn("DOMAIN ASSOCIATIONS:", result)
        self.assertIn("Total Domains: 2", result)
        self.assertIn("Active Domains: 1", result)
        self.assertIn("example.com: active (GoDaddy)", result)
        self.assertIn("test.org: expired (Namecheap)", result)
        self.assertIn("Business Connections: 2 found", result)
        self.assertIn("Test Corp: Admin", result)
        self.assertIn("Example LLC: Tech", result)
    
    def test_format_pattern_intelligence_section(self):
        """Test pattern intelligence section formatting"""
        real_data = {
            'aggregated_intelligence': {
                'merged_data': {
                    'related_numbers': [
                        {
                            'number': '+919876543211',
                            'relationship_type': 'Sequential',
                            'confidence_score': 0.85
                        },
                        {
                            'number': '+919876543212',
                            'relationship_type': 'Sequential',
                            'confidence_score': 0.75
                        }
                    ],
                    'bulk_registration': {
                        'detected': True,
                        'confidence_score': 0.9,
                        'block_size': 100,
                        'pattern_type': 'Sequential'
                    },
                    'sequential_patterns': {
                        'found': True,
                        'pattern_type': 'Consecutive',
                        'confidence_score': 0.8
                    }
                }
            }
        }
        
        result = self.tab._format_pattern_intelligence(real_data)
        
        # Check pattern intelligence content
        self.assertIn("PATTERN INTELLIGENCE", result)
        self.assertIn("RELATED NUMBER ANALYSIS:", result)
        self.assertIn("Related Numbers: 2 found", result)
        self.assertIn("High Confidence: 2 numbers", result)
        self.assertIn("+919876543211: Sequential (Confidence: 85.0%)", result)
        self.assertIn("Bulk Registration: 🚨 Detected (Confidence: 90.0%)", result)
        self.assertIn("Block Size: 100", result)
        self.assertIn("Pattern Type: Sequential", result)
        self.assertIn("Sequential Patterns: ✅ Found", result)
        self.assertIn("Pattern Type: Consecutive", result)
        self.assertIn("Confidence: 80.0%", result)
    
    def test_format_confidence_assessment_section(self):
        """Test investigation confidence and quality assessment section"""
        real_data = {
            'formatting_success': True,
            'api_data_available': True,
            'total_apis_used': 3,
            'is_valid': True,
            'aggregated_intelligence': {
                'overall_confidence': 87.5,
                'confidence_level': 'HIGH',
                'sources_used': ['libphonenumber', 'abstractapi', 'neutrino'],
                'successful_sources': 3,
                'total_sources': 4,
                'processing_time': 3.2
            }
        }
        
        result = self.tab._format_confidence_assessment(real_data)
        
        # Check confidence assessment content
        self.assertIn("INVESTIGATION CONFIDENCE & QUALITY ASSESSMENT", result)
        self.assertIn("OVERALL ASSESSMENT:", result)
        self.assertIn("Investigation Confidence: 87.5% (HIGH)", result)
        self.assertIn("Quality Level: 🟡 Good - Reliable for most purposes", result)
        self.assertIn("Data Sources: 3/4 sources successful", result)
        self.assertIn("Processing Time: 3.20 seconds", result)
        self.assertIn("Sources Used: libphonenumber, abstractapi, neutrino", result)
        self.assertIn("QUALITY INDICATORS:", result)
        self.assertIn("Number Formatting: ✅ Successful", result)
        self.assertIn("API Data: ✅ Available (3 APIs)", result)
        self.assertIn("Number Validation: ✅ Valid number", result)
    
    def test_format_osint_resources_section(self):
        """Test OSINT resources section formatting"""
        links = [
            {'name': 'Google Search', 'url': 'https://google.com/search?q=test', 'category': 'Search Engines'},
            {'name': 'TrueCaller', 'url': 'https://truecaller.com/search/test', 'category': 'Phone Lookup'},
            {'name': 'WhitePages', 'url': 'https://whitepages.com/search/test', 'category': 'Phone Lookup'},
            {'name': 'Social Searcher', 'url': 'https://socialsearcher.com/search/test', 'category': 'Social Media'}
        ]
        
        result = self.tab._format_osint_resources(links)
        
        # Check OSINT resources content
        self.assertIn("OSINT RESOURCES & TOOLS", result)
        self.assertIn("Total Resources: 4 professional OSINT tools", result)
        self.assertIn("Categories: 3 investigation domains", result)
        self.assertIn("Browser Links: Automatically opened for investigation", result)
        self.assertIn("SEARCH ENGINES (1 resources)", result)
        self.assertIn("1. Google Search", result)
        self.assertIn("PHONE LOOKUP (2 resources)", result)
        self.assertIn("1. TrueCaller", result)
        self.assertIn("2. WhitePages", result)
        self.assertIn("SOCIAL MEDIA (1 resources)", result)
        self.assertIn("1. Social Searcher", result)
    
    def test_format_investigation_methodology_section(self):
        """Test investigation methodology section formatting"""
        real_data = {
            'success': True,
            'aggregated_intelligence': {
                'overall_confidence': 82.3
            }
        }
        
        result = self.tab._format_investigation_methodology(real_data)
        
        # Check methodology content
        self.assertIn("INVESTIGATION METHODOLOGY & RECOMMENDATIONS", result)
        self.assertIn("COMPLETED ACTIONS:", result)
        self.assertIn("Target validation and format verification", result)
        self.assertIn("Multi-source intelligence aggregation", result)
        self.assertIn("Professional OSINT resource deployment", result)
        self.assertIn("Confidence scoring and quality assessment", result)
        self.assertIn("RECOMMENDED NEXT STEPS:", result)
        self.assertIn("Review all intelligence sections systematically", result)
        self.assertIn("Cross-reference findings across multiple sources", result)
        self.assertIn("Export comprehensive report for legal compliance", result)
        self.assertIn("INVESTIGATION SUMMARY:", result)
        self.assertIn("Data Quality: High", result)
        self.assertIn("Investigation Status: ✅ Complete", result)
        self.assertIn("Confidence Level: 82.3%", result)
        self.assertIn("Compliance: ✅ Professional standards maintained", result)
    
    def test_format_legal_compliance_section(self):
        """Test legal and ethical compliance section formatting"""
        result = self.tab._format_legal_compliance()
        
        # Check legal compliance content
        self.assertIn("LEGAL & ETHICAL COMPLIANCE", result)
        self.assertIn("COMPLIANCE STANDARDS:", result)
        self.assertIn("Investigation uses only publicly available information", result)
        self.assertIn("All OSINT resources are legitimate and authorized", result)
        self.assertIn("Professional ethical standards maintained throughout", result)
        self.assertIn("Data privacy and protection laws respected", result)
        self.assertIn("IMPORTANT REMINDERS:", result)
        self.assertIn("Ensure proper authorization before investigating individuals", result)
        self.assertIn("Respect platform terms of service and privacy policies", result)
        self.assertIn("Maintain chain of custody for potential legal proceedings", result)
        self.assertIn("Use information responsibly and within legal boundaries", result)
        self.assertIn("ENHANCED PHONE INVESTIGATION COMPLETE - CIOT v3.0 Professional OSINT", result)
    
    def test_standard_results_fallback(self):
        """Test that non-phone investigations use standard formatting"""
        target = "test@example.com"
        lookup_type = "Email Address"
        links = [{'name': 'Test Link', 'url': 'https://example.com', 'category': 'Email'}]
        real_data = {'success': True, 'domain': 'example.com'}
        
        result = self.tab.format_comprehensive_results(target, lookup_type, links, real_data)
        
        # Should use standard formatting for non-phone investigations
        self.assertIn("COMPREHENSIVE INVESTIGATION RESULTS", result)
        self.assertNotIn("ENHANCED PHONE NUMBER INVESTIGATION", result)
        self.assertNotIn("TECHNICAL INTELLIGENCE", result)
    
    def test_add_intelligence_sections_to_pdf_method_exists(self):
        """Test that the PDF intelligence sections method exists and can be called"""
        from gui.tabs.surface_web_tab import SurfaceWebTab
        
        # Check that the method exists
        self.assertTrue(hasattr(SurfaceWebTab, '_add_intelligence_sections_to_pdf'))
        
        # Create a mock PDF and real data
        mock_pdf = Mock()
        real_data = {
            'original_input': '+91 9876543210',
            'international_format': '+91 98765 43210',
            'is_valid': True,
            'aggregated_intelligence': {
                'overall_confidence': 85.0,
                'confidence_level': 'HIGH',
                'sources_used': ['libphonenumber', 'abstractapi'],
                'successful_sources': 2,
                'total_sources': 3,
                'merged_data': {
                    'domains_found': [],
                    'business_connections': []
                }
            }
        }
        
        # Bind the method to our mock tab
        self.tab._add_intelligence_sections_to_pdf = SurfaceWebTab._add_intelligence_sections_to_pdf.__get__(self.tab)
        
        # Call the method - should not raise any exceptions
        try:
            self.tab._add_intelligence_sections_to_pdf(mock_pdf, real_data)
            # Verify PDF methods were called
            self.assertTrue(mock_pdf.set_font.called)
            self.assertTrue(mock_pdf.cell.called)
        except Exception as e:
            self.fail(f"_add_intelligence_sections_to_pdf raised an exception: {e}")


if __name__ == '__main__':
    unittest.main()