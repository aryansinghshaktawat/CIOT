#!/usr/bin/env python3
"""
Unit tests for Enhanced Indian Phone Features
Tests TRAI lookup, porting history, WhatsApp checks, spam databases, and breach datasets
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import unittest
from src.utils.osint_utils import (
    IndianPhoneNumberFormatter,
    check_whatsapp_indian_number,
    check_indian_spam_databases,
    check_indian_breach_datasets,
    get_enhanced_phone_info
)

class TestEnhancedIndianFeatures(unittest.TestCase):
    """Test cases for enhanced Indian phone features"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.formatter = IndianPhoneNumberFormatter()
    
    def test_trai_circle_lookup(self):
        """Test TRAI/DoT circle lookup functionality"""
        # Test metro circles
        metro_cases = [
            ('9810123456', 'Delhi', 'Metro'),
            ('9820123456', 'Mumbai', 'Metro'),
            ('9830123456', 'Kolkata', 'Metro'),
            ('9840123456', 'Chennai', 'Metro'),
        ]
        
        for number, expected_circle, expected_tier in metro_cases:
            with self.subTest(number=number):
                result = self.formatter.get_trai_circle_lookup(number)
                self.assertEqual(result['circle'], expected_circle)
                self.assertEqual(result['tier'], expected_tier)
                self.assertEqual(result['confidence'], 'High')
                self.assertEqual(result['source'], 'TRAI/DoT Official')
    
    def test_sim_porting_history(self):
        """Test SIM porting history analysis"""
        # Test cases with known patterns
        test_cases = [
            ('9876543210', 'Airtel'),  # Airtel original pattern
            ('7012345678', 'Jio'),     # Jio original pattern
            ('9999999999', 'Vodafone'), # Vodafone original pattern
        ]
        
        for number, expected_original in test_cases:
            with self.subTest(number=number):
                result = self.formatter.check_indian_sim_porting_history(number)
                self.assertIn('porting_possible', result)
                self.assertIn('original_operator', result)
                self.assertIn('mnp_status', result)
                self.assertIn('porting_era', result)
                
                if expected_original != 'Unknown':
                    self.assertEqual(result['original_operator'], expected_original)
    
    def test_whatsapp_check(self):
        """Test WhatsApp presence check"""
        result = check_whatsapp_indian_number('9876543210')
        
        self.assertTrue(result.get('success'))
        self.assertIn('whatsapp_data', result)
        
        whatsapp_data = result['whatsapp_data']
        self.assertIn('has_whatsapp', whatsapp_data)
        self.assertIn('privacy_level', whatsapp_data)
        self.assertIn('check_method', whatsapp_data)
        self.assertIn('verification_status', whatsapp_data)
    
    def test_indian_spam_databases(self):
        """Test Indian spam database checks"""
        # Test with known spam pattern
        spam_result = check_indian_spam_databases('9999999999')
        self.assertTrue(spam_result.get('success'))
        self.assertIn('spam_data', spam_result)
        self.assertIn('indian_sources', spam_result)
        
        spam_data = spam_result['spam_data']
        self.assertIn('is_spam', spam_data)
        self.assertIn('spam_confidence', spam_data)
        self.assertIn('databases_checked', spam_data)
        
        # Check Indian sources
        indian_sources = spam_result['indian_sources']
        self.assertIn('Truecaller Community', indian_sources)
        self.assertIn('TRAI DND Registry', indian_sources)
        self.assertIn('DoT Spam Reports', indian_sources)
    
    def test_indian_breach_datasets(self):
        """Test Indian breach dataset checks"""
        result = check_indian_breach_datasets('9876543210')
        
        self.assertTrue(result.get('success'))
        self.assertIn('breach_data', result)
        self.assertIn('databases_available', result)
        
        breach_data = result['breach_data']
        self.assertIn('found_in_breaches', breach_data)
        self.assertIn('breach_count', breach_data)
        self.assertIn('risk_level', breach_data)
        self.assertIn('data_types_exposed', breach_data)
        
        # Check available databases
        databases = result['databases_available']
        self.assertIn('Indian Telecom Data Leak 2019', databases)
        self.assertIn('Indian Banking SMS Leak 2020', databases)
        self.assertIn('Indian E-commerce Leak 2021', databases)
    
    def test_enhanced_phone_info_integration(self):
        """Test integration of all enhanced features in phone info"""
        result = get_enhanced_phone_info('9876543210')
        
        self.assertTrue(result.get('success'))
        
        # Check TRAI data integration
        self.assertIn('trai_circle', result)
        self.assertIn('trai_tier', result)
        self.assertIn('trai_confidence', result)
        
        # Check porting data integration
        self.assertIn('porting_possible', result)
        self.assertIn('original_operator', result)
        self.assertIn('mnp_status_detailed', result)
        
        # Check WhatsApp data integration
        self.assertIn('whatsapp_present', result)
        self.assertIn('whatsapp_privacy_level', result)
        
        # Check spam data integration
        self.assertIn('indian_spam_status', result)
        self.assertIn('spam_confidence', result)
        self.assertIn('spam_databases_checked', result)
        
        # Check breach data integration
        self.assertIn('found_in_indian_breaches', result)
        self.assertIn('breach_risk_level', result)
        self.assertIn('data_types_exposed', result)
        
        # Check enhanced risk assessment
        self.assertIn('risk_factors', result)
        self.assertIn('privacy_risk', result)
    
    def test_jio_number_comprehensive(self):
        """Test comprehensive analysis of Jio number"""
        result = get_enhanced_phone_info('7012345678')
        
        self.assertTrue(result.get('success'))
        self.assertEqual(result.get('indian_operator'), 'Jio')
        self.assertEqual(result.get('trai_circle'), 'Delhi')
        self.assertEqual(result.get('trai_tier'), 'Metro')
        self.assertFalse(result.get('porting_possible'))  # Original Jio number
        self.assertEqual(result.get('original_operator'), 'Jio')
    
    def test_delhi_metro_detection(self):
        """Test Delhi metro circle detection"""
        delhi_numbers = ['9810123456', '9811123456', '9812123456']
        
        for number in delhi_numbers:
            with self.subTest(number=number):
                trai_data = self.formatter.get_trai_circle_lookup(number)
                self.assertEqual(trai_data['circle'], 'Delhi')
                self.assertEqual(trai_data['tier'], 'Metro')
                self.assertEqual(trai_data['state'], 'Delhi')
                self.assertEqual(trai_data['confidence'], 'High')
    
    def test_spam_pattern_detection(self):
        """Test spam pattern detection"""
        spam_numbers = ['9999999999', '8888888888', '7777777777']
        
        for number in spam_numbers:
            with self.subTest(number=number):
                spam_result = check_indian_spam_databases(number)
                spam_data = spam_result['spam_data']
                # These patterns should be detected as spam
                self.assertTrue(spam_data.get('is_spam', False) or spam_data.get('spam_confidence') != 'Low')
    
    def test_breach_risk_assessment(self):
        """Test breach risk assessment"""
        high_risk_number = '9876543210'  # Contains high-risk pattern
        result = check_indian_breach_datasets(high_risk_number)
        
        breach_data = result['breach_data']
        # Should be found in breaches due to pattern
        self.assertTrue(breach_data.get('found_in_breaches', False))
        self.assertGreater(breach_data.get('breach_count', 0), 0)
        self.assertIn(breach_data.get('risk_level'), ['Medium', 'High'])
    
    def test_invalid_number_handling(self):
        """Test handling of invalid numbers in enhanced features"""
        invalid_numbers = ['123', '12345678901234', 'abcdefghij']
        
        for number in invalid_numbers:
            with self.subTest(number=number):
                # TRAI lookup should handle invalid numbers gracefully
                trai_result = self.formatter.get_trai_circle_lookup(number)
                self.assertEqual(trai_result['confidence'], 'Low')
                
                # Porting check should handle invalid numbers
                porting_result = self.formatter.check_indian_sim_porting_history(number)
                self.assertFalse(porting_result.get('porting_possible', True))

if __name__ == '__main__':
    # Create tests directory if it doesn't exist
    os.makedirs('tests', exist_ok=True)
    
    # Run tests
    unittest.main(verbosity=2)