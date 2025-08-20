"""
Test Fixtures and Mock Data for Enhanced Phone Investigation Testing
Provides comprehensive mock data and test fixtures for reliable testing
"""

import pytest
import json
import time
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from unittest.mock import Mock, MagicMock
import sqlite3
import tempfile
import os


class MockAPIResponses:
    """Mock API responses for testing"""
    
    @staticmethod
    def get_abstractapi_success(phone_number: str = "9876543210") -> Dict[str, Any]:
        """Mock successful AbstractAPI response"""
        return {
            "phone": f"+91{phone_number}",
            "valid": True,
            "format": {
                "international": f"+91 {phone_number[:5]} {phone_number[5:]}",
                "local": phone_number
            },
            "country": {
                "code": "IN",
                "name": "India",
                "prefix": "+91"
            },
            "location": "Mumbai",
            "type": "mobile",
            "carrier": "Airtel"
        }
    
    @staticmethod
    def get_neutrino_success(phone_number: str = "9876543210") -> Dict[str, Any]:
        """Mock successful Neutrino API response"""
        return {
            "valid": True,
            "international_calling_code": 91,
            "country_code": "IN",
            "country": "India",
            "location": "Mumbai",
            "is_mobile": True,
            "type": "mobile",
            "carrier": "Airtel"
        }
    
    @staticmethod
    def get_findandtrace_success(phone_number: str = "9876543210") -> Dict[str, Any]:
        """Mock successful FindAndTrace API response"""
        return {
            "success": True,
            "data": {
                "number": phone_number,
                "country": "India",
                "carrier": "Airtel",
                "line_type": "Mobile",
                "location": {
                    "city": "Mumbai",
                    "state": "Maharashtra"
                }
            }
        }
    
    @staticmethod
    def get_api_error_response(error_code: int = 429) -> Dict[str, Any]:
        """Mock API error response"""
        error_messages = {
            400: "Bad Request - Invalid phone number format",
            401: "Unauthorized - Invalid API key",
            429: "Rate limit exceeded",
            500: "Internal server error",
            503: "Service unavailable"
        }
        
        return {
            "error": error_messages.get(error_code, "Unknown error"),
            "code": error_code,
            "message": error_messages.get(error_code, "Unknown error occurred")
        }
    
    @staticmethod
    def get_timeout_response() -> Exception:
        """Mock timeout exception"""
        import requests
        return requests.exceptions.Timeout("Request timeout after 30 seconds")
    
    @staticmethod
    def get_connection_error() -> Exception:
        """Mock connection error"""
        import requests
        return requests.exceptions.ConnectionError("Failed to establish connection")


class MockPhoneNumbers:
    """Mock phone numbers for testing"""
    
    VALID_INDIAN_NUMBERS = [
        "9876543210",
        "8765432109",
        "7654321098",
        "9123456789",
        "8987654321"
    ]
    
    VALID_US_NUMBERS = [
        "+1 555 123 4567",
        "+1 555 987 6543",
        "+1 555 246 8135"
    ]
    
    VALID_UK_NUMBERS = [
        "+44 20 7946 0958",
        "+44 161 123 4567"
    ]
    
    INVALID_NUMBERS = [
        "invalid_phone",
        "123",
        "abcdefghij",
        "++91 9876543210",
        "91-9876543210-extra"
    ]
    
    SUSPICIOUS_PATTERNS = [
        "1111111111",
        "1234567890",
        "0000000000",
        "9999999999"
    ]
    
    @classmethod
    def get_test_numbers(cls) -> Dict[str, Any]:
        """Get comprehensive test numbers"""
        return {
            'valid_indian': cls.VALID_INDIAN_NUMBERS[0],
            'valid_indian_formatted': '+91 98765 43210',
            'valid_us': cls.VALID_US_NUMBERS[0],
            'valid_uk': cls.VALID_UK_NUMBERS[0],
            'invalid_format': cls.INVALID_NUMBERS[0],
            'invalid_length': cls.INVALID_NUMBERS[1],
            'suspicious_pattern': cls.SUSPICIOUS_PATTERNS[0],
            'test_numbers': cls.VALID_INDIAN_NUMBERS,
            'international_numbers': cls.VALID_US_NUMBERS + cls.VALID_UK_NUMBERS,
            'all_invalid': cls.INVALID_NUMBERS,
            'suspicious_numbers': cls.SUSPICIOUS_PATTERNS
        }


