#!/usr/bin/env python3
"""
Security Measures Tests for CIOT
Tests for security and privacy protection measures
"""

import unittest
import tempfile
import shutil
import json
import time
from pathlib import Path
from unittest.mock import patch, MagicMock

# Import security modules
import sys
sys.path.append('src')

from core.secure_api_manager import SecureAPIManager
from core.rate_limiter import RateLimiter
from core.privacy_manager import PrivacyManager
from core.legal_compliance import LegalComplianceManager
from core.audit_logger import EnhancedAuditLogger
from core.security_manager import SecurityManager

class TestSecureAPIManager(unittest.TestCase):
    """Test secure API key management"""
    
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.api_manager = SecureAPIManager(self.temp_dir)
    
    def tearDown(self):
        shutil.rmtree(self.temp_dir)
    
    def test_api_key_encryption(self):
        """Test API key encryption and decryption"""
        # Set an API key
        self.api_manager.set_api_key("test_service", "api_key", "test_key_12345")
        
        # Verify it can be retrieved
        retrieved_key = self.api_manager.get_api_key("test_service")
        self.assertEqual(retrieved_key, "test_key_12345")
        
        # Verify encrypted file exists
        encrypted_file = Path(self.temp_dir) / "api_keys.enc"
        self.assertTrue(encrypted_file.exists())
        
        # Verify plain text file is removed
        plain_file = Path(self.temp_dir) / "api_keys.json"
        self.assertFalse(plain_file.exists())
    
    def test_api_key_validation(self):
        """Test API key format validation"""
        # Test valid keys
        self.assertTrue(self.api_manager.validate_key_format("abstractapi", "a" * 32))
        self.assertTrue(self.api_manager.validate_key_format("neutrino", "n" * 40))
        
        # Test invalid keys
        self.assertFalse(self.api_manager.validate_key_format("abstractapi", "short"))
        self.assertFalse(self.api_manager.validate_key_format("abstractapi", "a" * 31))
    
    def test_service_configuration(self):
        """Test service configuration management"""
        # Configure a service
        self.api_manager.set_api_key("test_service", "api_key", "test_key")
        self.api_manager.set_api_key("test_service", "base_url", "https://api.test.com")
        
        # Check service is configured
        self.assertTrue(self.api_manager.is_service_configured("test_service"))
        
        # Get full configuration
        config = self.api_manager.get_service_config("test_service")
        self.assertEqual(config["api_key"], "test_key")
        self.assertEqual(config["base_url"], "https://api.test.com")
        
        # Remove service
        self.api_manager.remove_api_key("test_service")
        self.assertFalse(self.api_manager.is_service_configured("test_service"))

class TestRateLimiter(unittest.TestCase):
    """Test rate limiting functionality"""
    
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.rate_limiter = RateLimiter(self.temp_dir)
        
        # Set strict limits for testing
        self.rate_limiter.limits["test_category"] = {
            "requests_per_minute": 2,
            "requests_per_hour": 5,
            "burst_limit": 1,
            "cooldown_seconds": 1
        }
    
    def tearDown(self):
        shutil.rmtree(self.temp_dir)
    
    def test_rate_limiting_basic(self):
        """Test basic rate limiting functionality"""
        # First request should be allowed
        allowed, message = self.rate_limiter.check_rate_limit("test_category")
        self.assertTrue(allowed)
        self.rate_limiter.record_request("test_category")
        
        # Second request should be allowed
        allowed, message = self.rate_limiter.check_rate_limit("test_category")
        self.assertTrue(allowed)
        self.rate_limiter.record_request("test_category")
        
        # Third request should be blocked (exceeds per-minute limit)
        allowed, message = self.rate_limiter.check_rate_limit("test_category")
        self.assertFalse(allowed)
        self.assertIn("per minute", message)
    
    def test_burst_limiting(self):
        """Test burst limiting functionality"""
        # First request should be allowed
        allowed, message = self.rate_limiter.check_rate_limit("test_category")
        self.assertTrue(allowed)
        self.rate_limiter.record_request("test_category")
        
        # Immediate second request should be blocked (burst limit)
        allowed, message = self.rate_limiter.check_rate_limit("test_category")
        self.assertFalse(allowed)
        self.assertIn("Burst limit", message)
    
    def test_rate_limit_status(self):
        """Test rate limit status reporting"""
        # Record a request
        self.rate_limiter.record_request("test_category")
        
        # Check status
        status = self.rate_limiter.get_rate_limit_status("test_category")
        self.assertIn("minute", status)
        self.assertEqual(status["minute"]["used"], 1)
        self.assertEqual(status["minute"]["remaining"], 1)
    
    def test_rate_limit_reset(self):
        """Test rate limit reset functionality"""
        # Fill up the rate limit
        self.rate_limiter.record_request("test_category")
        self.rate_limiter.record_request("test_category")
        
        # Should be blocked
        allowed, message = self.rate_limiter.check_rate_limit("test_category")
        self.assertFalse(allowed)
        
        # Reset limits
        self.rate_limiter.reset_rate_limits("test_category")
        
        # Should be allowed again
        allowed, message = self.rate_limiter.check_rate_limit("test_category")
        self.assertTrue(allowed)

