"""
Unit tests for Reputation Checker
Tests spam database integration, risk scoring, and caller ID lookup
"""

import unittest
import sys
import os
from unittest.mock import Mock, patch, MagicMock

# Add src directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from utils.reputation_checker import (
    ReputationChecker,
    RiskLevel,
    SpamCategory,
    SpamReport,
    CallerIDInfo,
    ReputationResult
)


class TestSpamReport(unittest.TestCase):
    """Test cases for SpamReport dataclass"""
    
    def test_spam_report_creation(self):
        """Test SpamReport creation"""
        report = SpamReport(
            source="Test Source",
            category=SpamCategory.SCAM,
            report_count=25,
            confidence=85.0,
            last_reported="2024-01-15"
        )
        
        self.assertEqual(report.source, "Test Source")
        self.assertEqual(report.category, SpamCategory.SCAM)
        self.assertEqual(report.report_count, 25)
        self.assertEqual(report.confidence, 85.0)
        self.assertEqual(report.last_reported, "2024-01-15")


class TestCallerIDInfo(unittest.TestCase):
    """Test cases for CallerIDInfo dataclass"""
    
    def test_caller_id_creation(self):
        """Test CallerIDInfo creation"""
        caller_id = CallerIDInfo(
            name="John Doe",
            business_name="Acme Corp",
            business_type="Technology",
            location="New York",
            verified=True,
            source="Test Source",
            confidence=90.0
        )
        
        self.assertEqual(caller_id.name, "John Doe")
        self.assertEqual(caller_id.business_name, "Acme Corp")
        self.assertEqual(caller_id.business_type, "Technology")
        self.assertEqual(caller_id.location, "New York")
        self.assertTrue(caller_id.verified)
        self.assertEqual(caller_id.source, "Test Source")
        self.assertEqual(caller_id.confidence, 90.0)