class MockInvestigationResults:
    """Mock investigation results for testing"""
    
    @staticmethod
    def get_successful_result(phone_number: str = "9876543210") -> Dict[str, Any]:
        """Get mock successful investigation result"""
        return {
            'success': True,
            'original_input': phone_number,
            'investigation_timestamp': datetime.now(),
            'formatting_success': True,
            'formatting_method': 'international_format',
            'international_format': f'+91 {phone_number[:5]} {phone_number[5:]}',
            'national_format': f'{phone_number[:5]} {phone_number[5:]}',
            'e164_format': f'+91{phone_number}',
            'rfc3966_format': f'tel:+91-{phone_number[:5]}-{phone_number[5:]}',
            'is_valid': True,
            'is_possible': True,
            'country_code': 91,
            'country_name': 'India',
            'region_code': 'IN',
            'location': 'Mumbai',
            'timezones': ['Asia/Kolkata'],
            'number_type': 'MOBILE',
            'is_mobile': True,
            'is_fixed_line': False,
            'carrier_name': 'Airtel',
            'network_type': '4G',
            'spam_risk_score': 0.2,
            'spam_reports': [],
            'breach_data': [],
            'reputation_status': 'Clean',
            'social_media_presence': {
                'whatsapp': {'exists': True, 'last_seen': 'Recently'},
                'telegram': {'found': False},
                'signal': {'found': False}
            },
            'whois_domains': [],
            'business_connections': [],
            'related_numbers': [
                {'number': '9876543211', 'confidence': 0.8, 'pattern_type': 'sequential'},
                {'number': '9876543212', 'confidence': 0.7, 'pattern_type': 'sequential'}
            ],
            'bulk_registration_status': {
                'detected': False,
                'confidence': 0.1,
                'block_size': 0
            },
            'historical_changes': [],
            'change_timeline': [],
            'confidence_score': 0.85,
            'investigation_quality': 'High',
            'api_sources_used': ['libphonenumber', 'AbstractAPI', 'NeutrinoAPI'],
            'total_sources': 3,
            'processing_time': 2.34,
            'cache_used': False,
            'fallback_used': False
        }
    
    @staticmethod
    def get_failed_result(phone_number: str = "invalid", error_message: str = "Invalid phone number format") -> Dict[str, Any]:
        """Get mock failed investigation result"""
        return {
            'success': False,
            'original_input': phone_number,
            'investigation_timestamp': datetime.now(),
            'error': error_message,
            'error_code': 'INVALID_FORMAT',
            'error_details': {
                'attempted_formats': ['international', 'national', 'e164'],
                'parsing_errors': ['Invalid country code', 'Invalid number length']
            },
            'guidance': {
                'message': 'Please enter a valid phone number',
                'examples': ['+91 98765 43210', '9876543210'],
                'format_help': 'Indian numbers should be 10 digits starting with 6-9'
            },
            'suggested_country': 'IN',
            'confidence_score': 0.0,
            'investigation_quality': 'Failed',
            'processing_time': 0.12,
            'fallback_used': True
        }
    
    @staticmethod
    def get_partial_result(phone_number: str = "9876543210") -> Dict[str, Any]:
        """Get mock partial investigation result (some APIs failed)"""
        result = MockInvestigationResults.get_successful_result(phone_number)
        result.update({
            'confidence_score': 0.6,
            'investigation_quality': 'Partial',
            'api_sources_used': ['libphonenumber'],  # Only basic formatting worked
            'total_sources': 1,
            'api_errors': {
                'AbstractAPI': 'Rate limit exceeded',
                'NeutrinoAPI': 'Connection timeout'
            },
            'social_media_presence': {},  # Empty due to API failures
            'business_connections': [],
            'related_numbers': []
        })
        return result