class TestPrivacyManager(unittest.TestCase):
    """Test privacy management functionality"""
    
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.data_dir = Path(self.temp_dir) / "data"
        self.data_dir.mkdir()
        self.privacy_manager = PrivacyManager(self.temp_dir, self.data_dir)
    
    def tearDown(self):
        shutil.rmtree(self.temp_dir)
    
    def test_consent_management(self):
        """Test user consent management"""
        # Initially no consent
        self.assertFalse(self.privacy_manager.check_consent("data_storage"))
        
        # Record consent
        consent = self.privacy_manager.record_consent("data_storage", True, {"purpose": "investigation"})
        self.assertTrue(consent["granted"])
        
        # Check consent is now granted
        self.assertTrue(self.privacy_manager.check_consent("data_storage"))
        
        # Withdraw consent
        self.privacy_manager.withdraw_consent("data_storage")
        self.assertFalse(self.privacy_manager.check_consent("data_storage"))
    
    def test_phone_number_anonymization(self):
        """Test phone number anonymization"""
        phone = "+1234567890"
        anonymized = self.privacy_manager.anonymize_phone_number(phone)
        
        # Should be anonymized
        self.assertNotEqual(phone, anonymized)
        self.assertTrue(anonymized.startswith("HASH_"))
        
        # Same phone should produce same hash
        anonymized2 = self.privacy_manager.anonymize_phone_number(phone)
        self.assertEqual(anonymized, anonymized2)
    
    def test_personal_data_anonymization(self):
        """Test personal data anonymization"""
        data = {
            "name": "John Doe",
            "email": "john@example.com",
            "phone": "+1234567890",
            "carrier": "Verizon"  # This should not be anonymized
        }
        
        anonymized = self.privacy_manager.anonymize_personal_data(data)
        
        # Personal fields should be anonymized
        self.assertNotEqual(data["name"], anonymized["name"])
        self.assertNotEqual(data["email"], anonymized["email"])
        
        # Non-personal fields should remain unchanged
        self.assertEqual(data["carrier"], anonymized["carrier"])
    
    def test_data_cleanup(self):
        """Test data cleanup functionality"""
        # Create test files
        cases_dir = self.data_dir / "cases"
        cases_dir.mkdir()
        
        test_file = cases_dir / "session_test.json"
        test_file.write_text('{"test": "data"}')
        
        # Set very short retention period
        self.privacy_manager.privacy_settings["data_retention"]["investigation_history_days"] = 0
        
        # Run cleanup
        self.privacy_manager.cleanup_expired_data()
        
        # File should be removed
        self.assertFalse(test_file.exists())
    
    def test_data_export(self):
        """Test user data export"""
        # Record some consent
        self.privacy_manager.record_consent("data_storage", True)
        
        # Export data
        export_data = self.privacy_manager.export_user_data()
        
        self.assertIsNotNone(export_data)
        self.assertIn("export_timestamp", export_data)
        self.assertIn("consent_records", export_data)
        self.assertIn("privacy_settings", export_data)

class TestLegalComplianceManager(unittest.TestCase):
    """Test legal compliance functionality"""
    
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.compliance_manager = LegalComplianceManager(self.temp_dir)
    
    def tearDown(self):
        shutil.rmtree(self.temp_dir)
    
    def test_startup_warning(self):
        """Test startup warning generation"""
        warning = self.compliance_manager.get_startup_warning("united_states")
        
        self.assertIsNotNone(warning)
        self.assertIn("title", warning)
        self.assertIn("message", warning)
        self.assertIn("key_points", warning)
        self.assertIn("prohibited_activities", warning)
    
    def test_investigation_warning(self):
        """Test investigation-specific warnings"""
        warning = self.compliance_manager.get_investigation_warning("phone", "european_union")
        
        self.assertIsNotNone(warning)
        self.assertIn("title", warning)
        self.assertIn("message", warning)
        self.assertIn("specific_risks", warning)
    
    def test_ethical_concerns_detection(self):
        """Test ethical concerns detection"""
        # Test concerning request
        concerns = self.compliance_manager.check_ethical_concerns("investigate my ex-girlfriend")
        self.assertTrue(len(concerns) > 0)
        self.assertEqual(concerns[0]["type"], "potential_harassment")
        
        # Test concerning request with minor
        concerns = self.compliance_manager.check_ethical_concerns("find information about this child")
        self.assertTrue(len(concerns) > 0)
        self.assertEqual(concerns[0]["type"], "minor_investigation")
        
        # Test illegal activity request
        concerns = self.compliance_manager.check_ethical_concerns("hack into their account")
        self.assertTrue(len(concerns) > 0)
        self.assertEqual(concerns[0]["type"], "illegal_activity")
        self.assertEqual(concerns[0]["level"], "critical")
    
    def test_jurisdiction_guidance(self):
        """Test jurisdiction-specific guidance"""
        guidance = self.compliance_manager.get_jurisdiction_guidance("european_union")
        
        self.assertIn("name", guidance)
        self.assertIn("key_points", guidance)
        self.assertIn("prohibited_activities", guidance)
        self.assertEqual(guidance["name"], "European Union (GDPR) Compliance")
    
    def test_warning_frequency(self):
        """Test warning frequency control"""
        # Should show warning initially
        self.assertTrue(self.compliance_manager.should_show_warning("test_warning"))
        
        # Should not show warning if recently shown
        recent_time = "2024-01-01T12:00:00"
        self.assertFalse(self.compliance_manager.should_show_warning("test_warning", recent_time))

