"""
Pytest configuration and shared fixtures for comprehensive testing suite
"""

import pytest
import asyncio
import os
import sys
import tempfile
import shutil
from unittest.mock import Mock, MagicMock, patch
from typing import Dict, Any, List, Optional
import sqlite3
from datetime import datetime, timedelta

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

# Import test utilities
from utils.cached_phone_formatter import CachedPhoneNumberFormatter
from utils.intelligence_aggregator import IntelligenceAggregator
from utils.async_intelligence_aggregator import AsyncIntelligenceAggregator
from utils.historical_data_manager import HistoricalDataManager
from utils.pattern_analysis import PatternAnalysisEngine


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def temp_db_path():
    """Create a temporary database path for testing"""
    temp_dir = tempfile.mkdtemp()
    db_path = os.path.join(temp_dir, "test_phone_history.db")
    yield db_path
    # Cleanup
    if os.path.exists(db_path):
        os.remove(db_path)
    shutil.rmtree(temp_dir, ignore_errors=True)


@pytest.fixture
def mock_phone_formatter():
    """Mock phone formatter for testing"""
    formatter = Mock(spec=CachedPhoneNumberFormatter)
    formatter.format_phone_number.return_value = {
        'success': True,
        'best_format': {
            'international': '+91 98765 43210',
            'national': '98765 43210',
            'e164': '+919876543210',
            'rfc3966': 'tel:+91-98765-43210'
        },
        'parsing_attempts': ['international_format'],
        'validation_results': {
            'is_valid': True,
            'is_possible': True,
            'country_code': 91,
            'country_name': 'India',
            'region_code': 'IN',
            'location': 'India',
            'number_type': 'MOBILE',
            'carrier': 'Airtel'
        }
    }
    return formatter


@pytest.fixture
def mock_intelligence_aggregator():
    """Mock intelligence aggregator for testing"""
    aggregator = Mock(spec=IntelligenceAggregator)
    aggregator.gather_comprehensive_intelligence.return_value = {
        'technical_intelligence': {
            'is_valid': True,
            'country_name': 'India',
            'carrier': 'Airtel'
        },
        'security_intelligence': {
            'spam_risk_score': 0.2,
            'reputation_status': 'Clean'
        },
        'social_intelligence': {
            'whatsapp_status': {'exists': True},
            'telegram_profile': {'found': False}
        },
        'business_intelligence': {
            'whois_domains': [],
            'business_connections': []
        },
        'pattern_intelligence': {
            'related_numbers': [],
            'bulk_registration_status': {'detected': False}
        },
        'historical_intelligence': {
            'historical_changes': [],
            'change_timeline': []
        }
    }
    return aggregator


@pytest.fixture
def sample_phone_numbers():
    """Sample phone numbers for testing"""
    return {
        'valid_indian': '9876543210',
        'valid_indian_formatted': '+91 98765 43210',
        'valid_us': '+1 555 123 4567',
        'valid_uk': '+44 20 7946 0958',
        'invalid_format': 'invalid_phone',
        'invalid_length': '123',
        'suspicious_pattern': '1111111111',
        'test_numbers': [
            '9876543210',
            '9876543211',
            '9876543212',
            '8765432109',
            '7654321098'
        ]
    }


@pytest.fixture
def sample_investigation_results():
    """Sample investigation results for testing"""
    return {
        'success': True,
        'original_input': '9876543210',
        'investigation_timestamp': datetime.now(),
        'formatting_success': True,
        'formatting_method': 'international_format',
        'international_format': '+91 98765 43210',
        'national_format': '98765 43210',
        'e164_format': '+919876543210',
        'rfc3966_format': 'tel:+91-98765-43210',
        'is_valid': True,
        'is_possible': True,
        'country_code': 91,
        'country_name': 'India',
        'region_code': 'IN',
        'location': 'India',
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
            'whatsapp': {'exists': True},
            'telegram': {'found': False}
        },
        'whois_domains': [],
        'business_connections': [],
        'related_numbers': [],
        'bulk_registration_status': {'detected': False},
        'historical_changes': [],
        'change_timeline': [],
        'confidence_score': 0.85,
        'investigation_quality': 'High',
        'api_sources_used': ['libphonenumber', 'AbstractAPI'],
        'total_sources': 2
    }


