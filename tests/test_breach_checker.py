"""
Unit tests for Breach Checker
Tests breach database integration, timeline analysis, and risk assessment
"""

import unittest
import sys
import os
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime

# Add src directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from utils.breach_checker import (
    BreachChecker,
    BreachSeverity,
    DataType,
    BreachIncident,
    BreachResult
)


class TestBreachIncident(unittest.TestCase):
    """Test cases for BreachIncident dataclass"""
    
    def test_breach_incident_creation(self):
        """Test BreachIncident creation"""
        incident = BreachIncident(
            name="Test Breach",
            date="2023-01-15",
            description="Test breach description",
            data_classes=[DataType.EMAIL, DataType.PASSWORD],
            breach_count=1000000,
            severity=BreachSeverity.HIGH,
            verified=True,
            source="Test Source",
            confidence=85.0
        )
        
        self.assertEqual(incident.name, "Test Breach")
        self.assertEqual(incident.date, "2023-01-15")
        self.assertEqual(incident.description, "Test breach description")
        self.assertEqual(len(incident.data_classes), 2)
        self.assertIn(DataType.EMAIL, incident.data_classes)
        self.assertIn(DataType.PASSWORD, incident.data_classes)
        self.assertEqual(incident.breach_count, 1000000)
        self.assertEqual(incident.severity, BreachSeverity.HIGH)
        self.assertTrue(incident.verified)
        self.assertEqual(incident.source, "Test Source")
        self.assertEqual(incident.confidence, 85.0)


class TestBreachResult(unittest.TestCase):
    """Test cases for BreachResult dataclass"""
    
    def test_breach_result_creation(self):
        """Test BreachResult creation"""
        incidents = [
            BreachIncident(
                name="Breach 1",
                date="2023-01-15",
                description="First breach",
                data_classes=[DataType.EMAIL],
                breach_count=1000,
                severity=BreachSeverity.MEDIUM
            ),
            BreachIncident(
                name="Breach 2",
                date="2023-06-20",
                description="Second breach",
                data_classes=[DataType.PASSWORD],
                breach_count=2000,
                severity=BreachSeverity.HIGH
            )
        ]
        
        result = BreachResult(
            identifier="test@example.com",
            identifier_type="email",
            breaches_found=incidents,
            total_breaches=2,
            total_records=3000,
            most_recent_breach="2023-06-20",
            overall_risk_score=75.0
        )
        
        self.assertEqual(result.identifier, "test@example.com")
        self.assertEqual(result.identifier_type, "email")
        self.assertEqual(len(result.breaches_found), 2)
        self.assertEqual(result.total_breaches, 2)
        self.assertEqual(result.total_records, 3000)
        self.assertEqual(result.most_recent_breach, "2023-06-20")
        self.assertEqual(result.overall_risk_score, 75.0)