class TestEnhancedAuditLogger(unittest.TestCase):
    """Test enhanced audit logging functionality"""
    
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.audit_logger = EnhancedAuditLogger(self.temp_dir)
    
    def tearDown(self):
        shutil.rmtree(self.temp_dir)
    
    def test_session_logging(self):
        """Test session start/end logging"""
        # Start session
        self.audit_logger.start_session("test_session", {"user": "test"})
        self.assertEqual(self.audit_logger.current_session, "test_session")
        
        # End session
        self.audit_logger.end_session({"actions": 5})
        self.assertIsNone(self.audit_logger.current_session)
    
    def test_investigation_action_logging(self):
        """Test investigation action logging"""
        self.audit_logger.start_session("test_session")
        
        # Log an action
        self.audit_logger.log_investigation_action("phone_lookup", "+1234567890", {"country": "US"})
        
        # Should not raise any exceptions
        self.assertTrue(True)
    
    def test_api_call_logging(self):
        """Test API call logging"""
        # Log successful API call
        self.audit_logger.log_api_call("abstractapi", "/validate", True, 0.5)
        
        # Log failed API call
        self.audit_logger.log_api_call("abstractapi", "/validate", False, 2.0, "Timeout")
        
        # Should not raise any exceptions
        self.assertTrue(True)
    
    def test_security_event_logging(self):
        """Test security event logging"""
        self.audit_logger.log_security_event(
            "rate_limit_exceeded",
            "medium",
            "User exceeded rate limit",
            {"category": "phone_investigation"}
        )
        
        # Should not raise any exceptions
        self.assertTrue(True)
    
    def test_data_anonymization(self):
        """Test data anonymization in logging"""
        # Test phone number anonymization
        phone = "+1234567890"
        anonymized = self.audit_logger._anonymize_data(phone)
        self.assertNotEqual(phone, anonymized)
        self.assertTrue(anonymized.startswith("PHONE_HASH_"))
        
        # Test email anonymization
        email = "test@example.com"
        anonymized = self.audit_logger._anonymize_data(email)
        self.assertNotEqual(email, anonymized)
        self.assertTrue(anonymized.startswith("EMAIL_HASH_"))