class MockHistoricalData:
    """Mock historical data for testing"""
    
    @staticmethod
    def get_historical_records(phone_number: str = "9876543210", count: int = 3) -> List[Dict[str, Any]]:
        """Get mock historical investigation records"""
        records = []
        base_date = datetime.now() - timedelta(days=90)
        
        carriers = ['Vodafone', 'Airtel', 'Jio']
        locations = ['Delhi', 'Mumbai', 'Bangalore']
        spam_scores = [0.1, 0.2, 0.15]
        
        for i in range(count):
            record = {
                'phone_number': phone_number,
                'investigation_date': base_date + timedelta(days=30*i),
                'country_code': 91,
                'country_name': 'India',
                'carrier': carriers[i % len(carriers)],
                'location': locations[i % len(locations)],
                'spam_score': spam_scores[i % len(spam_scores)],
                'confidence_score': 0.8 + (i * 0.05),
                'investigation_data': json.dumps({
                    'number_type': 'MOBILE',
                    'is_valid': True,
                    'network_type': '4G'
                })
            }
            records.append(record)
        
        return records
    
    @staticmethod
    def get_change_timeline(phone_number: str = "9876543210") -> List[Dict[str, Any]]:
        """Get mock change timeline"""
        return [
            {
                'change_type': 'carrier_change',
                'timestamp': datetime.now() - timedelta(days=60),
                'old_value': 'Vodafone',
                'new_value': 'Airtel',
                'confidence': 0.9
            },
            {
                'change_type': 'location_change',
                'timestamp': datetime.now() - timedelta(days=30),
                'old_value': 'Delhi',
                'new_value': 'Mumbai',
                'confidence': 0.7
            },
            {
                'change_type': 'spam_score_change',
                'timestamp': datetime.now() - timedelta(days=15),
                'old_value': 0.1,
                'new_value': 0.2,
                'confidence': 0.8
            }
        ]


class MockPatternAnalysis:
    """Mock pattern analysis data for testing"""
    
    @staticmethod
    def get_related_numbers(phone_number: str = "9876543210") -> List[Dict[str, Any]]:
        """Get mock related numbers"""
        base_number = int(phone_number)
        related = []
        
        # Sequential numbers
        for i in range(1, 4):
            related.append({
                'number': str(base_number + i),
                'confidence': 0.8 - (i * 0.1),
                'pattern_type': 'sequential',
                'relationship': f'Sequential +{i}'
            })
        
        # Similar pattern numbers
        similar_patterns = [
            {'number': '9876543201', 'confidence': 0.6, 'pattern_type': 'digit_swap', 'relationship': 'Digit swap'},
            {'number': '9876543012', 'confidence': 0.5, 'pattern_type': 'digit_rotation', 'relationship': 'Digit rotation'}
        ]
        
        related.extend(similar_patterns)
        return related
    
    @staticmethod
    def get_bulk_registration_analysis(phone_number: str = "9876543210") -> Dict[str, Any]:
        """Get mock bulk registration analysis"""
        # Simulate different scenarios based on number pattern
        if phone_number.endswith('0000') or phone_number == '1111111111':
            return {
                'detected': True,
                'confidence': 0.9,
                'block_size': 1000,
                'registration_pattern': 'sequential_block',
                'risk_level': 'high',
                'evidence': [
                    'Sequential number pattern detected',
                    'Large block registration identified',
                    'Suspicious timing pattern'
                ]
            }
        else:
            return {
                'detected': False,
                'confidence': 0.2,
                'block_size': 0,
                'registration_pattern': 'individual',
                'risk_level': 'low',
                'evidence': []
            }


