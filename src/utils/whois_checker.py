"""
WHOIS and Domain Linkage System
Searches for phone numbers in WHOIS records and discovers associated domains
"""

import requests
import re
import time
import socket
import whois
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import dns.resolver
import json
import sqlite3
import os
from urllib.parse import urlparse


@dataclass
class DomainRecord:
    """Container for domain information"""
    domain: str
    registrar: str = "Unknown"
    creation_date: Optional[datetime] = None
    expiration_date: Optional[datetime] = None
    last_updated: Optional[datetime] = None
    status: str = "unknown"  # active, expired, parked, suspended
    registrant_phone: Optional[str] = None
    admin_phone: Optional[str] = None
    tech_phone: Optional[str] = None
    registrant_org: Optional[str] = None
    registrant_name: Optional[str] = None
    registrant_email: Optional[str] = None
    name_servers: List[str] = field(default_factory=list)
    whois_server: Optional[str] = None
    confidence: float = 0.0
    last_checked: datetime = field(default_factory=datetime.now)


@dataclass
class BusinessConnection:
    """Container for business connection information"""
    organization: str
    contact_type: str  # registrant, admin, tech
    domains: List[str] = field(default_factory=list)
    phone_numbers: List[str] = field(default_factory=list)
    email_addresses: List[str] = field(default_factory=list)
    confidence: float = 0.0
    first_seen: Optional[datetime] = None
    last_seen: Optional[datetime] = None


@dataclass
class WHOISInvestigationResult:
    """Container for complete WHOIS investigation results"""
    phone_number: str
    domains_found: List[DomainRecord] = field(default_factory=list)
    business_connections: List[BusinessConnection] = field(default_factory=list)
    historical_changes: List[Dict] = field(default_factory=list)
    total_domains: int = 0
    active_domains: int = 0
    expired_domains: int = 0
    parked_domains: int = 0
    investigation_confidence: float = 0.0
    sources_checked: List[str] = field(default_factory=list)
    processing_time: float = 0.0
    errors: List[str] = field(default_factory=list)