class TestSecurityManager(unittest.TestCase):
    """Test integrated security manager functionality"""
    
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.data_dir = Path(self.temp_dir) / "data"
        self.data_dir.mkdir()
        self.security_manager = SecurityManager(self.temp_dir, self.data_dir)
    
    def tearDown(self):
        shutil.rmtree(self.temp_dir)
    
    def test_session_initialization(self):
        """Test secure session initialization"""
        result = self.security_manager.initialize_session("test_session", {"user": "test"})
        
        self.assertTrue(result["security_initialized"])
        self.assertEqual(result["session_id"], "test_session")
        self.assertTrue(result["rate_limits_active"])
        self.assertTrue(result["audit_logging_active"])
    
    def test_investigation_authorization(self):
        """Test investigation authorization checking"""
        # Normal investigation should be authorized
        authorized, details = self.security_manager.check_investigation_authorization(
            "phone", "+1234567890", {"user": "test"}
        )
        self.assertTrue(authorized)
        self.assertTrue(details["authorized"])
        
        # Concerning investigation should have warnings
        authorized, details = self.security_manager.check_investigation_authorization(
            "phone", "investigate my ex-girlfriend", {"user": "test"}
        )
        # Should still be authorized but with concerns
        self.assertTrue(authorized)
        self.assertTrue(len(details["ethical_concerns"]) > 0)
        
        # Critical investigation should be blocked
        authorized, details = self.security_manager.check_investigation_authorization(
            "phone", "hack into their account", {"user": "test"}
        )
        self.assertFalse(authorized)
        self.assertTrue(details["blocked"])
    
    def test_rate_limit_integration(self):
        """Test rate limiting integration"""
        # First request should be allowed
        allowed, message = self.security_manager.check_rate_limits("phone_investigation")
        self.assertTrue(allowed)
        
        # Record the request
        self.security_manager.record_operation("phone_investigation")
        
        # Should still work with default limits
        allowed, message = self.security_manager.check_rate_limits("phone_investigation")
        self.assertTrue(allowed)
    
    def test_api_key_integration(self):
        """Test API key management integration"""
        # Set an API key
        self.security_manager.api_manager.set_api_key("test_service", "api_key", "test_key")
        
        # Retrieve it securely
        key = self.security_manager.get_secure_api_key("test_service")
        self.assertEqual(key, "test_key")
        
        # Non-existent service should return None
        key = self.security_manager.get_secure_api_key("nonexistent")
        self.assertIsNone(key)
    
    def test_data_processing_integration(self):
        """Test data processing with privacy controls"""
        test_data = {
            "phone": "+1234567890",
            "name": "John Doe",
            "carrier": "Verizon"
        }
        
        # Process with anonymization
        processed = self.security_manager.process_investigation_data(test_data, anonymize=True)
        
        # Personal data should be anonymized
        self.assertNotEqual(test_data["name"], processed["name"])
        # Non-personal data should remain
        self.assertEqual(test_data["carrier"], processed["carrier"])
    
    def test_security_status(self):
        """Test security status reporting"""
        # Initialize session first
        self.security_manager.initialize_session("test_session")
        
        status = self.security_manager.get_security_status()
        
        self.assertIn("session_active", status)
        self.assertIn("privacy_settings", status)
        self.assertIn("rate_limits_active", status)
        self.assertIn("audit_logging_active", status)
    
    def test_security_incident_handling(self):
        """Test security incident handling"""
        # Should not raise exceptions
        self.security_manager.handle_security_incident(
            "test_incident",
            "medium",
            "Test security incident",
            {"test": "data"}
        )
        
        # Critical incident
        self.security_manager.handle_security_incident(
            "critical_incident",
            "critical",
            "Critical test incident"
        )
        
        self.assertTrue(True)  # If we get here, no exceptions were raised
    
    def test_security_report_generation(self):
        """Test security report generation"""
        # Initialize session
        self.security_manager.initialize_session("test_session")
        
        report = self.security_manager.generate_security_report()
        
        self.assertIn("report_timestamp", report)
        self.assertIn("security_status", report)
        self.assertIn("audit_report", report)
        self.assertIn("compliance_report", report)
        self.assertIn("privacy_summary", report)

class TestSecurityIntegration(unittest.TestCase):
    """Test security integration with existing CIOT functionality"""
    
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.data_dir = Path(self.temp_dir) / "data"
        self.data_dir.mkdir()
    
    def tearDown(self):
        shutil.rmtree(self.temp_dir)
    
    @patch('src.utils.osint_utils.get_phone_info')
    def test_secure_phone_investigation_integration(self, mock_get_phone_info):
        """Test integration with phone investigation functionality"""
        # Mock the phone investigation function
        mock_get_phone_info.return_value = {
            "phone": "+1234567890",
            "carrier": "Verizon",
            "location": "New York"
        }
        
        security_manager = SecurityManager(self.temp_dir, self.data_dir)
        
        # Initialize secure session
        session_result = security_manager.initialize_session("test_investigation")
        self.assertTrue(session_result["security_initialized"])
        
        # Check authorization
        authorized, auth_details = security_manager.check_investigation_authorization(
            "phone", "+1234567890"
        )
        self.assertTrue(authorized)
        
        # Check rate limits
        allowed, rate_message = security_manager.check_rate_limits("phone_investigation")
        self.assertTrue(allowed)
        
        # Record the operation
        security_manager.record_operation("phone_investigation")
        
        # Process results with privacy controls
        mock_result = mock_get_phone_info.return_value
        processed_result = security_manager.process_investigation_data(mock_result)
        
        # Should have processed the data
        self.assertIsNotNone(processed_result)
        
        # Clean up
        security_manager.cleanup_session_data()

if __name__ == '__main__':
    # Create test suite
    test_suite = unittest.TestSuite()
    
    # Add test classes
    test_classes = [
        TestSecureAPIManager,
        TestRateLimiter,
        TestPrivacyManager,
        TestLegalComplianceManager,
        TestEnhancedAuditLogger,
        TestSecurityManager,
        TestSecurityIntegration
    ]
    
    for test_class in test_classes:
        tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
        test_suite.addTests(tests)
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # Print summary
    print(f"\n{'='*50}")
    print(f"Security Tests Summary:")
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Success rate: {((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100):.1f}%")
    print(f"{'='*50}")