class TestBreachChecker(unittest.TestCase):
    """Test cases for BreachChecker class"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.checker = BreachChecker()
        self.test_email = 'test@example.com'
        self.test_phone = '+15551234567'
        self.test_username = 'testuser'
    
    def test_initialization(self):
        """Test BreachChecker initialization"""
        self.assertIsInstance(self.checker, BreachChecker)
        self.assertIn('haveibeenpwned', self.checker.breach_databases)
        self.assertIn('dehashed', self.checker.breach_databases)
        self.assertIn('leakcheck', self.checker.breach_databases)
        self.assertIn('intelx', self.checker.breach_databases)
        
        # Check database configurations
        hibp_config = self.checker.breach_databases['haveibeenpwned']
        self.assertEqual(hibp_config['name'], 'Have I Been Pwned')
        self.assertTrue(hibp_config['requires_key'])
        self.assertIn('email', hibp_config['supports'])
        self.assertGreater(hibp_config['reliability'], 0.9)
    
    def test_detect_identifier_type_email(self):
        """Test email identifier detection"""
        test_emails = [
            'user@example.com',
            'test.email+tag@domain.co.uk',
            'user123@test-domain.org'
        ]
        
        for email in test_emails:
            result = self.checker._detect_identifier_type(email)
            self.assertEqual(result, "email", f"Failed to detect {email} as email")
    
    def test_detect_identifier_type_phone(self):
        """Test phone identifier detection"""
        test_phones = [
            '+15551234567',
            '15551234567',
            '+919876543210',
            '919876543210'
        ]
        
        for phone in test_phones:
            result = self.checker._detect_identifier_type(phone)
            self.assertEqual(result, "phone", f"Failed to detect {phone} as phone")
    
    def test_detect_identifier_type_username(self):
        """Test username identifier detection"""
        test_usernames = [
            'testuser',
            'user123',
            'my_username',
            'user-name'
        ]
        
        for username in test_usernames:
            result = self.checker._detect_identifier_type(username)
            self.assertEqual(result, "username", f"Failed to detect {username} as username")
    
    def test_simulate_hibp_response_with_breaches(self):
        """Test HIBP simulation with breach patterns"""
        test_email = 'test@example.com'
        breaches = self.checker._simulate_hibp_response(test_email)
        
        self.assertIsInstance(breaches, list)
        self.assertGreater(len(breaches), 0)
        
        for breach in breaches:
            self.assertIsInstance(breach, BreachIncident)
            self.assertEqual(breach.source, "Have I Been Pwned (Simulated)")
            self.assertGreater(breach.confidence, 90.0)
            self.assertTrue(breach.verified)
    
    def test_simulate_hibp_response_no_breaches(self):
        """Test HIBP simulation with clean email"""
        clean_email = 'clean@domain.com'
        breaches = self.checker._simulate_hibp_response(clean_email)
        
        self.assertIsInstance(breaches, list)
        self.assertEqual(len(breaches), 0)
    
    def test_simulate_dehashed_response_email(self):
        """Test Dehashed simulation for email"""
        gmail_email = 'user@gmail.com'
        breaches = self.checker._simulate_dehashed_response(gmail_email, "email")
        
        self.assertIsInstance(breaches, list)
        self.assertGreater(len(breaches), 0)
        
        for breach in breaches:
            self.assertIsInstance(breach, BreachIncident)
            self.assertEqual(breach.source, "Dehashed (Simulated)")
            self.assertIn(DataType.EMAIL, breach.data_classes)
    
    def test_simulate_dehashed_response_phone(self):
        """Test Dehashed simulation for phone"""
        breaches = self.checker._simulate_dehashed_response(self.test_phone, "phone")
        
        self.assertIsInstance(breaches, list)
        self.assertGreater(len(breaches), 0)
        
        for breach in breaches:
            self.assertIsInstance(breach, BreachIncident)
            self.assertEqual(breach.source, "Dehashed (Simulated)")
            self.assertIn(DataType.PHONE, breach.data_classes)
    
    def test_simulate_leakcheck_response(self):
        """Test LeakCheck simulation"""
        yahoo_email = 'user@yahoo.com'
        breaches = self.checker._simulate_leakcheck_response(yahoo_email, "email")
        
        self.assertIsInstance(breaches, list)
        self.assertGreater(len(breaches), 0)
        
        for breach in breaches:
            self.assertIsInstance(breach, BreachIncident)
            self.assertEqual(breach.source, "LeakCheck (Simulated)")
            self.assertEqual(breach.severity, BreachSeverity.CRITICAL)
    
    def test_simulate_intelx_response(self):
        """Test Intelligence X simulation"""
        breaches = self.checker._simulate_intelx_response(self.test_username, "username")
        
        self.assertIsInstance(breaches, list)
        self.assertGreater(len(breaches), 0)
        
        for breach in breaches:
            self.assertIsInstance(breach, BreachIncident)
            self.assertEqual(breach.source, "Intelligence X (Simulated)")
            self.assertIn(DataType.USERNAME, breach.data_classes)
    
    def test_calculate_risk_score_no_breaches(self):
        """Test risk score calculation with no breaches"""
        result = BreachResult(identifier="test@example.com", identifier_type="email")
        risk_score = self.checker._calculate_risk_score(result)
        self.assertEqual(risk_score, 0.0)
    
    def test_calculate_risk_score_low_severity(self):
        """Test risk score calculation with low severity breaches"""
        incidents = [
            BreachIncident(
                name="Low Severity Breach",
                date="2023-01-15",
                description="Low severity breach",
                data_classes=[DataType.USERNAME],
                breach_count=1000,
                severity=BreachSeverity.LOW
            )
        ]
        
        result = BreachResult(
            identifier="test@example.com",
            identifier_type="email",
            breaches_found=incidents,
            most_recent_breach="2023-01-15"
        )
        
        risk_score = self.checker._calculate_risk_score(result)
        self.assertGreater(risk_score, 0.0)
        self.assertLess(risk_score, 50.0)
    
    def test_calculate_risk_score_high_severity(self):
        """Test risk score calculation with high severity breaches"""
        incidents = [
            BreachIncident(
                name="Critical Breach",
                date="2023-01-15",
                description="Critical breach with passwords",
                data_classes=[DataType.EMAIL, DataType.PASSWORD, DataType.SSN],
                breach_count=1000000,
                severity=BreachSeverity.CRITICAL
            ),
            BreachIncident(
                name="High Severity Breach",
                date="2023-06-20",
                description="High severity breach",
                data_classes=[DataType.EMAIL, DataType.PHONE],
                breach_count=500000,
                severity=BreachSeverity.HIGH
            )
        ]
        
        result = BreachResult(
            identifier="test@example.com",
            identifier_type="email",
            breaches_found=incidents,
            most_recent_breach="2023-06-20"
        )
        
        risk_score = self.checker._calculate_risk_score(result)
        self.assertGreater(risk_score, 40.0)  # Adjusted expectation
    
    def test_calculate_risk_score_recent_breach(self):
        """Test risk score calculation with recent breach"""
        recent_date = datetime.now().strftime("%Y-%m-%d")
        
        incidents = [
            BreachIncident(
                name="Recent Breach",
                date=recent_date,
                description="Very recent breach",
                data_classes=[DataType.EMAIL, DataType.PASSWORD],
                breach_count=100000,
                severity=BreachSeverity.HIGH
            )
        ]
        
        result = BreachResult(
            identifier="test@example.com",
            identifier_type="email",
            breaches_found=incidents,
            most_recent_breach=recent_date
        )
        
        risk_score = self.checker._calculate_risk_score(result)
        self.assertGreater(risk_score, 30.0)  # Should get recency bonus
    
    def test_analyze_breach_results(self):
        """Test breach results analysis"""
        incidents = [
            BreachIncident(
                name="Breach 1",
                date="2023-01-15",
                description="First breach",
                data_classes=[DataType.EMAIL, DataType.PASSWORD],
                breach_count=1000000,
                severity=BreachSeverity.CRITICAL
            ),
            BreachIncident(
                name="Breach 2",
                date="2023-06-20",
                description="Second breach",
                data_classes=[DataType.PHONE, DataType.NAME],
                breach_count=500000,
                severity=BreachSeverity.HIGH
            )
        ]
        
        result = BreachResult(
            identifier="test@example.com",
            identifier_type="email",
            breaches_found=incidents
        )
        
        self.checker._analyze_breach_results(result)
        
        # Check basic metrics
        self.assertEqual(result.total_breaches, 2)
        self.assertEqual(result.total_records, 1500000)
        self.assertEqual(result.most_recent_breach, "2023-06-20")
        self.assertEqual(result.oldest_breach, "2023-01-15")
        
        # Check severity breakdown
        self.assertIn("Critical", result.severity_breakdown)
        self.assertIn("High", result.severity_breakdown)
        self.assertEqual(result.severity_breakdown["Critical"], 1)
        self.assertEqual(result.severity_breakdown["High"], 1)
        
        # Check data types
        self.assertIn(DataType.EMAIL, result.data_types_exposed)
        self.assertIn(DataType.PASSWORD, result.data_types_exposed)
        self.assertIn(DataType.PHONE, result.data_types_exposed)
        self.assertIn(DataType.NAME, result.data_types_exposed)
        
        # Check risk flags
        self.assertTrue(result.credential_exposure)  # PASSWORD in data classes
        self.assertTrue(result.sensitive_data_exposure)  # CRITICAL severity
        
        # Check risk score
        self.assertGreater(result.overall_risk_score, 0.0)
        self.assertLessEqual(result.overall_risk_score, 100.0)
    
    def test_check_breaches_integration_email(self):
        """Test complete breach checking for email"""
        result = self.checker.check_breaches('test@example.com', 'email')
        
        self.assertIsInstance(result, BreachResult)
        self.assertEqual(result.identifier, 'test@example.com')
        self.assertEqual(result.identifier_type, 'email')
        self.assertGreater(len(result.databases_checked), 0)
        self.assertGreaterEqual(result.overall_risk_score, 0.0)
        self.assertLessEqual(result.overall_risk_score, 100.0)
        self.assertGreater(result.processing_time, 0.0)
        self.assertIsNotNone(result.last_updated)
    
    def test_check_breaches_integration_phone(self):
        """Test complete breach checking for phone"""
        result = self.checker.check_breaches('+15551234567', 'phone')
        
        self.assertIsInstance(result, BreachResult)
        self.assertEqual(result.identifier, '+15551234567')
        self.assertEqual(result.identifier_type, 'phone')
        self.assertGreater(len(result.databases_checked), 0)
        self.assertGreaterEqual(result.overall_risk_score, 0.0)
        self.assertLessEqual(result.overall_risk_score, 100.0)
    
    def test_check_breaches_auto_detect(self):
        """Test breach checking with auto-detection"""
        # Test email auto-detection
        result = self.checker.check_breaches('test@example.com', 'auto')
        self.assertEqual(result.identifier_type, 'email')
        
        # Test phone auto-detection
        result = self.checker.check_breaches('+15551234567', 'auto')
        self.assertEqual(result.identifier_type, 'phone')
        
        # Test username auto-detection
        result = self.checker.check_breaches('testuser', 'auto')
        self.assertEqual(result.identifier_type, 'username')
    
    def test_generate_breach_timeline_no_breaches(self):
        """Test timeline generation with no breaches"""
        result = BreachResult(identifier="test@example.com", identifier_type="email")
        timeline = self.checker.generate_breach_timeline(result)
        
        self.assertIsInstance(timeline, str)
        self.assertIn("No breaches found", timeline)
    
    def test_generate_breach_timeline_with_breaches(self):
        """Test timeline generation with breaches"""
        incidents = [
            BreachIncident(
                name="Older Breach",
                date="2020-01-15",
                description="Older breach",
                data_classes=[DataType.EMAIL],
                breach_count=1000000,
                severity=BreachSeverity.MEDIUM
            ),
            BreachIncident(
                name="Recent Breach",
                date="2023-06-20",
                description="Recent breach",
                data_classes=[DataType.PASSWORD],
                breach_count=500000,
                severity=BreachSeverity.HIGH
            )
        ]
        
        result = BreachResult(
            identifier="test@example.com",
            identifier_type="email",
            breaches_found=incidents
        )
        
        timeline = self.checker.generate_breach_timeline(result)
        
        self.assertIsInstance(timeline, str)
        self.assertIn("BREACH TIMELINE", timeline)
        self.assertIn("2020-01-15", timeline)
        self.assertIn("2023-06-20", timeline)
        self.assertIn("Older Breach", timeline)
        self.assertIn("Recent Breach", timeline)
        # Should be sorted chronologically
        older_pos = timeline.find("2020-01-15")
        recent_pos = timeline.find("2023-06-20")
        self.assertLess(older_pos, recent_pos)
    
    def test_generate_breach_report(self):
        """Test comprehensive breach report generation"""
        incidents = [
            BreachIncident(
                name="Test Breach",
                date="2023-01-15",
                description="Test breach for report generation",
                data_classes=[DataType.EMAIL, DataType.PASSWORD],
                breach_count=1000000,
                severity=BreachSeverity.HIGH,
                verified=True,
                source="Test Source",
                confidence=90.0
            )
        ]
        
        result = BreachResult(
            identifier="test@example.com",
            identifier_type="email",
            breaches_found=incidents,
            total_breaches=1,
            total_records=1000000,
            most_recent_breach="2023-01-15",
            overall_risk_score=75.0,
            credential_exposure=True,
            sensitive_data_exposure=True,
            databases_checked=["Have I Been Pwned", "Dehashed"],
            processing_time=2.5
        )
        
        # Analyze results first
        self.checker._analyze_breach_results(result)
        
        report = self.checker.generate_breach_report(result)
        
        self.assertIsInstance(report, str)
        self.assertIn('COMPREHENSIVE BREACH ANALYSIS', report)
        self.assertIn('test@example.com', report)
        self.assertIn('/100', report)  # Risk score format
        self.assertIn('RISK ASSESSMENT', report)
        self.assertIn('BREACH TIMELINE', report)
        self.assertIn('SEVERITY BREAKDOWN', report)
        self.assertIn('DATA TYPES EXPOSED', report)
        self.assertIn('BREACH DETAILS', report)
        self.assertIn('SECURITY RECOMMENDATIONS', report)
        self.assertIn('PASSWORD EXPOSURE DETECTED', report)
        self.assertIn('Test Breach', report)
        self.assertIn('Have I Been Pwned', report)
        self.assertIn('LEGAL NOTICE', report)


class TestBreachCheckerIntegration(unittest.TestCase):
    """Integration tests for BreachChecker"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.checker = BreachChecker()
    
    def test_data_type_severity_mapping(self):
        """Test data type to severity mapping"""
        # Critical data types
        critical_types = [DataType.PASSWORD, DataType.SSN, DataType.CREDIT_CARD, DataType.BANK_ACCOUNT]
        for data_type in critical_types:
            severity = self.checker.data_type_severity[data_type]
            self.assertEqual(severity, BreachSeverity.CRITICAL)
        
        # High severity data types
        high_types = [DataType.EMAIL, DataType.PHONE, DataType.ADDRESS]
        for data_type in high_types:
            severity = self.checker.data_type_severity[data_type]
            self.assertEqual(severity, BreachSeverity.HIGH)
    
    def test_database_configuration_consistency(self):
        """Test database configuration consistency"""
        for db_name, config in self.checker.breach_databases.items():
            # Required fields
            required_fields = ['name', 'api_url', 'requires_key', 'rate_limit', 'supports', 'reliability', 'enabled']
            for field in required_fields:
                self.assertIn(field, config, f"Missing {field} in {db_name}")
            
            # Valid types
            self.assertIsInstance(config['name'], str)
            self.assertIsInstance(config['api_url'], str)
            self.assertIsInstance(config['requires_key'], bool)
            self.assertIsInstance(config['rate_limit'], (int, float))
            self.assertIsInstance(config['supports'], list)
            self.assertIsInstance(config['reliability'], float)
            self.assertIsInstance(config['enabled'], bool)
            
            # Valid values
            self.assertGreater(config['rate_limit'], 0.0)
            self.assertGreaterEqual(config['reliability'], 0.0)
            self.assertLessEqual(config['reliability'], 1.0)
            self.assertGreater(len(config['supports']), 0)
            
            # Valid support types
            valid_types = ['email', 'phone', 'username']
            for support_type in config['supports']:
                self.assertIn(support_type, valid_types)
    
    def test_comprehensive_workflow(self):
        """Test complete breach checking workflow"""
        test_identifiers = [
            ('test@example.com', 'email'),
            ('+15551234567', 'phone'),
            ('testuser', 'username'),
            ('user@gmail.com', 'auto'),  # Should auto-detect as email
        ]
        
        for identifier, id_type in test_identifiers:
            with self.subTest(identifier=identifier, type=id_type):
                result = self.checker.check_breaches(identifier, id_type)
                
                # Basic validation
                self.assertIsInstance(result, BreachResult)
                self.assertEqual(result.identifier, identifier)
                self.assertIn(result.identifier_type, ['email', 'phone', 'username'])
                self.assertGreaterEqual(result.total_breaches, 0)
                self.assertGreaterEqual(result.overall_risk_score, 0.0)
                self.assertLessEqual(result.overall_risk_score, 100.0)
                self.assertGreater(result.processing_time, 0.0)
                self.assertIsNotNone(result.last_updated)
                
                # All found breaches should be valid
                for breach in result.breaches_found:
                    self.assertIsInstance(breach, BreachIncident)
                    self.assertIsNotNone(breach.name)
                    self.assertIsInstance(breach.severity, BreachSeverity)
                    self.assertGreaterEqual(breach.confidence, 0.0)
                    self.assertLessEqual(breach.confidence, 100.0)
                
                # Report generation should work
                report = self.checker.generate_breach_report(result)
                self.assertIsInstance(report, str)
                self.assertGreater(len(report), 100)
                
                # Timeline generation should work
                timeline = self.checker.generate_breach_timeline(result)
                self.assertIsInstance(timeline, str)


if __name__ == '__main__':
    unittest.main()