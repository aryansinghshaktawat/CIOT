"""
Tests for Historical Data Manager
Database integration tests for historical tracking functionality
"""

import pytest
import sqlite3
import tempfile
import os
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock

from src.utils.historical_data_manager import (
    HistoricalDataManager, 
    PhoneInvestigationRecord, 
    HistoricalChange
)


class TestHistoricalDataManager:
    """Test suite for HistoricalDataManager"""
    
    @pytest.fixture
    def temp_db_path(self):
        """Create temporary database for testing"""
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        temp_file.close()
        yield temp_file.name
        os.unlink(temp_file.name)
    
    @pytest.fixture
    def setup_test_db(self):
        test_db = 'data/test_phone_history.db'
        if os.path.exists(test_db):
            os.remove(test_db)
        return test_db

    def test_add_and_get_history(self, setup_test_db):
        db_path = setup_test_db
        manager = HistoricalDataManager(db_path)
        
        # Create sample intelligence data
        intelligence_data1 = {
            'technical_intelligence': {'country_code': 'IN', 'location': 'LocationA', 'number_type': 'Mobile', 'is_valid': True, 'is_mobile': True},
            'carrier_intelligence': {'carrier_name': 'CarrierA'},
            'security_intelligence': {'reputation_score': 0.9},
            'social_intelligence': {},
            'business_intelligence': {'domains': []},
            'api_sources_used': ['test'],
            'confidence_score': 0.9
        }
        
        intelligence_data2 = {
            'technical_intelligence': {'country_code': 'IN', 'location': 'LocationA', 'number_type': 'Mobile', 'is_valid': True, 'is_mobile': True},
            'carrier_intelligence': {'carrier_name': 'CarrierB'},
            'security_intelligence': {'reputation_score': 0.8},
            'social_intelligence': {},
            'business_intelligence': {'domains': []},
            'api_sources_used': ['test'],
            'confidence_score': 0.8
        }
        
        manager.store_investigation_data('1234567890', intelligence_data1)
        manager.store_investigation_data('1234567890', intelligence_data2)
        
        history = manager.get_historical_data('1234567890')
        assert history['total_records'] == 2
        assert history['investigations'][1]['carrier_name'] == 'CarrierA'  # Older record
        assert history['investigations'][0]['carrier_name'] == 'CarrierB'  # Newer record

    def test_detect_porting(self, setup_test_db):
        db_path = setup_test_db
        manager = HistoricalDataManager(db_path)
        
        # Create sample intelligence data with different carriers
        intelligence_data1 = {
            'technical_intelligence': {'country_code': 'IN', 'location': 'LocationA', 'number_type': 'Mobile', 'is_valid': True, 'is_mobile': True},
            'carrier_intelligence': {'carrier_name': 'CarrierA'},
            'security_intelligence': {'reputation_score': 0.9},
            'social_intelligence': {},
            'business_intelligence': {'domains': []},
            'api_sources_used': ['test'],
            'confidence_score': 0.9
        }
        
        intelligence_data2 = {
            'technical_intelligence': {'country_code': 'IN', 'location': 'LocationA', 'number_type': 'Mobile', 'is_valid': True, 'is_mobile': True},
            'carrier_intelligence': {'carrier_name': 'CarrierB'},
            'security_intelligence': {'reputation_score': 0.8},
            'social_intelligence': {},
            'business_intelligence': {'domains': []},
            'api_sources_used': ['test'],
            'confidence_score': 0.8
        }
        
        manager.store_investigation_data('1234567890', intelligence_data1)
        manager.store_investigation_data('1234567890', intelligence_data2)
        
        porting_analysis = manager.detect_number_porting('1234567890')
        assert porting_analysis['porting_detected'] == True
        assert porting_analysis['total_transitions'] >= 1
        assert porting_analysis['current_carrier'] == 'CarrierB'
        assert porting_analysis['original_carrier'] == 'CarrierA'

    def test_detect_ownership_change(self, setup_test_db):
        db_path = setup_test_db
        manager = HistoricalDataManager(db_path)
        
        # Create sample intelligence data with significant reputation change (ownership indicator)
        intelligence_data1 = {
            'technical_intelligence': {'country_code': 'IN', 'location': 'LocationA', 'number_type': 'Mobile', 'is_valid': True, 'is_mobile': True},
            'carrier_intelligence': {'carrier_name': 'CarrierA'},
            'security_intelligence': {'reputation_score': 0.9},
            'social_intelligence': {'whatsapp_presence': True},
            'business_intelligence': {'domains': ['example.com']},
            'api_sources_used': ['test'],
            'confidence_score': 0.9
        }
        
        intelligence_data2 = {
            'technical_intelligence': {'country_code': 'IN', 'location': 'LocationA', 'number_type': 'Mobile', 'is_valid': True, 'is_mobile': True},
            'carrier_intelligence': {'carrier_name': 'CarrierA'},
            'security_intelligence': {'reputation_score': 0.2},  # Significant drop
            'social_intelligence': {'whatsapp_presence': False},  # Social change
            'business_intelligence': {'domains': []},  # Domain change
            'api_sources_used': ['test'],
            'confidence_score': 0.7
        }
        
        manager.store_investigation_data('1234567890', intelligence_data1)
        manager.store_investigation_data('1234567890', intelligence_data2)
        
        ownership_analysis = manager.detect_ownership_changes('1234567890')
        assert 'ownership_changes_detected' in ownership_analysis
        assert 'confidence_score' in ownership_analysis
        assert 'indicators' in ownership_analysis

    def test_investigation_history(self, setup_test_db):
        db_path = setup_test_db
        manager = HistoricalDataManager(db_path)
        
        # Create sample intelligence data
        intelligence_data1 = {
            'technical_intelligence': {'country_code': 'IN', 'location': 'LocationA', 'number_type': 'Mobile', 'is_valid': True, 'is_mobile': True},
            'carrier_intelligence': {'carrier_name': 'CarrierA'},
            'security_intelligence': {'reputation_score': 0.9},
            'social_intelligence': {},
            'business_intelligence': {'domains': []},
            'api_sources_used': ['test'],
            'confidence_score': 0.9
        }
        
        intelligence_data2 = {
            'technical_intelligence': {'country_code': 'IN', 'location': 'LocationA', 'number_type': 'Mobile', 'is_valid': True, 'is_mobile': True},
            'carrier_intelligence': {'carrier_name': 'CarrierB'},
            'security_intelligence': {'reputation_score': 0.8},
            'social_intelligence': {},
            'business_intelligence': {'domains': []},
            'api_sources_used': ['test'],
            'confidence_score': 0.8
        }
        
        manager.store_investigation_data('1234567890', intelligence_data1)
        manager.store_investigation_data('1234567890', intelligence_data2)
        
        # Test comprehensive investigation history summary
        history_summary = manager.get_investigation_history_summary('1234567890')
        assert history_summary['phone_number'] == '1234567890'
        assert 'historical_data' in history_summary
        assert 'change_timeline' in history_summary
        assert 'porting_analysis' in history_summary
        assert 'ownership_analysis' in history_summary
        assert 'confidence_analysis' in history_summary
    
    @pytest.fixture
    def manager(self, temp_db_path):
        """Create HistoricalDataManager instance for testing"""
        return HistoricalDataManager(db_path=temp_db_path)
    
    @pytest.fixture
    def sample_intelligence_data(self):
        """Sample intelligence data for testing"""
        return {
            'technical_intelligence': {
                'country_code': 'IN',
                'location': 'Mumbai',
                'number_type': 'Mobile',
                'is_valid': True,
                'is_mobile': True
            },
            'carrier_intelligence': {
                'carrier_name': 'Airtel'
            },
            'security_intelligence': {
                'reputation_score': 0.8
            },
            'social_intelligence': {
                'whatsapp_presence': True,
                'telegram_presence': False
            },
            'business_intelligence': {
                'domains': ['example.com', 'test.org']
            },
            'api_sources_used': ['truecaller', 'numverify'],
            'confidence_score': 0.85
        }
    
    def test_database_initialization(self, manager):
        """Test database initialization creates required tables"""
        # Check if database file exists
        assert os.path.exists(manager.db_path)
        
        # Check if tables exist
        with sqlite3.connect(manager.db_path) as conn:
            cursor = conn.cursor()
            
            # Get table names
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = [row[0] for row in cursor.fetchall()]
            
            expected_tables = [
                'phone_investigations',
                'historical_changes',
                'carrier_transitions',
                'investigation_metadata'
            ]
            
            for table in expected_tables:
                assert table in tables, f"Table {table} not found"
    
    def test_store_investigation_data(self, manager, sample_intelligence_data):
        """Test storing investigation data"""
        phone_number = "+919876543210"
        
        # Store data
        manager.store_investigation_data(phone_number, sample_intelligence_data)
        
        # Verify data was stored
        with sqlite3.connect(manager.db_path) as conn:
            cursor = conn.cursor()
            
            # Check phone_investigations table
            cursor.execute("SELECT COUNT(*) FROM phone_investigations WHERE phone_number = ?", (phone_number,))
            count = cursor.fetchone()[0]
            assert count == 1
            
            # Check investigation_metadata table
            cursor.execute("SELECT COUNT(*) FROM investigation_metadata WHERE phone_number = ?", (phone_number,))
            count = cursor.fetchone()[0]
            assert count == 1
    
    def test_get_historical_data(self, manager, sample_intelligence_data):
        """Test retrieving historical data"""
        phone_number = "+919876543210"
        
        # Store some data first
        manager.store_investigation_data(phone_number, sample_intelligence_data)
        
        # Retrieve historical data
        historical_data = manager.get_historical_data(phone_number)
        
        assert historical_data['phone_number'] == phone_number
        assert historical_data['total_records'] == 1
        assert len(historical_data['investigations']) == 1
        assert 'metadata' in historical_data
        
        # Check investigation data
        investigation = historical_data['investigations'][0]
        assert investigation['carrier_name'] == 'Airtel'
        assert investigation['country_code'] == 'IN'
        assert investigation['is_valid'] == True
    
    def test_detect_changes(self, manager, sample_intelligence_data):
        """Test change detection functionality"""
        phone_number = "+919876543210"
        
        # Store initial data
        manager.store_investigation_data(phone_number, sample_intelligence_data)
        
        # Modify data for second investigation
        modified_data = sample_intelligence_data.copy()
        modified_data['carrier_intelligence']['carrier_name'] = 'Jio'
        modified_data['security_intelligence']['reputation_score'] = 0.6
        
        # Store modified data
        manager.store_investigation_data(phone_number, modified_data)
        
        # Get historical data and detect changes
        historical_data = manager.get_historical_data(phone_number, limit=2)
        current_data = {
            'phone_number': phone_number,
            'carrier_name': 'Jio',
            'reputation_score': 0.6
        }
        
        changes = manager.detect_changes(current_data, historical_data)
        
        assert changes['total_changes'] >= 1
        assert any(change['field_name'] == 'carrier_name' for change in changes['changes_detected'])
    
    def test_carrier_porting_detection(self, manager, sample_intelligence_data):
        """Test carrier porting detection"""
        phone_number = "+919876543210"
        
        # Store initial data with Airtel
        manager.store_investigation_data(phone_number, sample_intelligence_data)
        
        # Store data with different carrier (Jio)
        modified_data = sample_intelligence_data.copy()
        modified_data['carrier_intelligence']['carrier_name'] = 'Jio'
        manager.store_investigation_data(phone_number, modified_data)
        
        # Check porting detection
        porting_analysis = manager.detect_number_porting(phone_number)
        
        assert porting_analysis['porting_detected'] == True
        assert porting_analysis['total_transitions'] >= 1
        assert porting_analysis['current_carrier'] == 'Jio'
        assert porting_analysis['original_carrier'] == 'Airtel'
    
    def test_ownership_change_detection(self, manager, sample_intelligence_data):
        """Test ownership change detection"""
        phone_number = "+919876543210"
        
        # Store initial data
        manager.store_investigation_data(phone_number, sample_intelligence_data)
        
        # Store data with significant reputation change
        modified_data = sample_intelligence_data.copy()
        modified_data['security_intelligence']['reputation_score'] = 0.2  # Significant drop
        modified_data['social_intelligence']['whatsapp_presence'] = False  # Social change
        manager.store_investigation_data(phone_number, modified_data)
        
        # Detect ownership changes
        ownership_analysis = manager.detect_ownership_changes(phone_number)
        
        assert 'ownership_changes_detected' in ownership_analysis
        assert 'confidence_score' in ownership_analysis
        assert 'indicators' in ownership_analysis
    
    def test_change_timeline_generation(self, manager, sample_intelligence_data):
        """Test change timeline generation"""
        phone_number = "+919876543210"
        
        # Store initial data
        manager.store_investigation_data(phone_number, sample_intelligence_data)
        
        # Store modified data to create changes
        modified_data = sample_intelligence_data.copy()
        modified_data['carrier_intelligence']['carrier_name'] = 'Jio'
        manager.store_investigation_data(phone_number, modified_data)
        
        # Generate timeline
        timeline = manager.generate_change_timeline(phone_number)
        
        assert isinstance(timeline, list)
        if timeline:  # If changes were detected
            assert 'event_type' in timeline[0]
            assert 'timestamp' in timeline[0]
    
    def test_confidence_scoring(self, manager, sample_intelligence_data):
        """Test change confidence scoring"""
        phone_number = "+919876543210"
        
        # Store some data
        manager.store_investigation_data(phone_number, sample_intelligence_data)
        
        # Calculate confidence scoring
        confidence_analysis = manager.calculate_change_confidence_scoring(phone_number)
        
        assert 'stability_score' in confidence_analysis
        assert 'change_frequency' in confidence_analysis
        assert 'overall_confidence' in confidence_analysis
        assert 'verification_recommendations' in confidence_analysis
        assert 'risk_level' in confidence_analysis
    
    def test_investigation_history_summary(self, manager, sample_intelligence_data):
        """Test comprehensive investigation history summary"""
        phone_number = "+919876543210"
        
        # Store data
        manager.store_investigation_data(phone_number, sample_intelligence_data)
        
        # Get summary
        summary = manager.get_investigation_history_summary(phone_number)
        
        assert summary['phone_number'] == phone_number
        assert 'historical_data' in summary
        assert 'change_timeline' in summary
        assert 'porting_analysis' in summary
        assert 'ownership_analysis' in summary
        assert 'confidence_analysis' in summary
        assert 'recommendations' in summary
    
    def test_hash_phone_number(self, manager):
        """Test phone number hashing for privacy"""
        phone1 = "+919876543210"
        phone2 = "+919876543211"
        
        hash1 = manager._hash_phone_number(phone1)
        hash2 = manager._hash_phone_number(phone2)
        
        # Hashes should be different for different numbers
        assert hash1 != hash2
        
        # Same number should produce same hash
        assert hash1 == manager._hash_phone_number(phone1)
        
        # Hash should be 64 characters (SHA256)
        assert len(hash1) == 64
    
    def test_data_cleanup(self, manager, sample_intelligence_data):
        """Test old data cleanup functionality"""
        phone_number = "+919876543210"
        
        # Store data
        manager.store_investigation_data(phone_number, sample_intelligence_data)
        
        # Test cleanup with very short retention (should delete everything)
        cleanup_result = manager.cleanup_old_data(retention_days=0)
        
        assert cleanup_result['cleanup_completed'] == True
        assert 'records_deleted' in cleanup_result
        assert 'total_deleted' in cleanup_result
    
    def test_multiple_investigations_same_number(self, manager, sample_intelligence_data):
        """Test multiple investigations for the same number"""
        phone_number = "+919876543210"
        
        # Store multiple investigations
        for i in range(3):
            modified_data = sample_intelligence_data.copy()
            modified_data['security_intelligence']['reputation_score'] = 0.8 - (i * 0.1)
            manager.store_investigation_data(phone_number, modified_data)
        
        # Check historical data
        historical_data = manager.get_historical_data(phone_number)
        
        assert historical_data['total_records'] == 3
        assert historical_data['metadata']['total_investigations'] == 3
    
    def test_error_handling_invalid_data(self, manager):
        """Test error handling with invalid data"""
        phone_number = "+919876543210"
        invalid_data = {}  # Empty data
        
        # Should not raise exception
        try:
            manager.store_investigation_data(phone_number, invalid_data)
        except Exception as e:
            pytest.fail(f"Should handle invalid data gracefully: {e}")
        
        # Should return empty results for non-existent number
        historical_data = manager.get_historical_data("+919999999999")
        assert historical_data['total_records'] == 0
    
    def test_database_indexes(self, manager):
        """Test that database indexes are created properly"""
        with sqlite3.connect(manager.db_path) as conn:
            cursor = conn.cursor()
            
            # Check for indexes
            cursor.execute("SELECT name FROM sqlite_master WHERE type='index'")
            indexes = [row[0] for row in cursor.fetchall()]
            
            expected_indexes = [
                'idx_phone_hash',
                'idx_phone_timestamp',
                'idx_changes_phone',
                'idx_transitions_phone',
                'idx_metadata_phone'
            ]
            
            for index in expected_indexes:
                assert index in indexes, f"Index {index} not found"
    
    def test_concurrent_access(self, manager, sample_intelligence_data):
        """Test concurrent database access"""
        phone_number = "+919876543210"
        
        # Simulate concurrent access by creating multiple connections
        import threading
        import time
        
        def store_data(thread_id):
            modified_data = sample_intelligence_data.copy()
            modified_data['thread_id'] = thread_id
            manager.store_investigation_data(f"{phone_number}_{thread_id}", modified_data)
        
        # Create multiple threads
        threads = []
        for i in range(3):
            thread = threading.Thread(target=store_data, args=(i,))
            threads.append(thread)
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        # Verify all data was stored
        for i in range(3):
            historical_data = manager.get_historical_data(f"{phone_number}_{i}")
            assert historical_data['total_records'] == 1