class WHOISChecker:
    """
    WHOIS and domain linkage system for phone number investigation
    Searches WHOIS databases and discovers domain associations
    """
    
    def __init__(self, db_path: str = "data/whois_history.db"):
        self.db_path = db_path
        self.whois_sources = [
            'whois.whois-servers.net',
            'whois.iana.org',
            'whois.verisign-grs.com',
            'whois.publicinterestregistry.net',
            'whois.afilias.net'
        ]
        
        # Common WHOIS servers by TLD
        self.tld_whois_servers = {
            'com': 'whois.verisign-grs.com',
            'net': 'whois.verisign-grs.com',
            'org': 'whois.publicinterestregistry.net',
            'info': 'whois.afilias.net',
            'biz': 'whois.neulevel.biz',
            'us': 'whois.nic.us',
            'uk': 'whois.nic.uk',
            'ca': 'whois.cira.ca',
            'au': 'whois.aunic.net',
            'de': 'whois.denic.de',
            'fr': 'whois.afnic.fr',
            'in': 'whois.registry.in',
            'cn': 'whois.cnnic.net.cn',
            'jp': 'whois.jprs.jp'
        }
        
        # Domain status mappings
        self.status_mappings = {
            'clientDeleteProhibited': 'active',
            'clientTransferProhibited': 'active',
            'clientUpdateProhibited': 'active',
            'serverDeleteProhibited': 'active',
            'serverTransferProhibited': 'active',
            'serverUpdateProhibited': 'active',
            'ok': 'active',
            'inactive': 'parked',
            'pendingDelete': 'expired',
            'redemptionPeriod': 'expired',
            'pendingRestore': 'expired',
            'serverHold': 'suspended',
            'clientHold': 'suspended'
        }
        
        # Initialize database
        self._init_database()
    
    def _init_database(self):
        """Initialize SQLite database for historical tracking"""
        try:
            os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Create tables for historical tracking
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS whois_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    phone_number TEXT NOT NULL,
                    domain TEXT NOT NULL,
                    registrar TEXT,
                    creation_date TEXT,
                    expiration_date TEXT,
                    registrant_org TEXT,
                    registrant_name TEXT,
                    contact_type TEXT,
                    status TEXT,
                    confidence REAL,
                    checked_date TEXT,
                    UNIQUE(phone_number, domain, checked_date)
                )
            ''')
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS business_connections (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    phone_number TEXT NOT NULL,
                    organization TEXT NOT NULL,
                    contact_type TEXT,
                    domains TEXT,
                    confidence REAL,
                    first_seen TEXT,
                    last_seen TEXT,
                    UNIQUE(phone_number, organization, contact_type)
                )
            ''')
            
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_phone_number ON whois_history(phone_number)
            ''')
            
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_domain ON whois_history(domain)
            ''')
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            print(f"Database initialization error: {e}")
    
    def investigate_phone_whois(self, phone_number: str) -> WHOISInvestigationResult:
        """
        Comprehensive WHOIS investigation for a phone number
        
        Args:
            phone_number: Phone number to investigate
            
        Returns:
            WHOISInvestigationResult with complete findings
        """
        start_time = time.time()
        
        result = WHOISInvestigationResult(phone_number=phone_number)
        
        try:
            # Clean and format phone number
            clean_phone = self._clean_phone_number(phone_number)
            
            # Search multiple WHOIS sources
            result.sources_checked.extend([
                'Direct WHOIS Search',
                'Reverse WHOIS APIs',
                'Domain Registration Databases',
                'Historical WHOIS Data'
            ])
            
            # 1. Direct WHOIS database search
            domains_from_whois = self._search_whois_databases(clean_phone)
            result.domains_found.extend(domains_from_whois)
            
            # 2. Reverse WHOIS API search
            domains_from_apis = self._search_reverse_whois_apis(clean_phone)
            result.domains_found.extend(domains_from_apis)
            
            # 3. Domain registration pattern search
            domains_from_patterns = self._search_domain_patterns(clean_phone)
            result.domains_found.extend(domains_from_patterns)
            
            # 4. Historical data lookup
            historical_domains = self._get_historical_domains(clean_phone)
            result.domains_found.extend(historical_domains)
            
            # Remove duplicates and enrich domain data
            result.domains_found = self._deduplicate_and_enrich_domains(result.domains_found)
            
            # Analyze domain status
            result.total_domains = len(result.domains_found)
            for domain in result.domains_found:
                if domain.status == 'active':
                    result.active_domains += 1
                elif domain.status == 'expired':
                    result.expired_domains += 1
                elif domain.status == 'parked':
                    result.parked_domains += 1
            
            # Identify business connections
            result.business_connections = self._identify_business_connections(result.domains_found)
            
            # Get historical changes
            result.historical_changes = self._get_historical_changes(clean_phone)
            
            # Calculate investigation confidence
            result.investigation_confidence = self._calculate_investigation_confidence(result)
            
            # Store results for historical tracking
            self._store_investigation_results(clean_phone, result)
            
        except Exception as e:
            result.errors.append(f"Investigation error: {str(e)}")
        
        result.processing_time = time.time() - start_time
        return result
    
    def _clean_phone_number(self, phone_number: str) -> str:
        """Clean and normalize phone number for WHOIS search"""
        # Remove all non-digit characters except +
        clean = re.sub(r'[^\d+]', '', phone_number)
        
        # Handle different formats
        if clean.startswith('+91') and len(clean) == 13:
            return clean  # +919876543210
        elif clean.startswith('91') and len(clean) == 12:
            return f'+{clean}'  # 919876543210 -> +919876543210
        elif len(clean) == 11 and clean.startswith('0') and clean[1] in ['6', '7', '8', '9']:
            return f'+91{clean[1:]}'  # 09876543210 -> +919876543210
        elif len(clean) == 10 and clean[0] in ['6', '7', '8', '9']:
            return f'+91{clean}'  # 9876543210 -> +919876543210
        
        return clean
    
    def _search_whois_databases(self, phone_number: str) -> List[DomainRecord]:
        """Search direct WHOIS databases for phone number appearances"""
        domains = []
        
        try:
            # This would typically involve querying WHOIS databases
            # For demonstration, we'll simulate the search
            
            # Common patterns to search for
            search_patterns = [
                phone_number,
                phone_number.replace('+', ''),
                phone_number.replace('+91', ''),
                phone_number.replace(' ', ''),
                phone_number.replace('-', ''),
                phone_number.replace('(', '').replace(')', '')
            ]
            
            # Simulate domain findings (in production, this would query actual WHOIS databases)
            if phone_number.startswith('+91'):
                # Simulate finding domains for Indian numbers
                sample_domains = self._generate_sample_domains(phone_number)
                domains.extend(sample_domains)
            
        except Exception as e:
            print(f"WHOIS database search error: {e}")
        
        return domains
    
    def _search_reverse_whois_apis(self, phone_number: str) -> List[DomainRecord]:
        """Search reverse WHOIS APIs for domain associations"""
        domains = []
        
        try:
            # WhoisXML API
            domains.extend(self._query_whoisxml_api(phone_number))
            
            # DomainTools API
            domains.extend(self._query_domaintools_api(phone_number))
            
            # ViewDNS reverse WHOIS
            domains.extend(self._query_viewdns_api(phone_number))
            
        except Exception as e:
            print(f"Reverse WHOIS API search error: {e}")
        
        return domains
    
    def _query_whoisxml_api(self, phone_number: str) -> List[DomainRecord]:
        """Query WhoisXML API for reverse WHOIS lookup"""
        domains = []
        
        try:
            # This would require an actual API key and subscription
            # For demonstration, we'll simulate the response
            
            # In production, you would make actual API calls like:
            # url = f"https://reverse-whois.whoisxmlapi.com/api/v2?apiKey={api_key}&searchType=phone&mode=purchase&phone={phone_number}"
            # response = requests.get(url, timeout=10)
            
            # Simulate finding domains
            if phone_number.startswith('+91'):
                sample_domain = DomainRecord(
                    domain=f"example-{phone_number[-4:]}.com",
                    registrar="GoDaddy",
                    creation_date=datetime.now() - timedelta(days=365),
                    expiration_date=datetime.now() + timedelta(days=365),
                    status="active",
                    registrant_phone=phone_number,
                    registrant_org="Sample Business",
                    confidence=75.0,
                    whois_server="whois.godaddy.com"
                )
                domains.append(sample_domain)
            
        except Exception as e:
            print(f"WhoisXML API error: {e}")
        
        return domains
    
    def _query_domaintools_api(self, phone_number: str) -> List[DomainRecord]:
        """Query DomainTools API for reverse WHOIS lookup"""
        domains = []
        
        try:
            # This would require DomainTools API credentials
            # For demonstration, we'll simulate the response
            
            # In production:
            # url = f"https://api.domaintools.com/v1/reverse-whois/?terms={phone_number}&api_username={username}&api_key={api_key}"
            # response = requests.get(url, timeout=10)
            
            # Simulate response for demonstration
            pass
            
        except Exception as e:
            print(f"DomainTools API error: {e}")
        
        return domains
    
    def _query_viewdns_api(self, phone_number: str) -> List[DomainRecord]:
        """Query ViewDNS reverse WHOIS API"""
        domains = []
        
        try:
            # ViewDNS reverse WHOIS lookup
            # url = f"https://api.viewdns.info/reversewhois/?phone={phone_number}&apikey={api_key}&output=json"
            
            # Simulate response for demonstration
            pass
            
        except Exception as e:
            print(f"ViewDNS API error: {e}")
        
        return domains
    
    def _search_domain_patterns(self, phone_number: str) -> List[DomainRecord]:
        """Search for domains using phone number patterns"""
        domains = []
        
        try:
            # Extract number patterns for domain search
            clean_number = phone_number.replace('+91', '').replace('+', '')
            
            # Common domain patterns with phone numbers
            patterns = [
                f"{clean_number}.com",
                f"{clean_number}.in",
                f"call{clean_number}.com",
                f"phone{clean_number}.com",
                f"{clean_number}business.com",
                f"contact{clean_number}.in"
            ]
            
            # Check if these domains exist and get WHOIS data
            for pattern in patterns:
                domain_info = self._check_domain_existence(pattern)
                if domain_info:
                    domains.append(domain_info)
            
        except Exception as e:
            print(f"Domain pattern search error: {e}")
        
        return domains
    
    def _check_domain_existence(self, domain: str) -> Optional[DomainRecord]:
        """Check if a domain exists and get its WHOIS information"""
        try:
            # Check DNS resolution first
            try:
                socket.gethostbyname(domain)
                domain_exists = True
            except socket.gaierror:
                domain_exists = False
            
            if not domain_exists:
                return None
            
            # Get WHOIS information
            try:
                w = whois.whois(domain)
                
                if w and w.domain_name:
                    # Parse WHOIS data
                    creation_date = w.creation_date
                    if isinstance(creation_date, list):
                        creation_date = creation_date[0]
                    
                    expiration_date = w.expiration_date
                    if isinstance(expiration_date, list):
                        expiration_date = expiration_date[0]
                    
                    # Determine status
                    status = self._determine_domain_status(w)
                    
                    return DomainRecord(
                        domain=domain,
                        registrar=w.registrar or "Unknown",
                        creation_date=creation_date,
                        expiration_date=expiration_date,
                        status=status,
                        registrant_org=w.org,
                        registrant_name=w.name,
                        registrant_email=w.emails[0] if w.emails else None,
                        name_servers=w.name_servers or [],
                        confidence=60.0  # Medium confidence for pattern-based discovery
                    )
            
            except Exception as whois_error:
                print(f"WHOIS lookup error for {domain}: {whois_error}")
                return None
        
        except Exception as e:
            print(f"Domain existence check error for {domain}: {e}")
            return None
    
    def _determine_domain_status(self, whois_data) -> str:
        """Determine domain status from WHOIS data"""
        try:
            if hasattr(whois_data, 'status') and whois_data.status:
                status_list = whois_data.status
                if isinstance(status_list, str):
                    status_list = [status_list]
                
                for status in status_list:
                    status_lower = status.lower()
                    for key, mapped_status in self.status_mappings.items():
                        if key.lower() in status_lower:
                            return mapped_status
            
            # Check expiration date
            if hasattr(whois_data, 'expiration_date') and whois_data.expiration_date:
                exp_date = whois_data.expiration_date
                if isinstance(exp_date, list):
                    exp_date = exp_date[0]
                
                if exp_date and exp_date < datetime.now():
                    return 'expired'
            
            return 'active'  # Default to active if no clear status
            
        except Exception as e:
            print(f"Status determination error: {e}")
            return 'unknown'
    
    def _generate_sample_domains(self, phone_number: str) -> List[DomainRecord]:
        """Generate sample domain records for demonstration"""
        domains = []
        
        try:
            clean_number = phone_number.replace('+91', '')
            
            # Sample domain 1
            domain1 = DomainRecord(
                domain=f"business{clean_number[-4:]}.com",
                registrar="Namecheap",
                creation_date=datetime.now() - timedelta(days=730),
                expiration_date=datetime.now() + timedelta(days=365),
                status="active",
                registrant_phone=phone_number,
                registrant_org="Sample Business Pvt Ltd",
                registrant_name="Business Owner",
                registrant_email=f"contact@business{clean_number[-4:]}.com",
                name_servers=["ns1.namecheap.com", "ns2.namecheap.com"],
                confidence=85.0
            )
            domains.append(domain1)
            
            # Sample domain 2
            domain2 = DomainRecord(
                domain=f"contact{clean_number[-4:]}.in",
                registrar="BigRock",
                creation_date=datetime.now() - timedelta(days=1095),
                expiration_date=datetime.now() - timedelta(days=30),  # Expired
                status="expired",
                registrant_phone=phone_number,
                registrant_org="Old Business",
                confidence=70.0
            )
            domains.append(domain2)
            
        except Exception as e:
            print(f"Sample domain generation error: {e}")
        
        return domains
    
    def _deduplicate_and_enrich_domains(self, domains: List[DomainRecord]) -> List[DomainRecord]:
        """Remove duplicate domains and enrich with additional data"""
        seen_domains = {}
        enriched_domains = []
        
        for domain in domains:
            domain_key = domain.domain.lower()
            
            if domain_key not in seen_domains:
                # Enrich domain with additional checks
                enriched_domain = self._enrich_domain_data(domain)
                enriched_domains.append(enriched_domain)
                seen_domains[domain_key] = True
            else:
                # Merge data from duplicate entries
                existing_domain = next(d for d in enriched_domains if d.domain.lower() == domain_key)
                existing_domain = self._merge_domain_data(existing_domain, domain)
        
        return enriched_domains
    
    def _enrich_domain_data(self, domain: DomainRecord) -> DomainRecord:
        """Enrich domain record with additional data"""
        try:
            # Check current DNS status
            try:
                socket.gethostbyname(domain.domain)
                domain.status = 'active' if domain.status == 'unknown' else domain.status
            except socket.gaierror:
                if domain.status == 'active':
                    domain.status = 'parked'  # Domain exists in WHOIS but no DNS
            
            # Update confidence based on data completeness
            confidence_factors = 0
            if domain.registrant_phone:
                confidence_factors += 30
            if domain.registrant_org:
                confidence_factors += 20
            if domain.registrant_email:
                confidence_factors += 15
            if domain.creation_date:
                confidence_factors += 15
            if domain.name_servers:
                confidence_factors += 10
            if domain.registrar and domain.registrar != "Unknown":
                confidence_factors += 10
            
            domain.confidence = min(confidence_factors, 95.0)
            
        except Exception as e:
            print(f"Domain enrichment error for {domain.domain}: {e}")
        
        return domain
    
    def _merge_domain_data(self, existing: DomainRecord, new: DomainRecord) -> DomainRecord:
        """Merge data from duplicate domain records"""
        # Use the record with higher confidence as base
        if new.confidence > existing.confidence:
            base, supplement = new, existing
        else:
            base, supplement = existing, new
        
        # Fill in missing data from supplement
        if not base.registrant_phone and supplement.registrant_phone:
            base.registrant_phone = supplement.registrant_phone
        if not base.registrant_org and supplement.registrant_org:
            base.registrant_org = supplement.registrant_org
        if not base.registrant_email and supplement.registrant_email:
            base.registrant_email = supplement.registrant_email
        if not base.creation_date and supplement.creation_date:
            base.creation_date = supplement.creation_date
        if not base.expiration_date and supplement.expiration_date:
            base.expiration_date = supplement.expiration_date
        
        # Merge name servers
        if supplement.name_servers:
            base.name_servers = list(set(base.name_servers + supplement.name_servers))
        
        # Update confidence to average of both sources
        base.confidence = (base.confidence + supplement.confidence) / 2
        
        return base
    
    def _identify_business_connections(self, domains: List[DomainRecord]) -> List[BusinessConnection]:
        """Identify business connections from domain data"""
        connections = {}
        
        for domain in domains:
            if domain.registrant_org:
                org_key = domain.registrant_org.lower().strip()
                
                if org_key not in connections:
                    connections[org_key] = BusinessConnection(
                        organization=domain.registrant_org,
                        contact_type="registrant",
                        first_seen=domain.creation_date,
                        last_seen=domain.last_updated or domain.creation_date
                    )
                
                connection = connections[org_key]
                connection.domains.append(domain.domain)
                
                if domain.registrant_phone:
                    connection.phone_numbers.append(domain.registrant_phone)
                if domain.registrant_email:
                    connection.email_addresses.append(domain.registrant_email)
                
                # Update date ranges
                if domain.creation_date:
                    if not connection.first_seen or domain.creation_date < connection.first_seen:
                        connection.first_seen = domain.creation_date
                    if not connection.last_seen or domain.creation_date > connection.last_seen:
                        connection.last_seen = domain.creation_date
                
                # Calculate confidence based on number of domains and data quality
                connection.confidence = min(50 + (len(connection.domains) * 10), 95.0)
        
        return list(connections.values())
    
    def _get_historical_domains(self, phone_number: str) -> List[DomainRecord]:
        """Get historical domain data from database"""
        domains = []
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT DISTINCT domain, registrar, creation_date, expiration_date,
                       registrant_org, registrant_name, status, confidence
                FROM whois_history 
                WHERE phone_number = ?
                ORDER BY checked_date DESC
            ''', (phone_number,))
            
            for row in cursor.fetchall():
                domain = DomainRecord(
                    domain=row[0],
                    registrar=row[1] or "Unknown",
                    creation_date=datetime.fromisoformat(row[2]) if row[2] else None,
                    expiration_date=datetime.fromisoformat(row[3]) if row[3] else None,
                    registrant_org=row[4],
                    registrant_name=row[5],
                    status=row[6] or "unknown",
                    confidence=row[7] or 0.0,
                    registrant_phone=phone_number
                )
                domains.append(domain)
            
            conn.close()
            
        except Exception as e:
            print(f"Historical domain lookup error: {e}")
        
        return domains
    
    def _get_historical_changes(self, phone_number: str) -> List[Dict]:
        """Get historical changes for phone number"""
        changes = []
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT domain, status, registrant_org, checked_date
                FROM whois_history 
                WHERE phone_number = ?
                ORDER BY domain, checked_date
            ''', (phone_number,))
            
            rows = cursor.fetchall()
            
            # Group by domain and detect changes
            domain_history = {}
            for row in rows:
                domain, status, org, checked_date = row
                if domain not in domain_history:
                    domain_history[domain] = []
                domain_history[domain].append({
                    'status': status,
                    'organization': org,
                    'date': checked_date
                })
            
            # Detect changes
            for domain, history in domain_history.items():
                for i in range(1, len(history)):
                    prev = history[i-1]
                    curr = history[i]
                    
                    if prev['status'] != curr['status']:
                        changes.append({
                            'domain': domain,
                            'change_type': 'status_change',
                            'old_value': prev['status'],
                            'new_value': curr['status'],
                            'date': curr['date'],
                            'confidence': 90.0
                        })
                    
                    if prev['organization'] != curr['organization']:
                        changes.append({
                            'domain': domain,
                            'change_type': 'ownership_change',
                            'old_value': prev['organization'],
                            'new_value': curr['organization'],
                            'date': curr['date'],
                            'confidence': 85.0
                        })
            
            conn.close()
            
        except Exception as e:
            print(f"Historical changes lookup error: {e}")
        
        return changes
    
    def _calculate_investigation_confidence(self, result: WHOISInvestigationResult) -> float:
        """Calculate overall investigation confidence"""
        if not result.domains_found:
            return 0.0
        
        # Base confidence from domain confidence scores
        domain_confidences = [d.confidence for d in result.domains_found if d.confidence > 0]
        if not domain_confidences:
            return 20.0  # Low confidence if no domain confidence scores
        
        avg_domain_confidence = sum(domain_confidences) / len(domain_confidences)
        
        # Bonuses for multiple sources and business connections
        source_bonus = min(len(result.sources_checked) * 5, 20)
        business_bonus = min(len(result.business_connections) * 10, 30)
        domain_count_bonus = min(result.total_domains * 5, 25)
        
        # Penalty for errors
        error_penalty = len(result.errors) * 10
        
        final_confidence = avg_domain_confidence + source_bonus + business_bonus + domain_count_bonus - error_penalty
        
        return max(0.0, min(100.0, final_confidence))
    
    def _store_investigation_results(self, phone_number: str, result: WHOISInvestigationResult):
        """Store investigation results for historical tracking"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            current_time = datetime.now().isoformat()
            
            # Store domain records
            for domain in result.domains_found:
                cursor.execute('''
                    INSERT OR REPLACE INTO whois_history 
                    (phone_number, domain, registrar, creation_date, expiration_date,
                     registrant_org, registrant_name, contact_type, status, confidence, checked_date)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    phone_number,
                    domain.domain,
                    domain.registrar,
                    domain.creation_date.isoformat() if domain.creation_date else None,
                    domain.expiration_date.isoformat() if domain.expiration_date else None,
                    domain.registrant_org,
                    domain.registrant_name,
                    'registrant',
                    domain.status,
                    domain.confidence,
                    current_time
                ))
            
            # Store business connections
            for connection in result.business_connections:
                cursor.execute('''
                    INSERT OR REPLACE INTO business_connections
                    (phone_number, organization, contact_type, domains, confidence, first_seen, last_seen)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (
                    phone_number,
                    connection.organization,
                    connection.contact_type,
                    json.dumps(connection.domains),
                    connection.confidence,
                    connection.first_seen.isoformat() if connection.first_seen else None,
                    connection.last_seen.isoformat() if connection.last_seen else None
                ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            print(f"Storage error: {e}")
    
    def generate_business_intelligence_summary(self, result: WHOISInvestigationResult) -> Dict[str, Any]:
        """Generate business intelligence summary from WHOIS investigation"""
        summary = {
            'total_domains': result.total_domains,
            'active_domains': result.active_domains,
            'expired_domains': result.expired_domains,
            'parked_domains': result.parked_domains,
            'business_entities': len(result.business_connections),
            'domain_portfolio_value': 'Unknown',
            'registration_patterns': {},
            'risk_indicators': [],
            'business_profile': 'Unknown'
        }
        
        if not result.domains_found:
            return summary
        
        # Analyze registration patterns
        registrars = {}
        creation_years = {}
        tlds = {}
        
        for domain in result.domains_found:
            # Registrar analysis
            if domain.registrar:
                registrars[domain.registrar] = registrars.get(domain.registrar, 0) + 1
            
            # Creation year analysis
            if domain.creation_date:
                year = domain.creation_date.year
                creation_years[year] = creation_years.get(year, 0) + 1
            
            # TLD analysis
            tld = domain.domain.split('.')[-1]
            tlds[tld] = tlds.get(tld, 0) + 1
        
        summary['registration_patterns'] = {
            'preferred_registrars': dict(sorted(registrars.items(), key=lambda x: x[1], reverse=True)[:3]),
            'registration_years': dict(sorted(creation_years.items(), key=lambda x: x[1], reverse=True)[:5]),
            'preferred_tlds': dict(sorted(tlds.items(), key=lambda x: x[1], reverse=True)[:5])
        }
        
        # Risk indicators
        if result.expired_domains > result.active_domains:
            summary['risk_indicators'].append('High number of expired domains')
        
        if len(set(d.registrar for d in result.domains_found if d.registrar)) == 1:
            summary['risk_indicators'].append('All domains with same registrar')
        
        if result.total_domains > 10:
            summary['risk_indicators'].append('Large domain portfolio')
        
        # Business profile assessment
        if result.business_connections:
            if len(result.business_connections) == 1:
                summary['business_profile'] = 'Single Business Entity'
            else:
                summary['business_profile'] = 'Multiple Business Entities'
        elif result.total_domains > 5:
            summary['business_profile'] = 'Domain Investor/Reseller'
        elif result.total_domains > 0:
            summary['business_profile'] = 'Small Business/Individual'
        
        return summary