@pytest.fixture
def mock_api_responses():
    """Mock API responses for testing"""
    return {
        'abstractapi_success': {
            'phone': '+919876543210',
            'valid': True,
            'country': {
                'code': 'IN',
                'name': 'India'
            },
            'carrier': 'Airtel',
            'line_type': 'mobile'
        },
        'neutrino_success': {
            'valid': True,
            'country': 'India',
            'location': 'Mumbai',
            'carrier': 'Airtel'
        },
        'api_error': {
            'error': 'API rate limit exceeded',
            'code': 429
        }
    }


@pytest.fixture
def mock_historical_data():
    """Mock historical data for testing"""
    return [
        {
            'phone_number': '9876543210',
            'investigation_date': datetime.now() - timedelta(days=30),
            'carrier': 'Vodafone',
            'location': 'Delhi',
            'spam_score': 0.1
        },
        {
            'phone_number': '9876543210',
            'investigation_date': datetime.now() - timedelta(days=15),
            'carrier': 'Airtel',
            'location': 'Mumbai',
            'spam_score': 0.2
        }
    ]


@pytest.fixture
def performance_test_config():
    """Configuration for performance tests"""
    return {
        'max_response_time': 5.0,  # 5 seconds max
        'concurrent_requests': 10,
        'test_iterations': 100,
        'memory_limit_mb': 100,
        'cache_hit_ratio_min': 0.8
    }


@pytest.fixture
def ui_test_config():
    """Configuration for UI tests"""
    return {
        'window_size': (1200, 800),
        'test_timeout': 30,
        'element_wait_time': 5,
        'screenshot_on_failure': True
    }


@pytest.fixture(autouse=True)
def cleanup_caches():
    """Automatically cleanup caches after each test"""
    yield
    # Cleanup any caches or temporary data
    try:
        from utils.performance_cache import clear_performance_caches
        clear_performance_caches()
    except ImportError:
        pass


@pytest.fixture
def mock_security_manager():
    """Mock security manager for testing"""
    security_manager = Mock()
    security_manager.validate_api_key.return_value = True
    security_manager.check_rate_limit.return_value = True
    security_manager.log_investigation.return_value = None
    security_manager.encrypt_data.return_value = b'encrypted_data'
    security_manager.decrypt_data.return_value = 'decrypted_data'
    return security_manager


@pytest.fixture
def test_database_schema():
    """Create test database schema"""
    def create_test_db(db_path: str):
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Create phone history table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS phone_investigations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                phone_number TEXT NOT NULL,
                investigation_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                country_code TEXT,
                carrier TEXT,
                location TEXT,
                spam_score REAL,
                investigation_data TEXT,
                confidence_score REAL
            )
        ''')
        
        # Create pattern analysis table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS pattern_analysis (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                phone_number TEXT NOT NULL,
                related_numbers TEXT,
                pattern_type TEXT,
                confidence_score REAL,
                analysis_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
    
    return create_test_db


# Pytest markers for test categorization
def pytest_configure(config):
    """Configure pytest markers"""
    config.addinivalue_line(
        "markers", "unit: Unit tests for individual components"
    )
    config.addinivalue_line(
        "markers", "integration: Integration tests for component interactions"
    )
    config.addinivalue_line(
        "markers", "ui: UI automation tests"
    )
    config.addinivalue_line(
        "markers", "performance: Performance and load tests"
    )
    config.addinivalue_line(
        "markers", "e2e: End-to-end workflow tests"
    )
    config.addinivalue_line(
        "markers", "slow: Tests that take longer to run"
    )
    config.addinivalue_line(
        "markers", "api: Tests that require external API calls"
    )


# Test data cleanup
@pytest.fixture(scope="session", autouse=True)
def cleanup_test_data():
    """Cleanup test data after test session"""
    yield
    # Cleanup any persistent test data
    test_files = [
        'test_phone_history.db',
        'test_performance_cache.db',
        'test_audit.log'
    ]
    
    for file in test_files:
        if os.path.exists(file):
            try:
                os.remove(file)
            except OSError:
                pass