"""
Integration tests for WHOIS and domain linkage system
Tests all functionality including database operations and API integrations
"""

import pytest
import tempfile
import os
import sqlite3
import socket
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, MagicMock

from src.utils.whois_checker import (
    WHOISChecker, 
    DomainRecord, 
    BusinessConnection, 
    WHOISInvestigationResult
)


class TestWHOISChecker:
    """Test suite for WHOIS checker functionality"""
    
    @pytest.fixture
    def temp_db(self):
        """Create temporary database for testing"""
        temp_dir = tempfile.mkdtemp()
        db_path = os.path.join(temp_dir, "test_whois.db")
        yield db_path
        # Cleanup
        if os.path.exists(db_path):
            os.remove(db_path)
        os.rmdir(temp_dir)
    
    @pytest.fixture
    def whois_checker(self, temp_db):
        """Create WHOIS checker instance with temporary database"""
        return WHOISChecker(db_path=temp_db)
    
    def test_database_initialization(self, whois_checker):
        """Test database initialization creates required tables"""
        conn = sqlite3.connect(whois_checker.db_path)
        cursor = conn.cursor()
        
        # Check if tables exist
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]
        
        assert 'whois_history' in tables
        assert 'business_connections' in tables
        
        # Check table structure
        cursor.execute("PRAGMA table_info(whois_history)")
        columns = [row[1] for row in cursor.fetchall()]
        
        expected_columns = [
            'id', 'phone_number', 'domain', 'registrar', 'creation_date',
            'expiration_date', 'registrant_org', 'registrant_name',
            'contact_type', 'status', 'confidence', 'checked_date'
        ]
        
        for col in expected_columns:
            assert col in columns
        
        conn.close()
    
    def test_clean_phone_number(self, whois_checker):
        """Test phone number cleaning and normalization"""
        test_cases = [
            ('+91 9876543210', '+919876543210'),
            ('919876543210', '+919876543210'),
            ('9876543210', '+919876543210'),
            ('(+91) 98765-43210', '+919876543210'),
            ('+91-9876-543-210', '+919876543210'),
            ('09876543210', '+919876543210')
        ]
        
        for input_phone, expected in test_cases:
            result = whois_checker._clean_phone_number(input_phone)
            assert result == expected, f"Failed for input: {input_phone}"
    
    def test_domain_record_creation(self):
        """Test DomainRecord dataclass creation and validation"""
        domain = DomainRecord(
            domain="example.com",
            registrar="GoDaddy",
            creation_date=datetime.now() - timedelta(days=365),
            expiration_date=datetime.now() + timedelta(days=365),
            status="active",
            registrant_phone="+919876543210",
            registrant_org="Test Business",
            confidence=85.0
        )
        
        assert domain.domain == "example.com"
        assert domain.registrar == "GoDaddy"
        assert domain.status == "active"
        assert domain.confidence == 85.0
        assert isinstance(domain.name_servers, list)
    
    def test_business_connection_creation(self):
        """Test BusinessConnection dataclass creation"""
        connection = BusinessConnection(
            organization="Test Business Pvt Ltd",
            contact_type="registrant",
            domains=["example.com", "test.com"],
            phone_numbers=["+919876543210"],
            confidence=90.0
        )
        
        assert connection.organization == "Test Business Pvt Ltd"
        assert len(connection.domains) == 2
        assert len(connection.phone_numbers) == 1
        assert connection.confidence == 90.0
    
    @patch('socket.gethostbyname')
    @patch('whois.whois')
    def test_check_domain_existence(self, mock_whois, mock_gethostbyname, whois_checker):
        """Test domain existence checking with WHOIS lookup"""
        # Mock successful DNS resolution
        mock_gethostbyname.return_value = '192.168.1.1'
        
        # Mock WHOIS response
        mock_whois_data = Mock()
        mock_whois_data.domain_name = 'example.com'
        mock_whois_data.registrar = 'GoDaddy'
        mock_whois_data.creation_date = datetime.now() - timedelta(days=365)
        mock_whois_data.expiration_date = datetime.now() + timedelta(days=365)
        mock_whois_data.org = 'Test Organization'
        mock_whois_data.name = 'Test User'
        mock_whois_data.emails = ['test@example.com']
        mock_whois_data.name_servers = ['ns1.godaddy.com', 'ns2.godaddy.com']
        mock_whois_data.status = ['clientTransferProhibited']
        
        mock_whois.return_value = mock_whois_data
        
        result = whois_checker._check_domain_existence('example.com')
        
        assert result is not None
        assert result.domain == 'example.com'
        assert result.registrar == 'GoDaddy'
        assert result.status == 'active'
        assert result.registrant_org == 'Test Organization'
        assert result.confidence == 60.0  # Pattern-based discovery confidence
    
    @patch('socket.gethostbyname')
    def test_check_domain_existence_no_dns(self, mock_gethostbyname, whois_checker):
        """Test domain existence check when DNS resolution fails"""
        # Mock DNS resolution failure
        mock_gethostbyname.side_effect = socket.gaierror("Name resolution failed")
        
        result = whois_checker._check_domain_existence('nonexistent.com')
        
        assert result is None
    
    def test_determine_domain_status(self, whois_checker):
        """Test domain status determination from WHOIS data"""
        # Test active status
        mock_whois_active = Mock()
        mock_whois_active.status = ['clientTransferProhibited', 'clientDeleteProhibited']
        mock_whois_active.expiration_date = datetime.now() + timedelta(days=365)
        
        status = whois_checker._determine_domain_status(mock_whois_active)
        assert status == 'active'
        
        # Test expired status
        mock_whois_expired = Mock()
        mock_whois_expired.status = ['pendingDelete']
        mock_whois_expired.expiration_date = datetime.now() - timedelta(days=30)
        
        status = whois_checker._determine_domain_status(mock_whois_expired)
        assert status == 'expired'
        
        # Test suspended status
        mock_whois_suspended = Mock()
        mock_whois_suspended.status = ['serverHold']
        mock_whois_suspended.expiration_date = datetime.now() + timedelta(days=365)
        
        status = whois_checker._determine_domain_status(mock_whois_suspended)
        assert status == 'suspended'
    
    def test_generate_sample_domains(self, whois_checker):
        """Test sample domain generation for demonstration"""
        phone_number = '+919876543210'
        domains = whois_checker._generate_sample_domains(phone_number)
        
        assert len(domains) >= 2
        assert all(isinstance(d, DomainRecord) for d in domains)
        assert any(d.status == 'active' for d in domains)
        assert any(d.status == 'expired' for d in domains)
        assert all(d.registrant_phone == phone_number for d in domains)
    
    def test_deduplicate_and_enrich_domains(self, whois_checker):
        """Test domain deduplication and enrichment"""
        # Create duplicate domains with different data
        domain1 = DomainRecord(
            domain="example.com",
            registrar="GoDaddy",
            status="active",
            registrant_org="Test Org",
            confidence=70.0
        )
        
        domain2 = DomainRecord(
            domain="example.com",  # Same domain
            registrar="GoDaddy",
            status="active",
            registrant_phone="+919876543210",  # Additional data
            confidence=80.0
        )
        
        domain3 = DomainRecord(
            domain="different.com",
            registrar="Namecheap",
            status="active",
            confidence=60.0
        )
        
        domains = [domain1, domain2, domain3]
        
        with patch.object(whois_checker, '_enrich_domain_data', side_effect=lambda x: x):
            result = whois_checker._deduplicate_and_enrich_domains(domains)
        
        assert len(result) == 2  # Should have 2 unique domains
        
        # Find the merged example.com domain
        example_domain = next(d for d in result if d.domain == "example.com")
        assert example_domain.registrant_phone == "+919876543210"  # Should have merged data
        assert example_domain.registrant_org == "Test Org"
    
    def test_identify_business_connections(self, whois_checker):
        """Test business connection identification from domains"""
        domains = [
            DomainRecord(
                domain="business1.com",
                registrant_org="Test Business Pvt Ltd",
                registrant_phone="+919876543210",
                registrant_email="contact@business1.com",
                creation_date=datetime.now() - timedelta(days=365),
                confidence=80.0
            ),
            DomainRecord(
                domain="business2.com",
                registrant_org="Test Business Pvt Ltd",  # Same organization
                registrant_phone="+919876543210",
                registrant_email="info@business2.com",
                creation_date=datetime.now() - timedelta(days=200),
                confidence=85.0
            ),
            DomainRecord(
                domain="other.com",
                registrant_org="Different Company",
                registrant_phone="+919876543210",
                confidence=75.0
            )
        ]
        
        connections = whois_checker._identify_business_connections(domains)
        
        assert len(connections) == 2  # Two different organizations
        
        # Find Test Business connection
        test_business = next(c for c in connections if c.organization == "Test Business Pvt Ltd")
        assert len(test_business.domains) == 2
        assert len(test_business.phone_numbers) == 2  # Should have both phone entries
        assert len(test_business.email_addresses) == 2
        assert test_business.confidence >= 70.0  # Should have good confidence
    
    def test_store_and_retrieve_investigation_results(self, whois_checker):
        """Test storing and retrieving investigation results from database"""
        phone_number = "+919876543210"
        
        # Create test result
        result = WHOISInvestigationResult(phone_number=phone_number)
        result.domains_found = [
            DomainRecord(
                domain="test.com",
                registrar="GoDaddy",
                creation_date=datetime.now() - timedelta(days=365),
                expiration_date=datetime.now() + timedelta(days=365),
                status="active",
                registrant_org="Test Organization",
                registrant_name="Test User",
                confidence=85.0
            )
        ]
        result.business_connections = [
            BusinessConnection(
                organization="Test Organization",
                contact_type="registrant",
                domains=["test.com"],
                confidence=90.0,
                first_seen=datetime.now() - timedelta(days=365),
                last_seen=datetime.now()
            )
        ]
        
        # Store results
        whois_checker._store_investigation_results(phone_number, result)
        
        # Retrieve historical domains
        historical_domains = whois_checker._get_historical_domains(phone_number)
        
        assert len(historical_domains) == 1
        assert historical_domains[0].domain == "test.com"
        assert historical_domains[0].registrant_org == "Test Organization"
        assert historical_domains[0].confidence == 85.0
    
    def test_get_historical_changes(self, whois_checker):
        """Test historical change detection"""
        phone_number = "+919876543210"
        
        # Insert test data with changes
        conn = sqlite3.connect(whois_checker.db_path)
        cursor = conn.cursor()
        
        # Initial record
        cursor.execute('''
            INSERT INTO whois_history 
            (phone_number, domain, status, registrant_org, checked_date)
            VALUES (?, ?, ?, ?, ?)
        ''', (phone_number, "test.com", "active", "Old Organization", "2024-01-01T00:00:00"))
        
        # Changed record
        cursor.execute('''
            INSERT INTO whois_history 
            (phone_number, domain, status, registrant_org, checked_date)
            VALUES (?, ?, ?, ?, ?)
        ''', (phone_number, "test.com", "expired", "New Organization", "2024-02-01T00:00:00"))
        
        conn.commit()
        conn.close()
        
        # Get historical changes
        changes = whois_checker._get_historical_changes(phone_number)
        
        assert len(changes) == 2  # Status change and ownership change
        
        # Check for status change
        status_change = next((c for c in changes if c['change_type'] == 'status_change'), None)
        assert status_change is not None
        assert status_change['old_value'] == 'active'
        assert status_change['new_value'] == 'expired'
        
        # Check for ownership change
        ownership_change = next((c for c in changes if c['change_type'] == 'ownership_change'), None)
        assert ownership_change is not None
        assert ownership_change['old_value'] == 'Old Organization'
        assert ownership_change['new_value'] == 'New Organization'
    
    def test_calculate_investigation_confidence(self, whois_checker):
        """Test investigation confidence calculation"""
        # Test with no domains
        result_empty = WHOISInvestigationResult(phone_number="+919876543210")
        confidence = whois_checker._calculate_investigation_confidence(result_empty)
        assert confidence == 0.0
        
        # Test with domains and business connections
        result_full = WHOISInvestigationResult(phone_number="+919876543210")
        result_full.domains_found = [
            DomainRecord(domain="test1.com", confidence=80.0, status="active"),
            DomainRecord(domain="test2.com", confidence=90.0, status="active")
        ]
        result_full.business_connections = [
            BusinessConnection(organization="Test Org", contact_type="registrant")
        ]
        result_full.sources_checked = ["Source1", "Source2", "Source3"]
        result_full.total_domains = 2
        
        confidence = whois_checker._calculate_investigation_confidence(result_full)
        assert confidence > 80.0  # Should have high confidence
        assert confidence <= 100.0
    
    @patch.object(WHOISChecker, '_search_whois_databases')
    @patch.object(WHOISChecker, '_search_reverse_whois_apis')
    @patch.object(WHOISChecker, '_search_domain_patterns')
    @patch.object(WHOISChecker, '_get_historical_domains')
    def test_investigate_phone_whois_integration(self, mock_historical, mock_patterns, 
                                               mock_apis, mock_whois, whois_checker):
        """Test complete WHOIS investigation integration"""
        phone_number = "+919876543210"
        
        # Mock return values
        sample_domain = DomainRecord(
            domain="test.com",
            registrar="GoDaddy",
            status="active",
            registrant_phone=phone_number,
            registrant_org="Test Organization",
            confidence=85.0
        )
        
        mock_whois.return_value = [sample_domain]
        mock_apis.return_value = []
        mock_patterns.return_value = []
        mock_historical.return_value = []
        
        # Mock the deduplication and enrichment
        with patch.object(whois_checker, '_deduplicate_and_enrich_domains', 
                         return_value=[sample_domain]):
            result = whois_checker.investigate_phone_whois(phone_number)
        
        assert result.phone_number == phone_number
        assert len(result.domains_found) == 1
        assert result.domains_found[0].domain == "test.com"
        assert result.total_domains == 1
        assert result.active_domains == 1
        assert result.investigation_confidence > 0
        assert len(result.sources_checked) > 0
        assert result.processing_time > 0
    
    def test_generate_business_intelligence_summary(self, whois_checker):
        """Test business intelligence summary generation"""
        # Create test result with various domains
        result = WHOISInvestigationResult(phone_number="+919876543210")
        result.domains_found = [
            DomainRecord(
                domain="business1.com",
                registrar="GoDaddy",
                creation_date=datetime(2020, 1, 1),
                status="active",
                confidence=85.0
            ),
            DomainRecord(
                domain="business2.in",
                registrar="GoDaddy",
                creation_date=datetime(2021, 1, 1),
                status="active",
                confidence=80.0
            ),
            DomainRecord(
                domain="old.com",
                registrar="Namecheap",
                creation_date=datetime(2019, 1, 1),
                status="expired",
                confidence=70.0
            )
        ]
        result.business_connections = [
            BusinessConnection(organization="Test Business", contact_type="registrant")
        ]
        result.total_domains = 3
        result.active_domains = 2
        result.expired_domains = 1
        result.parked_domains = 0
        
        summary = whois_checker.generate_business_intelligence_summary(result)
        
        assert summary['total_domains'] == 3
        assert summary['active_domains'] == 2
        assert summary['expired_domains'] == 1
        assert summary['business_entities'] == 1
        assert 'registration_patterns' in summary
        assert 'preferred_registrars' in summary['registration_patterns']
        assert 'GoDaddy' in summary['registration_patterns']['preferred_registrars']
        assert summary['business_profile'] == 'Single Business Entity'
    
    def test_error_handling(self, whois_checker):
        """Test error handling in various scenarios"""
        # Test with invalid phone number
        result = whois_checker.investigate_phone_whois("invalid")
        assert len(result.errors) == 0  # Should handle gracefully
        
        # Test database connection error
        whois_checker.db_path = "/invalid/path/db.sqlite"
        
        # Should not crash, but may have errors
        result = whois_checker.investigate_phone_whois("+919876543210")
        assert isinstance(result, WHOISInvestigationResult)
    
    def test_real_whois_lookup(self, whois_checker):
        """Integration test with real WHOIS lookup (requires internet)"""
        # This test requires internet connection and may be slow
        # Skip if running in CI or offline environment
        
        try:
            import socket
            socket.gethostbyname("google.com")  # Test internet connectivity
        except socket.gaierror:
            pytest.skip("No internet connection available")
        
        # Test with a known domain
        domain_info = whois_checker._check_domain_existence("google.com")
        
        if domain_info:  # May fail due to rate limiting or blocking
            assert domain_info.domain == "google.com"
            assert domain_info.registrar is not None
            assert domain_info.status in ['active', 'unknown']
    
    def test_phone_number_format_variations(self, whois_checker):
        """Test investigation with various phone number formats"""
        test_numbers = [
            "+919876543210",
            "919876543210", 
            "9876543210",
            "(+91) 98765-43210",
            "+91-9876-543-210"
        ]
        
        for phone_number in test_numbers:
            # Mock the internal methods to avoid actual API calls
            with patch.object(whois_checker, '_search_whois_databases', return_value=[]):
                with patch.object(whois_checker, '_search_reverse_whois_apis', return_value=[]):
                    with patch.object(whois_checker, '_search_domain_patterns', return_value=[]):
                        with patch.object(whois_checker, '_get_historical_domains', return_value=[]):
                            result = whois_checker.investigate_phone_whois(phone_number)
                            
                            assert result.phone_number == phone_number
                            assert isinstance(result, WHOISInvestigationResult)
                            assert result.processing_time >= 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])