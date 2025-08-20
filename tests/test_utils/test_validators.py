#!/usr/bin/env python3
"""
Tests for validation utilities
"""

import unittest
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from src.utils.validators import validate_email, validate_phone, validate_ip

class TestValidators(unittest.TestCase):
    """Test cases for validation functions"""
    
    def test_email_validation(self):
        """Test email validation"""
        # Valid emails
        self.assertTrue(validate_email("test@example.com"))
        self.assertTrue(validate_email("user.name@domain.co.uk"))
        
        # Invalid emails
        self.assertFalse(validate_email("invalid-email"))
        self.assertFalse(validate_email("@domain.com"))
        self.assertFalse(validate_email("user@"))
    
    def test_phone_validation(self):
        """Test phone number validation"""
        # Valid phones
        self.assertTrue(validate_phone("+1234567890"))
        self.assertTrue(validate_phone("(555) 123-4567"))
        
        # Invalid phones
        self.assertFalse(validate_phone("123"))
        self.assertFalse(validate_phone("abc"))
    
    def test_ip_validation(self):
        """Test IP address validation"""
        # Valid IPs
        self.assertTrue(validate_ip("192.168.1.1"))
        self.assertTrue(validate_ip("8.8.8.8"))
        
        # Invalid IPs
        self.assertFalse(validate_ip("256.256.256.256"))
        self.assertFalse(validate_ip("not.an.ip"))

if __name__ == '__main__':
    unittest.main()