class TestDatabaseManager:
    """Test database manager for creating and managing test databases"""
    
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.connection = None
    
    def create_test_database(self):
        """Create test database with required tables"""
        self.connection = sqlite3.connect(self.db_path)
        cursor = self.connection.cursor()
        
        # Phone investigations table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS phone_investigations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                phone_number TEXT NOT NULL,
                investigation_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                country_code INTEGER,
                country_name TEXT,
                carrier TEXT,
                location TEXT,
                spam_score REAL,
                confidence_score REAL,
                investigation_data TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Pattern analysis table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS pattern_analysis (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                phone_number TEXT NOT NULL,
                related_numbers TEXT,
                pattern_type TEXT,
                confidence_score REAL,
                analysis_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                bulk_registration_data TEXT
            )
        ''')
        
        # Cache table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS cache_entries (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                cache_key TEXT UNIQUE NOT NULL,
                cache_value TEXT NOT NULL,
                expiry_time TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Performance metrics table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS performance_metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                operation_type TEXT NOT NULL,
                duration REAL NOT NULL,
                success BOOLEAN NOT NULL,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                metadata TEXT
            )
        ''')
        
        self.connection.commit()
    
    def populate_test_data(self, phone_numbers: List[str]):
        """Populate database with test data"""
        if not self.connection:
            self.create_test_database()
        
        cursor = self.connection.cursor()
        
        for phone in phone_numbers:
            # Add historical investigation data
            historical_records = MockHistoricalData.get_historical_records(phone, 2)
            
            for record in historical_records:
                cursor.execute('''
                    INSERT INTO phone_investigations 
                    (phone_number, investigation_date, country_code, country_name, 
                     carrier, location, spam_score, confidence_score, investigation_data)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    record['phone_number'],
                    record['investigation_date'],
                    record['country_code'],
                    record['country_name'],
                    record['carrier'],
                    record['location'],
                    record['spam_score'],
                    record['confidence_score'],
                    record['investigation_data']
                ))
            
            # Add pattern analysis data
            related_numbers = MockPatternAnalysis.get_related_numbers(phone)
            bulk_analysis = MockPatternAnalysis.get_bulk_registration_analysis(phone)
            
            cursor.execute('''
                INSERT INTO pattern_analysis 
                (phone_number, related_numbers, pattern_type, confidence_score, bulk_registration_data)
                VALUES (?, ?, ?, ?, ?)
            ''', (
                phone,
                json.dumps(related_numbers),
                'comprehensive',
                0.8,
                json.dumps(bulk_analysis)
            ))
        
        self.connection.commit()
    
    def cleanup(self):
        """Cleanup test database"""
        if self.connection:
            self.connection.close()
        
        if os.path.exists(self.db_path):
            try:
                os.remove(self.db_path)
            except OSError:
                pass


class MockSecurityManager:
    """Mock security manager for testing"""
    
    def __init__(self):
        self.api_calls = []
        self.rate_limits = {}
        self.audit_logs = []
    
    def validate_api_key(self, api_key: str, service: str) -> bool:
        """Mock API key validation"""
        # Simulate different validation results
        if api_key == 'invalid_key':
            return False
        if api_key == 'expired_key':
            return False
        return True
    
    def check_rate_limit(self, service: str, identifier: str) -> bool:
        """Mock rate limit checking"""
        key = f"{service}:{identifier}"
        current_time = time.time()
        
        if key not in self.rate_limits:
            self.rate_limits[key] = []
        
        # Clean old entries (older than 1 minute)
        self.rate_limits[key] = [
            timestamp for timestamp in self.rate_limits[key]
            if current_time - timestamp < 60
        ]
        
        # Check if under limit (max 10 per minute)
        if len(self.rate_limits[key]) >= 10:
            return False
        
        self.rate_limits[key].append(current_time)
        return True
    
    def log_investigation(self, phone_number: str, user_id: str, result: Dict[str, Any]):
        """Mock investigation logging"""
        log_entry = {
            'timestamp': datetime.now(),
            'phone_number': phone_number,
            'user_id': user_id,
            'success': result.get('success', False),
            'confidence_score': result.get('confidence_score', 0)
        }
        self.audit_logs.append(log_entry)
    
    def encrypt_data(self, data: str) -> bytes:
        """Mock data encryption"""
        return f"encrypted_{data}".encode()
    
    def decrypt_data(self, encrypted_data: bytes) -> str:
        """Mock data decryption"""
        return encrypted_data.decode().replace('encrypted_', '')


# Pytest fixtures using the mock classes
@pytest.fixture
def mock_api_responses():
    """Fixture providing mock API responses"""
    return MockAPIResponses()


@pytest.fixture
def comprehensive_phone_numbers():
    """Fixture providing comprehensive phone numbers for testing"""
    return MockPhoneNumbers.get_test_numbers()


@pytest.fixture
def mock_investigation_results():
    """Fixture providing mock investigation results"""
    return MockInvestigationResults()


@pytest.fixture
def mock_historical_data():
    """Fixture providing mock historical data"""
    return MockHistoricalData()


@pytest.fixture
def mock_pattern_analysis():
    """Fixture providing mock pattern analysis data"""
    return MockPatternAnalysis()


@pytest.fixture
def test_database(temp_db_path):
    """Fixture providing test database with sample data"""
    db_manager = TestDatabaseManager(temp_db_path)
    db_manager.create_test_database()
    
    # Populate with sample data
    sample_numbers = MockPhoneNumbers.VALID_INDIAN_NUMBERS[:3]
    db_manager.populate_test_data(sample_numbers)
    
    yield db_manager
    
    db_manager.cleanup()


@pytest.fixture
def mock_security_manager():
    """Fixture providing mock security manager"""
    return MockSecurityManager()


if __name__ == '__main__':
    # Test the mock classes
    print("Testing mock classes...")
    
    # Test API responses
    api_mock = MockAPIResponses()
    print("AbstractAPI Success:", api_mock.get_abstractapi_success())
    print("API Error:", api_mock.get_api_error_response(429))
    
    # Test phone numbers
    phone_mock = MockPhoneNumbers()
    print("Test Numbers:", phone_mock.get_test_numbers())
    
    # Test investigation results
    result_mock = MockInvestigationResults()
    print("Successful Result:", result_mock.get_successful_result())
    
    print("All mock classes working correctly!")