class TestPhoneInvestigationRecord:
    """Test PhoneInvestigationRecord data class"""
    
    def test_record_creation(self):
        """Test creating investigation record"""
        record = PhoneInvestigationRecord(
            phone_number="+919876543210",
            investigation_timestamp=datetime.now(),
            country_code="IN",
            carrier_name="Airtel",
            location="Mumbai",
            number_type="Mobile",
            is_valid=True,
            is_mobile=True,
            reputation_score=0.8,
            social_media_presence={"whatsapp": True},
            whois_domains=["example.com"],
            api_sources=["truecaller"],
            confidence_score=0.85,
            raw_data={"test": "data"}
        )
        
        assert record.phone_number == "+919876543210"
        assert record.carrier_name == "Airtel"
        assert record.is_valid == True
        assert record.reputation_score == 0.8


class TestHistoricalChange:
    """Test HistoricalChange data class"""
    
    def test_change_creation(self):
        """Test creating historical change record"""
        change = HistoricalChange(
            phone_number="+919876543210",
            change_type="Carrier Change",
            field_name="carrier_name",
            old_value="Airtel",
            new_value="Jio",
            change_timestamp=datetime.now(),
            confidence_score=0.9,
            verification_status="Detected",
            change_source="Automated Detection"
        )
        
        assert change.phone_number == "+919876543210"
        assert change.change_type == "Carrier Change"
        assert change.old_value == "Airtel"
        assert change.new_value == "Jio"
        assert change.confidence_score == 0.9


if __name__ == "__main__":
    pytest.main([__file__])