class TestReputationChecker(unittest.TestCase):
    """Test cases for ReputationChecker class"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.checker = ReputationChecker()
        self.test_phone_us = '+15551234567'
        self.test_phone_indian = '+919876543210'
    
    def test_initialization(self):
        """Test ReputationChecker initialization"""
        self.assertIsInstance(self.checker, ReputationChecker)
        self.assertIn('whocallsme', self.checker.spam_databases)
        self.assertIn('opencnam', self.checker.spam_databases)
        self.assertIn('truecaller', self.checker.spam_databases)
        
        # Check risk thresholds
        self.assertEqual(self.checker.risk_thresholds[RiskLevel.CRITICAL], 80)
        self.assertEqual(self.checker.risk_thresholds[RiskLevel.HIGH], 60)
        self.assertEqual(self.checker.risk_thresholds[RiskLevel.MEDIUM], 40)
        self.assertEqual(self.checker.risk_thresholds[RiskLevel.LOW], 0)
    
    def test_format_phone_number_us(self):
        """Test US phone number formatting"""
        test_cases = [
            ('5551234567', '+15551234567'),
            ('+15551234567', '+15551234567'),
            ('(555) 123-4567', '+15551234567'),
            ('555-123-4567', '+15551234567')
        ]
        
        for input_number, expected in test_cases:
            result = self.checker._format_phone_number(input_number, 'US')
            self.assertEqual(result, expected)
    
    def test_format_phone_number_indian(self):
        """Test Indian phone number formatting"""
        test_cases = [
            ('9876543210', '+919876543210'),
            ('+919876543210', '+919876543210'),
            ('919876543210', '+919876543210'),
            ('09876543210', '+919876543210')
        ]
        
        for input_number, expected in test_cases:
            result = self.checker._format_phone_number(input_number, 'IN')
            self.assertEqual(result, expected)
    
    def test_check_whocallsme_spam_pattern(self):
        """Test WhoCallsMe spam pattern detection"""
        db_config = self.checker.spam_databases['whocallsme']
        
        # Test spam pattern
        spam_number = '+15559999999'
        result = self.checker._check_whocallsme(spam_number, db_config)
        
        self.assertIsNotNone(result)
        self.assertEqual(result.source, 'WhoCallsMe')
        self.assertEqual(result.category, SpamCategory.SCAM)
        self.assertGreater(result.report_count, 0)
        self.assertGreater(result.confidence, 80.0)
    
    def test_check_whocallsme_telemarketing_pattern(self):
        """Test WhoCallsMe telemarketing pattern detection"""
        db_config = self.checker.spam_databases['whocallsme']
        
        # Test telemarketing pattern
        telemarketing_number = '+18005551234'
        result = self.checker._check_whocallsme(telemarketing_number, db_config)
        
        self.assertIsNotNone(result)
        self.assertEqual(result.source, 'WhoCallsMe')
        self.assertEqual(result.category, SpamCategory.TELEMARKETING)
        self.assertGreater(result.report_count, 0)
        self.assertGreater(result.confidence, 60.0)
    
    def test_check_whocallsme_clean_number(self):
        """Test WhoCallsMe with clean number"""
        db_config = self.checker.spam_databases['whocallsme']
        
        # Test clean number
        clean_number = '+15551234567'
        result = self.checker._check_whocallsme(clean_number, db_config)
        
        self.assertIsNone(result)
    
    def test_check_truecaller_fraud_pattern(self):
        """Test Truecaller fraud pattern detection"""
        db_config = self.checker.spam_databases['truecaller']
        
        # Test fraud pattern (repeated digits)
        fraud_number = '+919876543333'  # Last 4 digits same
        result = self.checker._check_truecaller(fraud_number, db_config)
        
        self.assertIsNotNone(result)
        self.assertEqual(result.source, 'Truecaller Community')
        self.assertEqual(result.category, SpamCategory.FRAUD)
        self.assertGreater(result.report_count, 0)
        self.assertGreater(result.confidence, 85.0)
    
    def test_check_truecaller_promotional_pattern(self):
        """Test Truecaller promotional pattern detection"""
        db_config = self.checker.spam_databases['truecaller']
        
        # Test promotional pattern
        promotional_number = '+919001234567'
        result = self.checker._check_truecaller(promotional_number, db_config)
        
        self.assertIsNotNone(result)
        self.assertEqual(result.source, 'Truecaller Community')
        self.assertEqual(result.category, SpamCategory.PROMOTIONAL)
        self.assertGreater(result.report_count, 0)
        self.assertGreater(result.confidence, 50.0)
    
    def test_get_caller_id_info_business(self):
        """Test caller ID info for business numbers"""
        # Test toll-free business number
        business_number = '+18005551234'
        result = self.checker._get_caller_id_info(business_number)
        
        self.assertIsNotNone(result)
        self.assertIsInstance(result, CallerIDInfo)
        self.assertIsNotNone(result.name)
        self.assertIsNotNone(result.business_type)
        self.assertIsNotNone(result.location)
        self.assertGreater(result.confidence, 50.0)
    
    def test_get_caller_id_info_indian_business(self):
        """Test caller ID info for Indian business numbers"""
        # Test Indian business number
        indian_business = '+918001234567'
        result = self.checker._get_caller_id_info(indian_business)
        
        self.assertIsNotNone(result)
        self.assertIsInstance(result, CallerIDInfo)
        self.assertEqual(result.location, "India")
        self.assertGreater(result.confidence, 50.0)
    
    def test_calculate_risk_score_no_reports(self):
        """Test risk score calculation with no reports"""
        spam_reports = []
        risk_score = self.checker._calculate_risk_score(spam_reports)
        self.assertEqual(risk_score, 0.0)
    
    def test_calculate_risk_score_single_high_risk(self):
        """Test risk score calculation with single high-risk report"""
        spam_reports = [
            SpamReport(
                source="Test Source",
                category=SpamCategory.SCAM,
                report_count=50,
                confidence=90.0
            )
        ]
        
        risk_score = self.checker._calculate_risk_score(spam_reports)
        self.assertGreater(risk_score, 70.0)  # Should be high risk
    
    def test_calculate_risk_score_multiple_reports(self):
        """Test risk score calculation with multiple reports"""
        spam_reports = [
            SpamReport(
                source="Source 1",
                category=SpamCategory.SCAM,
                report_count=25,
                confidence=85.0
            ),
            SpamReport(
                source="Source 2",
                category=SpamCategory.TELEMARKETING,
                report_count=15,
                confidence=70.0
            ),
            SpamReport(
                source="Source 3",
                category=SpamCategory.FRAUD,
                report_count=30,
                confidence=80.0
            )
        ]
        
        risk_score = self.checker._calculate_risk_score(spam_reports)
        self.assertGreater(risk_score, 50.0)  # Should be medium-high with multiple sources
    
    def test_calculate_risk_score_low_confidence(self):
        """Test risk score calculation with low confidence reports"""
        spam_reports = [
            SpamReport(
                source="Test Source",
                category=SpamCategory.PROMOTIONAL,
                report_count=5,
                confidence=30.0
            )
        ]
        
        risk_score = self.checker._calculate_risk_score(spam_reports)
        self.assertLess(risk_score, 40.0)  # Should be low risk
    
    def test_classify_risk_level(self):
        """Test risk level classification"""
        test_cases = [
            (95, RiskLevel.CRITICAL),
            (75, RiskLevel.HIGH),
            (50, RiskLevel.MEDIUM),
            (25, RiskLevel.LOW),
            (0, RiskLevel.LOW)
        ]
        
        for score, expected_level in test_cases:
            level = self.checker._classify_risk_level(score)
            self.assertEqual(level, expected_level)
    
    def test_calculate_confidence_score_no_databases(self):
        """Test confidence calculation with no databases"""
        confidence = self.checker._calculate_confidence_score([], [])
        self.assertEqual(confidence, 0.0)
    
    def test_calculate_confidence_score_multiple_databases(self):
        """Test confidence calculation with multiple databases"""
        spam_reports = [
            SpamReport(
                source="Source 1",
                category=SpamCategory.SCAM,
                report_count=25,
                confidence=85.0
            )
        ]
        databases_checked = ['Database 1', 'Database 2', 'Database 3']
        
        confidence = self.checker._calculate_confidence_score(spam_reports, databases_checked)
        self.assertGreater(confidence, 60.0)
    
    def test_get_database_weight(self):
        """Test database weight retrieval"""
        # Test known database
        weight = self.checker._get_database_weight('WhoCallsMe')
        self.assertEqual(weight, 0.85)
        
        # Test unknown database
        weight = self.checker._get_database_weight('Unknown Database')
        self.assertEqual(weight, 0.5)
    
    @patch('utils.osint_utils.load_api_keys')
    def test_check_opencnam_no_api_key(self, mock_load_keys):
        """Test OpenCNAM check without API key"""
        mock_load_keys.return_value = {}
        
        db_config = self.checker.spam_databases['opencnam']
        result = self.checker._check_opencnam('+15551234567', db_config)
        
        self.assertIsNone(result)
    
    @patch('utils.osint_utils.load_api_keys')
    def test_check_opencnam_with_api_key(self, mock_load_keys):
        """Test OpenCNAM check with API key"""
        mock_load_keys.return_value = {'opencnam': {'api_key': 'test_key'}}
        
        db_config = self.checker.spam_databases['opencnam']
        
        # Test robocall pattern
        robocall_number = '+15551230000'
        result = self.checker._check_opencnam(robocall_number, db_config)
        
        self.assertIsNotNone(result)
        self.assertEqual(result.category, SpamCategory.ROBOCALL)
    
    def test_check_reputation_integration(self):
        """Test complete reputation check integration"""
        # Test with a number that should trigger multiple patterns
        test_number = '+15559999999'  # Should trigger spam patterns
        
        result = self.checker.check_reputation(test_number, 'US')
        
        self.assertIsInstance(result, ReputationResult)
        self.assertEqual(result.phone_number, test_number)
        self.assertIsInstance(result.risk_level, RiskLevel)
        self.assertGreaterEqual(result.risk_score, 0.0)
        self.assertLessEqual(result.risk_score, 100.0)
        self.assertIsInstance(result.is_spam, bool)
        self.assertGreaterEqual(result.total_reports, 0)
        self.assertIsInstance(result.spam_reports, list)
        self.assertIsInstance(result.databases_checked, list)
        self.assertGreater(len(result.databases_checked), 0)
        self.assertGreaterEqual(result.confidence_score, 0.0)
        self.assertLessEqual(result.confidence_score, 100.0)
        self.assertGreater(result.processing_time, 0.0)
    
    def test_generate_reputation_report(self):
        """Test reputation report generation"""
        # Create mock result
        spam_reports = [
            SpamReport(
                source="Test Source",
                category=SpamCategory.SCAM,
                report_count=25,
                confidence=85.0,
                last_reported="2024-01-15"
            )
        ]
        
        caller_id = CallerIDInfo(
            name="Test Caller",
            business_name="Test Business",
            business_type="Technology",
            location="Test Location",
            verified=True,
            source="Test Source",
            confidence=80.0
        )
        
        result = ReputationResult(
            phone_number='+15551234567',
            risk_level=RiskLevel.HIGH,
            risk_score=75.0,
            is_spam=True,
            total_reports=25,
            spam_reports=spam_reports,
            caller_id=caller_id,
            databases_checked=['Database 1', 'Database 2'],
            confidence_score=80.0,
            processing_time=2.5
        )
        
        report = self.checker.generate_reputation_report(result)
        
        self.assertIsInstance(report, str)
        self.assertIn('COMPREHENSIVE REPUTATION ANALYSIS', report)
        self.assertIn('+15551234567', report)
        self.assertIn('High', report)
        self.assertIn('75.0%', report)
        self.assertIn('YES', report)  # Spam status
        self.assertIn('Test Source', report)
        self.assertIn('Scam', report)
        self.assertIn('Test Caller', report)
        self.assertIn('Test Business', report)


class TestReputationCheckerIntegration(unittest.TestCase):
    """Integration tests for ReputationChecker"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.checker = ReputationChecker()
    
    def test_spam_category_weights(self):
        """Test that spam category weights are properly configured"""
        # High severity categories should have higher weights
        self.assertEqual(self.checker.category_weights[SpamCategory.SCAM], 1.0)
        self.assertEqual(self.checker.category_weights[SpamCategory.FRAUD], 1.0)
        self.assertGreater(
            self.checker.category_weights[SpamCategory.HARASSMENT],
            self.checker.category_weights[SpamCategory.TELEMARKETING]
        )
        self.assertGreater(
            self.checker.category_weights[SpamCategory.TELEMARKETING],
            self.checker.category_weights[SpamCategory.PROMOTIONAL]
        )
    
    def test_database_reliability_weights(self):
        """Test database reliability weight configuration"""
        # Truecaller should have high reliability
        self.assertGreaterEqual(self.checker.spam_databases['truecaller']['weight'], 0.85)
        
        # Community lists should have lower reliability
        self.assertLessEqual(self.checker.spam_databases['community_lists']['weight'], 0.70)
        
        # All weights should be between 0 and 1
        for db_config in self.checker.spam_databases.values():
            self.assertGreaterEqual(db_config['weight'], 0.0)
            self.assertLessEqual(db_config['weight'], 1.0)
    
    def test_risk_threshold_boundaries(self):
        """Test risk level threshold boundaries"""
        boundary_tests = [
            (79.9, RiskLevel.HIGH),
            (80.0, RiskLevel.CRITICAL),
            (59.9, RiskLevel.MEDIUM),
            (60.0, RiskLevel.HIGH),
            (39.9, RiskLevel.LOW),
            (40.0, RiskLevel.MEDIUM)
        ]
        
        for score, expected_level in boundary_tests:
            level = self.checker._classify_risk_level(score)
            self.assertEqual(level, expected_level,
                           f"Score {score} should map to {expected_level}, got {level}")
    
    def test_comprehensive_workflow(self):
        """Test complete reputation checking workflow"""
        # Test with different types of numbers
        test_numbers = [
            ('+15551234567', 'US'),    # Regular US number
            ('+919876543210', 'IN'),   # Regular Indian number
            ('+15559999999', 'US'),    # Spam pattern
            ('+18005551234', 'US'),    # Business number
        ]
        
        for phone_number, country_code in test_numbers:
            with self.subTest(phone=phone_number, country=country_code):
                result = self.checker.check_reputation(phone_number, country_code)
                
                # Basic validation
                self.assertIsInstance(result, ReputationResult)
                self.assertEqual(result.phone_number, phone_number)
                self.assertIn(result.risk_level, [RiskLevel.LOW, RiskLevel.MEDIUM, RiskLevel.HIGH, RiskLevel.CRITICAL])
                self.assertGreaterEqual(result.risk_score, 0.0)
                self.assertLessEqual(result.risk_score, 100.0)
                self.assertGreaterEqual(result.confidence_score, 0.0)
                self.assertLessEqual(result.confidence_score, 100.0)
                self.assertGreater(result.processing_time, 0.0)
                
                # Report generation should work
                report = self.checker.generate_reputation_report(result)
                self.assertIsInstance(report, str)
                self.assertGreater(len(report), 100)


if __name__ == '__main__':
    unittest.main()