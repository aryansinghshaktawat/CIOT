"""
Historical Data Manager for Phone Investigation
Tracks and analyzes historical changes in phone number data
"""

import sqlite3
import json
import hashlib
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
from pathlib import Path
import logging

@dataclass
class PhoneInvestigationRecord:
    """Data class for phone investigation records"""
    phone_number: str
    investigation_timestamp: datetime
    country_code: str
    carrier_name: str
    location: str
    number_type: str
    is_valid: bool
    is_mobile: bool
    reputation_score: float
    social_media_presence: Dict
    whois_domains: List[str]
    api_sources: List[str]
    confidence_score: float
    raw_data: Dict

@dataclass
class HistoricalChange:
    """Data class for detected changes"""
    phone_number: str
    change_type: str
    field_name: str
    old_value: str
    new_value: str
    change_timestamp: datetime
    confidence_score: float
    verification_status: str
    change_source: str

class HistoricalDataManager:
    """
    Manages historical phone investigation data with SQLite storage
    Provides change detection, porting analysis, and trend tracking
    """
    
    def __init__(self, db_path: str = "data/phone_history.db"):
        """
        Initialize HistoricalDataManager
        
        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.logger = logging.getLogger(__name__)
        
        # Initialize database
        self._init_database()
    
    def _init_database(self) -> None:
        """Initialize SQLite database with required tables"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Phone investigation records table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS phone_investigations (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        phone_number TEXT NOT NULL,
                        phone_hash TEXT NOT NULL,
                        investigation_timestamp TIMESTAMP NOT NULL,
                        country_code TEXT,
                        carrier_name TEXT,
                        location TEXT,
                        number_type TEXT,
                        is_valid BOOLEAN,
                        is_mobile BOOLEAN,
                        reputation_score REAL,
                        social_media_presence TEXT,
                        whois_domains TEXT,
                        api_sources TEXT,
                        confidence_score REAL,
                        raw_data TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
                
                # Historical changes table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS historical_changes (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        phone_number TEXT NOT NULL,
                        phone_hash TEXT NOT NULL,
                        change_type TEXT NOT NULL,
                        field_name TEXT NOT NULL,
                        old_value TEXT,
                        new_value TEXT,
                        change_timestamp TIMESTAMP NOT NULL,
                        confidence_score REAL,
                        verification_status TEXT,
                        change_source TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
                
                # Carrier transitions table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS carrier_transitions (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        phone_number TEXT NOT NULL,
                        phone_hash TEXT NOT NULL,
                        from_carrier TEXT,
                        to_carrier TEXT,
                        transition_timestamp TIMESTAMP NOT NULL,
                        transition_type TEXT,
                        confidence_score REAL,
                        porting_detected BOOLEAN,
                        verification_status TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
                
                # Investigation metadata table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS investigation_metadata (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        phone_number TEXT NOT NULL,
                        phone_hash TEXT NOT NULL,
                        first_seen TIMESTAMP,
                        last_seen TIMESTAMP,
                        total_investigations INTEGER DEFAULT 1,
                        change_frequency REAL,
                        stability_score REAL,
                        risk_indicators TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
                
                # Create indexes for performance
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_phone_hash ON phone_investigations(phone_hash)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_phone_timestamp ON phone_investigations(phone_number, investigation_timestamp)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_changes_phone ON historical_changes(phone_hash)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_transitions_phone ON carrier_transitions(phone_hash)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_metadata_phone ON investigation_metadata(phone_hash)')
                
                conn.commit()
                self.logger.info("Historical data database initialized successfully")
                
        except Exception as e:
            self.logger.error(f"Database initialization error: {str(e)}")
            raise
    
    def _hash_phone_number(self, phone_number: str) -> str:
        """
        Create hash of phone number for privacy and indexing
        
        Args:
            phone_number: Phone number to hash
            
        Returns:
            SHA256 hash of phone number
        """
        return hashlib.sha256(phone_number.encode()).hexdigest()
    
    def _safe_json_loads(self, json_str: str) -> any:
        """
        Safely load JSON string with error handling
        
        Args:
            json_str: JSON string to parse
            
        Returns:
            Parsed JSON object or appropriate default
        """
        if not json_str:
            return {}
        
        try:
            return json.loads(json_str)
        except (json.JSONDecodeError, TypeError) as e:
            self.logger.warning(f"Failed to parse JSON: {json_str[:100]}... Error: {str(e)}")
            return {}
    
    def store_investigation_data(self, phone_number: str, intelligence_data: Dict) -> None:
        """
        Store current investigation data for historical tracking
        
        Args:
            phone_number: Phone number investigated
            intelligence_data: Complete intelligence data from investigation
        """
        try:
            phone_hash = self._hash_phone_number(phone_number)
            current_time = datetime.now()
            
            # Extract key fields from intelligence data
            technical_intel = intelligence_data.get('technical_intelligence', {})
            carrier_intel = intelligence_data.get('carrier_intelligence', {})
            security_intel = intelligence_data.get('security_intelligence', {})
            social_intel = intelligence_data.get('social_intelligence', {})
            business_intel = intelligence_data.get('business_intelligence', {})
            
            # Create investigation record
            record = PhoneInvestigationRecord(
                phone_number=phone_number,
                investigation_timestamp=current_time,
                country_code=technical_intel.get('country_code', ''),
                carrier_name=carrier_intel.get('carrier_name', ''),
                location=technical_intel.get('location', ''),
                number_type=technical_intel.get('number_type', ''),
                is_valid=technical_intel.get('is_valid', False),
                is_mobile=technical_intel.get('is_mobile', False),
                reputation_score=security_intel.get('reputation_score', 0.0),
                social_media_presence=social_intel,
                whois_domains=business_intel.get('domains', []),
                api_sources=intelligence_data.get('api_sources_used', []),
                confidence_score=intelligence_data.get('confidence_score', 0.0),
                raw_data=intelligence_data
            )
            
            # Store in database
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    INSERT INTO phone_investigations (
                        phone_number, phone_hash, investigation_timestamp,
                        country_code, carrier_name, location, number_type,
                        is_valid, is_mobile, reputation_score,
                        social_media_presence, whois_domains, api_sources,
                        confidence_score, raw_data
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    phone_number, phone_hash, current_time.isoformat(),
                    record.country_code, record.carrier_name, record.location, record.number_type,
                    record.is_valid, record.is_mobile, record.reputation_score,
                    json.dumps(record.social_media_presence), json.dumps(record.whois_domains),
                    json.dumps(record.api_sources), record.confidence_score, json.dumps(record.raw_data)
                ))
                
                # Update metadata
                self._update_investigation_metadata(cursor, phone_number, phone_hash, current_time)
                
                conn.commit()
                
            # Detect changes if previous data exists
            self._detect_and_store_changes(phone_number, record)
            
            self.logger.info(f"Stored investigation data for {phone_number}")
            
        except Exception as e:
            self.logger.error(f"Error storing investigation data: {str(e)}")
            raise
    
    def _update_investigation_metadata(self, cursor, phone_number: str, phone_hash: str, current_time: datetime) -> None:
        """Update investigation metadata for a phone number"""
        # Check if metadata exists
        cursor.execute('SELECT * FROM investigation_metadata WHERE phone_hash = ?', (phone_hash,))
        existing = cursor.fetchone()
        
        if existing:
            # Update existing metadata
            cursor.execute('''
                UPDATE investigation_metadata 
                SET last_seen = ?, total_investigations = total_investigations + 1, updated_at = ?
                WHERE phone_hash = ?
            ''', (current_time.isoformat(), current_time.isoformat(), phone_hash))
        else:
            # Create new metadata
            cursor.execute('''
                INSERT INTO investigation_metadata (
                    phone_number, phone_hash, first_seen, last_seen, total_investigations
                ) VALUES (?, ?, ?, ?, 1)
            ''', (phone_number, phone_hash, current_time.isoformat(), current_time.isoformat()))
    
    def get_historical_data(self, phone_number: str, limit: int = 10) -> Dict:
        """
        Retrieve historical data for comparison
        
        Args:
            phone_number: Phone number to retrieve history for
            limit: Maximum number of records to retrieve
            
        Returns:
            Dict containing historical investigation data
        """
        try:
            phone_hash = self._hash_phone_number(phone_number)
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Get historical investigations
                cursor.execute('''
                    SELECT * FROM phone_investigations 
                    WHERE phone_hash = ? 
                    ORDER BY investigation_timestamp DESC 
                    LIMIT ?
                ''', (phone_hash, limit))
                
                investigations = []
                for row in cursor.fetchall():
                    investigations.append({
                        'id': row[0],
                        'phone_number': row[1],
                        'investigation_timestamp': row[3],
                        'country_code': row[4],
                        'carrier_name': row[5],
                        'location': row[6],
                        'number_type': row[7],
                        'is_valid': row[8],
                        'is_mobile': row[9],
                        'reputation_score': row[10],
                        'social_media_presence': self._safe_json_loads(row[11]),
                        'whois_domains': self._safe_json_loads(row[12]),
                        'api_sources': self._safe_json_loads(row[13]),
                        'confidence_score': row[14],
                        'raw_data': self._safe_json_loads(row[15])
                    })
                
                # Get metadata
                cursor.execute('SELECT * FROM investigation_metadata WHERE phone_hash = ?', (phone_hash,))
                metadata_row = cursor.fetchone()
                
                metadata = {}
                if metadata_row:
                    metadata = {
                        'first_seen': metadata_row[3],  # first_seen
                        'last_seen': metadata_row[4],   # last_seen
                        'total_investigations': metadata_row[5],  # total_investigations
                        'change_frequency': metadata_row[6],      # change_frequency
                        'stability_score': metadata_row[7],       # stability_score
                        'risk_indicators': self._safe_json_loads(metadata_row[8])  # risk_indicators (JSON)
                    }
                
                return {
                    'phone_number': phone_number,
                    'investigations': investigations,
                    'metadata': metadata,
                    'total_records': len(investigations)
                }
                
        except Exception as e:
            self.logger.error(f"Error retrieving historical data: {str(e)}")
            return {
                'phone_number': phone_number,
                'investigations': [],
                'metadata': {},
                'total_records': 0,
                'error': str(e)
            }
    
    def detect_changes(self, current_data: Dict, historical_data: Dict) -> Dict:
        """
        Detect and analyze changes over time
        
        Args:
            current_data: Current investigation data
            historical_data: Historical investigation data
            
        Returns:
            Dict containing detected changes and analysis
        """
        try:
            changes_detected = []
            
            if not historical_data.get('investigations'):
                return {
                    'changes_detected': [],
                    'change_summary': 'No historical data available for comparison',
                    'total_changes': 0
                }
            
            # Get the second most recent historical record for comparison (if available)
            # The most recent record (index 0) would be the current investigation
            if len(historical_data['investigations']) < 2:
                return {
                    'changes_detected': [],
                    'change_summary': 'Insufficient historical data for comparison',
                    'total_changes': 0
                }
            
            latest_historical = historical_data['investigations'][1]  # Previous record
            
            # Fields to monitor for changes
            monitored_fields = {
                'carrier_name': 'Carrier Change',
                'location': 'Location Change',
                'number_type': 'Number Type Change',
                'is_valid': 'Validity Change',
                'reputation_score': 'Reputation Change'
            }
            
            current_time = datetime.now()
            
            for field, change_type in monitored_fields.items():
                current_value = current_data.get(field)
                historical_value = latest_historical.get(field)
                
                # Skip if either value is None/empty
                if current_value is None or historical_value is None:
                    continue
                
                # Normalize values for comparison
                current_normalized = self._normalize_value_for_comparison(current_value)
                historical_normalized = self._normalize_value_for_comparison(historical_value)
                
                if current_normalized != historical_normalized:
                    confidence_score = self._calculate_change_confidence(field, str(historical_value), str(current_value))
                    
                    change = HistoricalChange(
                        phone_number=current_data.get('phone_number', ''),
                        change_type=change_type,
                        field_name=field,
                        old_value=str(historical_value),
                        new_value=str(current_value),
                        change_timestamp=current_time,
                        confidence_score=confidence_score,
                        verification_status='Detected',
                        change_source='Automated Detection'
                    )
                    
                    changes_detected.append(change)
            
            # Special handling for carrier changes (porting detection)
            if any(c.field_name == 'carrier_name' for c in changes_detected):
                self._detect_carrier_porting(current_data, latest_historical)
            
            return {
                'changes_detected': [asdict(change) for change in changes_detected],
                'change_summary': f'Detected {len(changes_detected)} changes',
                'total_changes': len(changes_detected),
                'comparison_timestamp': current_time.isoformat(),
                'historical_reference': latest_historical.get('investigation_timestamp')
            }
            
        except Exception as e:
            self.logger.error(f"Error detecting changes: {str(e)}")
            return {
                'changes_detected': [],
                'change_summary': f'Error detecting changes: {str(e)}',
                'total_changes': 0,
                'error': str(e)
            }
    
    def _normalize_value_for_comparison(self, value) -> str:
        """
        Normalize values for consistent comparison
        
        Args:
            value: Value to normalize
            
        Returns:
            Normalized string representation
        """
        if isinstance(value, bool):
            return '1' if value else '0'  # Normalize booleans to match SQLite storage
        elif isinstance(value, (int, float)):
            return str(value)
        elif value is None:
            return ''
        else:
            return str(value).strip()
    
    def _calculate_change_confidence(self, field_name: str, old_value: str, new_value: str) -> float:
        """
        Calculate confidence score for detected changes
        
        Args:
            field_name: Name of the field that changed
            old_value: Previous value
            new_value: Current value
            
        Returns:
            Confidence score between 0.0 and 1.0
        """
        # Base confidence scores by field type
        field_confidence = {
            'carrier_name': 0.9,  # High confidence for carrier changes
            'location': 0.7,      # Medium-high for location changes
            'number_type': 0.8,   # High for number type changes
            'is_valid': 0.6,      # Medium for validity changes
            'reputation_score': 0.5  # Lower for reputation changes (more volatile)
        }
        
        base_confidence = field_confidence.get(field_name, 0.5)
        
        # Adjust based on value characteristics
        if field_name == 'reputation_score':
            try:
                old_score = float(old_value)
                new_score = float(new_value)
                score_diff = abs(new_score - old_score)
                
                # Higher confidence for larger reputation changes
                if score_diff > 0.3:
                    base_confidence = 0.8
                elif score_diff > 0.1:
                    base_confidence = 0.6
                else:
                    base_confidence = 0.4
            except ValueError:
                pass
        
        return base_confidence
    
    def _detect_carrier_porting(self, current_data: Dict, historical_data: Dict) -> None:
        """
        Detect and record carrier porting activities
        
        Args:
            current_data: Current investigation data
            historical_data: Historical investigation data
        """
        try:
            phone_number = current_data.get('phone_number', '')
            phone_hash = self._hash_phone_number(phone_number)
            
            old_carrier = historical_data.get('carrier_name', '')
            new_carrier = current_data.get('carrier_name', '')
            
            if old_carrier and new_carrier and old_carrier != new_carrier:
                current_time = datetime.now()
                
                with sqlite3.connect(self.db_path) as conn:
                    cursor = conn.cursor()
                    
                    cursor.execute('''
                        INSERT INTO carrier_transitions (
                            phone_number, phone_hash, from_carrier, to_carrier,
                            transition_timestamp, transition_type, confidence_score,
                            porting_detected, verification_status
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        phone_number, phone_hash, old_carrier, new_carrier,
                        current_time.isoformat(), 'MNP Porting', 0.8, True, 'Detected'
                    ))
                    
                    conn.commit()
                    
                self.logger.info(f"Detected carrier porting: {old_carrier} -> {new_carrier} for {phone_number}")
                
        except Exception as e:
            self.logger.error(f"Error detecting carrier porting: {str(e)}")
    
    def _detect_and_store_changes(self, phone_number: str, current_record: PhoneInvestigationRecord) -> None:
        """
        Detect changes and store them in the database
        
        Args:
            phone_number: Phone number being investigated
            current_record: Current investigation record
        """
        try:
            # Get historical data for comparison (need at least 2 records)
            historical_data = self.get_historical_data(phone_number, limit=2)
            
            if historical_data['total_records'] >= 2:
                # Convert current record to dict for comparison
                current_data = asdict(current_record)
                
                # Detect changes
                changes_result = self.detect_changes(current_data, historical_data)
                
                # Check for carrier changes and trigger porting detection
                if any(change['field_name'] == 'carrier_name' for change in changes_result.get('changes_detected', [])):
                    # Get the previous record for carrier comparison
                    current_carrier_data = {'carrier_name': current_record.carrier_name}
                    previous_carrier_data = {'carrier_name': historical_data['investigations'][1]['carrier_name']}
                    self._detect_carrier_porting(current_carrier_data, previous_carrier_data)
                
                # Store detected changes
                if changes_result['total_changes'] > 0:
                    phone_hash = self._hash_phone_number(phone_number)
                    
                    with sqlite3.connect(self.db_path) as conn:
                        cursor = conn.cursor()
                        
                        for change in changes_result['changes_detected']:
                            # Handle datetime serialization
                            timestamp = change['change_timestamp']
                            if hasattr(timestamp, 'isoformat'):
                                timestamp = timestamp.isoformat()
                            
                            cursor.execute('''
                                INSERT INTO historical_changes (
                                    phone_number, phone_hash, change_type, field_name,
                                    old_value, new_value, change_timestamp,
                                    confidence_score, verification_status, change_source
                                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                            ''', (
                                phone_number, phone_hash, change['change_type'], change['field_name'],
                                change['old_value'], change['new_value'], timestamp,
                                change['confidence_score'], change['verification_status'], change['change_source']
                            ))
                        
                        conn.commit()
                        
        except Exception as e:
            self.logger.error(f"Error detecting and storing changes: {str(e)}")
    
    def generate_change_timeline(self, phone_number: str) -> List[Dict]:
        """
        Generate chronological timeline of changes
        
        Args:
            phone_number: Phone number to generate timeline for
            
        Returns:
            List of timeline events
        """
        try:
            phone_hash = self._hash_phone_number(phone_number)
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Get all changes and transitions
                cursor.execute('''
                    SELECT 'change' as event_type, change_type, field_name, old_value, new_value,
                           change_timestamp, confidence_score, verification_status
                    FROM historical_changes 
                    WHERE phone_hash = ?
                    
                    UNION ALL
                    
                    SELECT 'transition' as event_type, transition_type, 'carrier', from_carrier, to_carrier,
                           transition_timestamp, confidence_score, verification_status
                    FROM carrier_transitions 
                    WHERE phone_hash = ?
                    
                    ORDER BY change_timestamp DESC
                ''', (phone_hash, phone_hash))
                
                timeline = []
                for row in cursor.fetchall():
                    timeline.append({
                        'event_type': row[0],
                        'change_type': row[1],
                        'field_name': row[2],
                        'old_value': row[3],
                        'new_value': row[4],
                        'timestamp': row[5],
                        'confidence_score': row[6],
                        'verification_status': row[7]
                    })
                
                return timeline
                
        except Exception as e:
            self.logger.error(f"Error generating change timeline: {str(e)}")
            return []
    
    def detect_number_porting(self, phone_number: str) -> Dict:
        """
        Detect number porting activities and carrier transitions
        
        Args:
            phone_number: Phone number to analyze for porting
            
        Returns:
            Dict containing porting analysis results
        """
        try:
            phone_hash = self._hash_phone_number(phone_number)
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Get carrier transitions
                cursor.execute('''
                    SELECT * FROM carrier_transitions 
                    WHERE phone_hash = ? 
                    ORDER BY transition_timestamp DESC
                ''', (phone_hash,))
                
                transitions = []
                for row in cursor.fetchall():
                    transitions.append({
                        'from_carrier': row[3],
                        'to_carrier': row[4],
                        'transition_timestamp': row[5],
                        'transition_type': row[6],
                        'confidence_score': row[7],
                        'porting_detected': row[8],
                        'verification_status': row[9]
                    })
                
                # Analyze porting patterns
                porting_analysis = {
                    'total_transitions': len(transitions),
                    'porting_detected': any(t['porting_detected'] for t in transitions),
                    'transitions': transitions,
                    'porting_confidence': 0.0,
                    'current_carrier': None,
                    'original_carrier': None,
                    'porting_timeline': []
                }
                
                if transitions:
                    porting_analysis['current_carrier'] = transitions[0]['to_carrier']
                    porting_analysis['original_carrier'] = transitions[-1]['from_carrier']
                    porting_analysis['porting_confidence'] = sum(t['confidence_score'] for t in transitions) / len(transitions)
                    porting_analysis['porting_timeline'] = [
                        {
                            'date': t['transition_timestamp'],
                            'from': t['from_carrier'],
                            'to': t['to_carrier'],
                            'confidence': t['confidence_score']
                        }
                        for t in reversed(transitions)
                    ]
                
                return porting_analysis
                
        except Exception as e:
            self.logger.error(f"Error detecting number porting: {str(e)}")
            return {
                'total_transitions': 0,
                'porting_detected': False,
                'transitions': [],
                'porting_confidence': 0.0,
                'error': str(e)
            }
    
    def detect_ownership_changes(self, phone_number: str) -> Dict:
        """
        Detect ownership change indicators for recycling and porting activities
        
        Args:
            phone_number: Phone number to analyze
            
        Returns:
            Dict containing ownership change analysis
        """
        try:
            historical_data = self.get_historical_data(phone_number, limit=50)
            
            if historical_data['total_records'] < 2:
                return {
                    'ownership_changes_detected': False,
                    'confidence_score': 0.0,
                    'indicators': [],
                    'analysis': 'Insufficient historical data for ownership analysis'
                }
            
            investigations = historical_data['investigations']
            indicators = []
            
            # Check for significant reputation changes
            reputation_scores = [inv.get('reputation_score', 0) for inv in investigations if inv.get('reputation_score') is not None]
            if len(reputation_scores) > 1:
                reputation_variance = max(reputation_scores) - min(reputation_scores)
                if reputation_variance > 0.5:
                    indicators.append({
                        'type': 'reputation_change',
                        'description': 'Significant reputation score changes detected',
                        'confidence': 0.7,
                        'details': f'Reputation variance: {reputation_variance:.2f}'
                    })
            
            # Check for social media presence changes
            social_changes = 0
            for i in range(1, len(investigations)):
                current_social = investigations[i-1].get('social_media_presence', {})
                previous_social = investigations[i].get('social_media_presence', {})
                
                if current_social != previous_social:
                    social_changes += 1
            
            if social_changes > 0:
                indicators.append({
                    'type': 'social_media_changes',
                    'description': f'Social media presence changes detected ({social_changes} times)',
                    'confidence': 0.6,
                    'details': f'Changes in {social_changes} investigations'
                })
            
            # Check for WHOIS domain changes
            domain_changes = 0
            for i in range(1, len(investigations)):
                current_domains = set(investigations[i-1].get('whois_domains', []))
                previous_domains = set(investigations[i].get('whois_domains', []))
                
                if current_domains != previous_domains:
                    domain_changes += 1
            
            if domain_changes > 0:
                indicators.append({
                    'type': 'domain_association_changes',
                    'description': f'Domain association changes detected ({domain_changes} times)',
                    'confidence': 0.8,
                    'details': f'Changes in {domain_changes} investigations'
                })
            
            # Calculate overall confidence
            if indicators:
                confidence_score = sum(ind['confidence'] for ind in indicators) / len(indicators)
                ownership_changes_detected = confidence_score > 0.6
            else:
                confidence_score = 0.0
                ownership_changes_detected = False
            
            return {
                'ownership_changes_detected': ownership_changes_detected,
                'confidence_score': confidence_score,
                'indicators': indicators,
                'total_indicators': len(indicators),
                'analysis': f'Analyzed {len(investigations)} historical records',
                'recommendation': self._generate_ownership_recommendation(confidence_score, indicators)
            }
            
        except Exception as e:
            self.logger.error(f"Error detecting ownership changes: {str(e)}")
            return {
                'ownership_changes_detected': False,
                'confidence_score': 0.0,
                'indicators': [],
                'error': str(e)
            }
    
    def _generate_ownership_recommendation(self, confidence_score: float, indicators: List[Dict]) -> str:
        """Generate recommendation based on ownership change analysis"""
        if confidence_score > 0.8:
            return "High likelihood of ownership change - recommend manual verification"
        elif confidence_score > 0.6:
            return "Moderate likelihood of ownership change - monitor for additional indicators"
        elif confidence_score > 0.3:
            return "Low likelihood of ownership change - continue normal monitoring"
        else:
            return "No significant ownership change indicators detected"
    
    def calculate_change_confidence_scoring(self, phone_number: str) -> Dict:
        """
        Calculate comprehensive change confidence scoring
        
        Args:
            phone_number: Phone number to analyze
            
        Returns:
            Dict containing confidence scoring analysis
        """
        try:
            historical_data = self.get_historical_data(phone_number)
            timeline = self.generate_change_timeline(phone_number)
            porting_analysis = self.detect_number_porting(phone_number)
            ownership_analysis = self.detect_ownership_changes(phone_number)
            
            # Calculate stability metrics
            total_investigations = historical_data['metadata'].get('total_investigations', 0)
            total_changes = len(timeline)
            
            if total_investigations > 0:
                change_frequency = total_changes / total_investigations
                stability_score = max(0.0, 1.0 - (change_frequency * 2))  # Higher changes = lower stability
            else:
                change_frequency = 0.0
                stability_score = 1.0
            
            # Calculate verification recommendations
            recommendations = []
            
            if porting_analysis['porting_detected']:
                recommendations.append("Verify current carrier through direct API calls")
            
            if ownership_analysis['ownership_changes_detected']:
                recommendations.append("Manual verification recommended due to ownership change indicators")
            
            if change_frequency > 0.5:
                recommendations.append("High change frequency detected - monitor closely")
            
            if not recommendations:
                recommendations.append("No special verification requirements detected")
            
            return {
                'phone_number': phone_number,
                'stability_score': stability_score,
                'change_frequency': change_frequency,
                'total_investigations': total_investigations,
                'total_changes': total_changes,
                'porting_confidence': porting_analysis['porting_confidence'],
                'ownership_change_confidence': ownership_analysis['confidence_score'],
                'overall_confidence': (stability_score + (1.0 - change_frequency)) / 2,
                'verification_recommendations': recommendations,
                'risk_level': self._calculate_risk_level(stability_score, change_frequency, ownership_analysis['confidence_score']),
                'last_analysis': datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Error calculating change confidence scoring: {str(e)}")
            return {
                'phone_number': phone_number,
                'error': str(e),
                'overall_confidence': 0.0,
                'verification_recommendations': ["Error in analysis - manual verification recommended"]
            }
    
    def _calculate_risk_level(self, stability_score: float, change_frequency: float, ownership_confidence: float) -> str:
        """Calculate overall risk level based on various factors"""
        risk_score = (1.0 - stability_score) + change_frequency + ownership_confidence
        
        if risk_score > 2.0:
            return "High Risk"
        elif risk_score > 1.0:
            return "Medium Risk"
        elif risk_score > 0.5:
            return "Low Risk"
        else:
            return "Minimal Risk"
    
    def get_investigation_history_summary(self, phone_number: str) -> Dict:
        """
        Get comprehensive investigation history summary
        
        Args:
            phone_number: Phone number to summarize
            
        Returns:
            Dict containing complete history summary
        """
        try:
            historical_data = self.get_historical_data(phone_number)
            timeline = self.generate_change_timeline(phone_number)
            porting_analysis = self.detect_number_porting(phone_number)
            ownership_analysis = self.detect_ownership_changes(phone_number)
            confidence_analysis = self.calculate_change_confidence_scoring(phone_number)
            
            return {
                'phone_number': phone_number,
                'summary_generated': datetime.now().isoformat(),
                'historical_data': historical_data,
                'change_timeline': timeline,
                'porting_analysis': porting_analysis,
                'ownership_analysis': ownership_analysis,
                'confidence_analysis': confidence_analysis,
                'investigation_quality': self._assess_investigation_quality(historical_data, timeline),
                'recommendations': self._generate_investigation_recommendations(
                    historical_data, porting_analysis, ownership_analysis, confidence_analysis
                )
            }
            
        except Exception as e:
            self.logger.error(f"Error generating investigation history summary: {str(e)}")
            return {
                'phone_number': phone_number,
                'error': str(e),
                'summary_generated': datetime.now().isoformat()
            }
    
    def _assess_investigation_quality(self, historical_data: Dict, timeline: List[Dict]) -> str:
        """Assess the quality of investigation data"""
        total_records = historical_data.get('total_records', 0)
        
        if total_records >= 10:
            return "High Quality - Extensive historical data available"
        elif total_records >= 5:
            return "Good Quality - Sufficient historical data for analysis"
        elif total_records >= 2:
            return "Fair Quality - Limited historical data available"
        else:
            return "Poor Quality - Insufficient historical data for reliable analysis"
    
    def _generate_investigation_recommendations(self, historical_data: Dict, porting_analysis: Dict, 
                                             ownership_analysis: Dict, confidence_analysis: Dict) -> List[str]:
        """Generate comprehensive investigation recommendations"""
        recommendations = []
        
        # Based on historical data quality
        if historical_data.get('total_records', 0) < 3:
            recommendations.append("Conduct additional investigations to build historical baseline")
        
        # Based on porting analysis
        if porting_analysis.get('porting_detected'):
            recommendations.append("Verify current carrier information through multiple sources")
        
        # Based on ownership analysis
        if ownership_analysis.get('ownership_changes_detected'):
            recommendations.append("Consider manual verification due to potential ownership changes")
        
        # Based on confidence analysis
        risk_level = confidence_analysis.get('risk_level', 'Unknown')
        if risk_level in ['High Risk', 'Medium Risk']:
            recommendations.append(f"Enhanced monitoring recommended due to {risk_level} classification")
        
        # General recommendations
        if not recommendations:
            recommendations.append("Continue standard monitoring and investigation procedures")
        
        return recommendations
    
    def cleanup_old_data(self, retention_days: int = 365) -> Dict:
        """
        Clean up old investigation data based on retention policy
        
        Args:
            retention_days: Number of days to retain data
            
        Returns:
            Dict containing cleanup results
        """
        try:
            cutoff_date = (datetime.now() - timedelta(days=retention_days)).isoformat()
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Count records to be deleted
                cursor.execute('SELECT COUNT(*) FROM phone_investigations WHERE created_at < ?', (cutoff_date,))
                investigations_to_delete = cursor.fetchone()[0]
                
                cursor.execute('SELECT COUNT(*) FROM historical_changes WHERE created_at < ?', (cutoff_date,))
                changes_to_delete = cursor.fetchone()[0]
                
                cursor.execute('SELECT COUNT(*) FROM carrier_transitions WHERE created_at < ?', (cutoff_date,))
                transitions_to_delete = cursor.fetchone()[0]
                
                # Delete old records
                cursor.execute('DELETE FROM phone_investigations WHERE created_at < ?', (cutoff_date,))
                cursor.execute('DELETE FROM historical_changes WHERE created_at < ?', (cutoff_date,))
                cursor.execute('DELETE FROM carrier_transitions WHERE created_at < ?', (cutoff_date,))
                
                # Clean up orphaned metadata
                cursor.execute('''
                    DELETE FROM investigation_metadata 
                    WHERE phone_hash NOT IN (SELECT DISTINCT phone_hash FROM phone_investigations)
                ''')
                orphaned_metadata = cursor.rowcount
                
                conn.commit()
                
                return {
                    'cleanup_completed': True,
                    'retention_days': retention_days,
                    'cutoff_date': cutoff_date,
                    'records_deleted': {
                        'investigations': investigations_to_delete,
                        'changes': changes_to_delete,
                        'transitions': transitions_to_delete,
                        'orphaned_metadata': orphaned_metadata
                    },
                    'total_deleted': investigations_to_delete + changes_to_delete + transitions_to_delete + orphaned_metadata
                }
                
        except Exception as e:
            self.logger.error(f"Error during data cleanup: {str(e)}")
            return {
                'cleanup_completed': False,
                'error': str(e)
            }