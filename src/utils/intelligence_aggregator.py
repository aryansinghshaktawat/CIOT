"""
Multi-Source Intelligence Aggregator
Coordinates data from multiple sources with confidence scoring and data merging
"""

import time
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field
from enum import Enum
import statistics
import requests
import re
from .whois_checker import WHOISChecker
from .pattern_analysis import PatternAnalysisEngine
from .historical_data_manager import HistoricalDataManager


class ConfidenceLevel(Enum):
    """Confidence levels for intelligence data"""
    CRITICAL = 95  # 95-100%
    HIGH = 80     # 80-94%
    MEDIUM = 60   # 60-79%
    LOW = 40      # 40-59%
    VERY_LOW = 20 # 20-39%
    UNRELIABLE = 0 # 0-19%


class DataSource(Enum):
    """Available data sources"""
    LIBPHONENUMBER = "libphonenumber"
    ABSTRACTAPI = "abstractapi"
    NEUTRINO = "neutrino"
    FINDANDTRACE = "findandtrace"
    TELNYX = "telnyx"
    NUMVERIFY = "numverify"
    VERIPHONE = "veriphone"
    WHOIS = "whois"
    PATTERN_ANALYSIS = "pattern_analysis"


@dataclass
class IntelligenceResult:
    """Container for intelligence data with confidence scoring"""
    source: DataSource
    data: Dict[str, Any]
    confidence: float
    timestamp: float
    success: bool
    error: Optional[str] = None
    response_time: float = 0.0
    
    def __post_init__(self):
        """Validate confidence score"""
        if not 0 <= self.confidence <= 100:
            raise ValueError(f"Confidence must be between 0-100, got {self.confidence}")


@dataclass
class AggregatedIntelligence:
    """Final aggregated intelligence with merged data"""
    phone_number: str
    country_code: str
    results: List[IntelligenceResult] = field(default_factory=list)
    merged_data: Dict[str, Any] = field(default_factory=dict)
    overall_confidence: float = 0.0
    sources_used: List[str] = field(default_factory=list)
    total_sources: int = 0
    successful_sources: int = 0
    processing_time: float = 0.0
    errors: List[str] = field(default_factory=list)


class IntelligenceAggregator:
    """
    Multi-source intelligence aggregator for phone number investigation
    Coordinates data from multiple APIs with confidence scoring and intelligent merging
    """
    
    def __init__(self):
        # Initialize WHOIS checker, pattern analysis engine, and historical data manager
        self.whois_checker = WHOISChecker()
        self.pattern_engine = PatternAnalysisEngine()
        self.historical_manager = HistoricalDataManager()
        
        # Source reliability weights (based on historical accuracy)
        self.source_weights = {
            DataSource.LIBPHONENUMBER: 0.95,  # Highest reliability - local processing
            DataSource.ABSTRACTAPI: 0.85,    # High reliability - good for validation
            DataSource.NEUTRINO: 0.80,       # Good reliability - carrier info
            DataSource.TELNYX: 0.85,         # High reliability - telecom grade
            DataSource.FINDANDTRACE: 0.70,   # Medium reliability - web scraping
            DataSource.NUMVERIFY: 0.75,      # Good reliability - basic validation
            DataSource.VERIPHONE: 0.75,      # Good reliability - basic validation
            DataSource.WHOIS: 0.80,          # Good reliability - domain linkage
            DataSource.PATTERN_ANALYSIS: 0.85  # High reliability - algorithmic analysis
        }
        
        # Field priority mapping (which source to trust for specific fields)
        self.field_priorities = {
            'is_valid': [DataSource.LIBPHONENUMBER, DataSource.ABSTRACTAPI, DataSource.TELNYX],
            'country': [DataSource.LIBPHONENUMBER, DataSource.ABSTRACTAPI, DataSource.NEUTRINO],
            'carrier': [DataSource.NEUTRINO, DataSource.TELNYX, DataSource.FINDANDTRACE],
            'line_type': [DataSource.LIBPHONENUMBER, DataSource.ABSTRACTAPI, DataSource.NEUTRINO],
            'location': [DataSource.FINDANDTRACE, DataSource.NEUTRINO, DataSource.ABSTRACTAPI],
            'operator': [DataSource.FINDANDTRACE, DataSource.NEUTRINO, DataSource.ABSTRACTAPI],
            'circle': [DataSource.FINDANDTRACE, DataSource.LIBPHONENUMBER],
            'state': [DataSource.FINDANDTRACE, DataSource.NEUTRINO],
            'domains': [DataSource.WHOIS],
            'business_connections': [DataSource.WHOIS],
            'domain_count': [DataSource.WHOIS],
            'related_numbers': [DataSource.PATTERN_ANALYSIS],
            'bulk_registration': [DataSource.PATTERN_ANALYSIS],
            'sequential_patterns': [DataSource.PATTERN_ANALYSIS],
            'carrier_block': [DataSource.PATTERN_ANALYSIS],
            'pattern_intelligence': [DataSource.PATTERN_ANALYSIS]
        }
        
        # Timeout settings for different sources
        self.source_timeouts = {
            DataSource.LIBPHONENUMBER: 1.0,   # Local processing - fast
            DataSource.ABSTRACTAPI: 10.0,    # API call
            DataSource.NEUTRINO: 10.0,       # API call
            DataSource.TELNYX: 10.0,         # API call
            DataSource.FINDANDTRACE: 15.0,   # Web scraping - slower
            DataSource.NUMVERIFY: 10.0,      # API call
            DataSource.VERIPHONE: 10.0,      # API call
            DataSource.WHOIS: 30.0,          # WHOIS lookups - can be slow
            DataSource.PATTERN_ANALYSIS: 5.0  # Pattern analysis - local processing
        }
    
    def aggregate_intelligence(self, phone_number: str, country_code: str = 'IN', 
                             sources: Optional[List[DataSource]] = None) -> AggregatedIntelligence:
        """
        Aggregate intelligence from multiple sources
        
        Args:
            phone_number: Phone number to investigate
            country_code: Country context for investigation
            sources: Specific sources to use (None = use all available)
            
        Returns:
            AggregatedIntelligence with merged data and confidence scores
        """
        start_time = time.time()
        
        # Initialize aggregated result
        aggregated = AggregatedIntelligence(
            phone_number=phone_number,
            country_code=country_code
        )
        
        # Determine sources to use
        if sources is None:
            sources = list(DataSource)
        
        aggregated.total_sources = len(sources)
        
        # Collect data from each source
        for source in sources:
            try:
                result = self._query_source(source, phone_number, country_code)
                aggregated.results.append(result)
                aggregated.sources_used.append(source.value)
                
                if result.success:
                    aggregated.successful_sources += 1
                else:
                    aggregated.errors.append(f"{source.value}: {result.error}")
                    
            except Exception as e:
                error_msg = f"{source.value}: {str(e)}"
                aggregated.errors.append(error_msg)
                
                # Add failed result
                failed_result = IntelligenceResult(
                    source=source,
                    data={},
                    confidence=0.0,
                    timestamp=time.time(),
                    success=False,
                    error=str(e)
                )
                aggregated.results.append(failed_result)
        
        # Merge data from successful sources
        aggregated.merged_data = self._merge_intelligence_data(aggregated.results)
        
        # Calculate overall confidence
        aggregated.overall_confidence = self._calculate_overall_confidence(aggregated.results)
        
        # Calculate processing time
        aggregated.processing_time = time.time() - start_time
        
        # Store investigation data for historical tracking
        try:
            self._store_historical_data(phone_number, aggregated)
        except Exception as e:
            aggregated.errors.append(f"Historical data storage error: {str(e)}")
        
        return aggregated
    
    def _query_source(self, source: DataSource, phone_number: str, country_code: str) -> IntelligenceResult:
        """
        Query a specific intelligence source
        
        Args:
            source: Data source to query
            phone_number: Phone number to investigate
            country_code: Country context
            
        Returns:
            IntelligenceResult with data and confidence score
        """
        start_time = time.time()
        timeout = self.source_timeouts.get(source, 10.0)
        
        try:
            if source == DataSource.LIBPHONENUMBER:
                data, confidence = self._query_libphonenumber(phone_number, country_code)
            elif source == DataSource.ABSTRACTAPI:
                data, confidence = self._query_abstractapi(phone_number, timeout)
            elif source == DataSource.NEUTRINO:
                data, confidence = self._query_neutrino(phone_number, country_code, timeout)
            elif source == DataSource.FINDANDTRACE:
                data, confidence = self._query_findandtrace(phone_number, timeout)
            elif source == DataSource.TELNYX:
                data, confidence = self._query_telnyx(phone_number, timeout)
            elif source == DataSource.NUMVERIFY:
                data, confidence = self._query_numverify(phone_number, timeout)
            elif source == DataSource.VERIPHONE:
                data, confidence = self._query_veriphone(phone_number, timeout)
            elif source == DataSource.WHOIS:
                data, confidence = self._query_whois(phone_number, timeout)
            elif source == DataSource.PATTERN_ANALYSIS:
                data, confidence = self._query_pattern_analysis(phone_number, country_code, timeout)
            else:
                raise ValueError(f"Unsupported source: {source}")
            
            response_time = time.time() - start_time
            
            return IntelligenceResult(
                source=source,
                data=data,
                confidence=confidence,
                timestamp=time.time(),
                success=True,
                response_time=response_time
            )
            
        except Exception as e:
            response_time = time.time() - start_time
            
            return IntelligenceResult(
                source=source,
                data={},
                confidence=0.0,
                timestamp=time.time(),
                success=False,
                error=str(e),
                response_time=response_time
            )
    
    def _query_libphonenumber(self, phone_number: str, country_code: str) -> Tuple[Dict, float]:
        """Query libphonenumber for phone data"""
        try:
            import phonenumbers
            from phonenumbers import geocoder, carrier, timezone
            
            parsed_number = phonenumbers.parse(phone_number, country_code)
            
            if not phonenumbers.is_valid_number(parsed_number):
                return {}, 20.0  # Low confidence for invalid numbers
            
            data = {
                'is_valid': phonenumbers.is_valid_number(parsed_number),
                'is_possible': phonenumbers.is_possible_number(parsed_number),
                'country': geocoder.description_for_number(parsed_number, 'en'),
                'country_code': parsed_number.country_code,
                'national_number': parsed_number.national_number,
                'international_format': phonenumbers.format_number(parsed_number, phonenumbers.PhoneNumberFormat.INTERNATIONAL),
                'national_format': phonenumbers.format_number(parsed_number, phonenumbers.PhoneNumberFormat.NATIONAL),
                'e164_format': phonenumbers.format_number(parsed_number, phonenumbers.PhoneNumberFormat.E164),
                'carrier': carrier.name_for_number(parsed_number, 'en'),
                'location': geocoder.description_for_number(parsed_number, 'en'),
                'timezones': timezone.time_zones_for_number(parsed_number),
                'line_type': phonenumbers.number_type(parsed_number).name,
                'region_code': phonenumbers.region_code_for_number(parsed_number)
            }
            
            # High confidence for libphonenumber (local processing)
            confidence = 95.0 if data['is_valid'] else 85.0
            
            return data, confidence
            
        except Exception as e:
            return {'error': str(e)}, 10.0
    
    def _query_abstractapi(self, phone_number: str, timeout: float) -> Tuple[Dict, float]:
        """Query AbstractAPI for phone validation"""
        try:
            from utils.osint_utils import load_api_keys
            
            api_keys = load_api_keys()
            if 'abstractapi' not in api_keys:
                return {'error': 'API key not available'}, 0.0
            
            # Format phone number
            clean_phone = re.sub(r'[^\d+]', '', phone_number)
            if not clean_phone.startswith('+'):
                if len(clean_phone) == 10 and clean_phone[0] in ['6', '7', '8', '9']:
                    clean_phone = f'+91{clean_phone}'
                elif len(clean_phone) == 12 and clean_phone.startswith('91'):
                    clean_phone = f'+{clean_phone}'
            
            url = f"https://phonevalidation.abstractapi.com/v1/?api_key={api_keys['abstractapi']['api_key']}&phone={clean_phone}"
            
            response = requests.get(url, timeout=timeout)
            if response.status_code == 200:
                data = response.json()
                
                # Calculate confidence based on data completeness
                confidence = 85.0 if data.get('valid') else 40.0
                if data.get('carrier') and data.get('carrier') != 'Unknown':
                    confidence += 10.0
                
                return data, min(confidence, 95.0)
            else:
                return {'error': f'HTTP {response.status_code}'}, 20.0
                
        except Exception as e:
            return {'error': str(e)}, 10.0
    
    def _query_neutrino(self, phone_number: str, country_code: str, timeout: float) -> Tuple[Dict, float]:
        """Query Neutrino API for phone validation"""
        try:
            from utils.osint_utils import load_api_keys
            
            api_keys = load_api_keys()
            if 'neutrino' not in api_keys:
                return {'error': 'API key not available'}, 0.0
            
            # Format phone number
            clean_phone = re.sub(r'[^\d+]', '', phone_number)
            if not clean_phone.startswith('+'):
                if len(clean_phone) == 10 and clean_phone[0] in ['6', '7', '8', '9']:
                    clean_phone = f'+91{clean_phone}'
            
            url = "https://neutrinoapi.net/phone-validate"
            data = {
                'user-id': api_keys['neutrino']['user_id'],
                'api-key': api_keys['neutrino']['api_key'],
                'number': clean_phone,
                'country-code': country_code
            }
            
            response = requests.post(url, data=data, timeout=timeout)
            if response.status_code == 200:
                result = response.json()
                
                # Calculate confidence based on validation result
                confidence = 80.0 if result.get('valid') else 30.0
                if result.get('prefix-network'):
                    confidence += 10.0
                
                return result, min(confidence, 90.0)
            else:
                return {'error': f'HTTP {response.status_code}'}, 20.0
                
        except Exception as e:
            return {'error': str(e)}, 10.0
    
    def _query_findandtrace(self, phone_number: str, timeout: float) -> Tuple[Dict, float]:
        """Query Find and Trace for Indian phone data"""
        try:
            from utils.osint_utils import get_findandtrace_data
            
            clean_phone = re.sub(r'[^\d]', '', phone_number)
            
            # Only for Indian numbers
            if len(clean_phone) == 10 and clean_phone[0] in ['6', '7', '8', '9']:
                data = get_findandtrace_data(clean_phone)
                
                if data.get('success'):
                    # Calculate confidence based on data availability
                    confidence = 70.0  # Base confidence for Find and Trace
                    if data.get('operator'):
                        confidence += 10.0
                    if data.get('telecom_circle'):
                        confidence += 10.0
                    
                    return data, min(confidence, 85.0)
                else:
                    return data, 30.0
            else:
                return {'error': 'Not an Indian mobile number'}, 0.0
                
        except Exception as e:
            return {'error': str(e)}, 10.0
    
    def _query_telnyx(self, phone_number: str, timeout: float) -> Tuple[Dict, float]:
        """Query Telnyx API for phone data"""
        try:
            from utils.osint_utils import load_api_keys
            
            api_keys = load_api_keys()
            if 'telnyx' not in api_keys:
                return {'error': 'API key not available'}, 0.0
            
            # Format phone number
            clean_phone = re.sub(r'[^\d+]', '', phone_number)
            if not clean_phone.startswith('+'):
                if len(clean_phone) == 10 and clean_phone[0] in ['6', '7', '8', '9']:
                    clean_phone = f'+91{clean_phone}'
            
            url = f"https://api.telnyx.com/v2/number_lookup/{clean_phone}"
            headers = {
                'Authorization': f"Bearer {api_keys['telnyx']['api_key']}",
                'Content-Type': 'application/json'
            }
            
            response = requests.get(url, headers=headers, timeout=timeout)
            if response.status_code == 200:
                data = response.json()
                
                # Calculate confidence based on data quality
                confidence = 85.0 if data.get('data') else 40.0
                
                return data, confidence
            else:
                return {'error': f'HTTP {response.status_code}'}, 20.0
                
        except Exception as e:
            return {'error': str(e)}, 10.0
    
    def _query_numverify(self, phone_number: str, timeout: float) -> Tuple[Dict, float]:
        """Query Numverify API for phone validation"""
        try:
            from utils.osint_utils import load_api_keys
            
            api_keys = load_api_keys()
            if 'numverify' not in api_keys:
                return {'error': 'API key not available'}, 0.0
            
            # Format phone number
            clean_phone = re.sub(r'[^\d+]', '', phone_number)
            if not clean_phone.startswith('+'):
                if len(clean_phone) == 10 and clean_phone[0] in ['6', '7', '8', '9']:
                    clean_phone = f'+91{clean_phone}'
            
            url = f"http://apilayer.net/api/validate?access_key={api_keys['numverify']['api_key']}&number={clean_phone}"
            
            response = requests.get(url, timeout=timeout)
            if response.status_code == 200:
                data = response.json()
                
                # Calculate confidence
                confidence = 75.0 if data.get('valid') else 35.0
                
                return data, confidence
            else:
                return {'error': f'HTTP {response.status_code}'}, 20.0
                
        except Exception as e:
            return {'error': str(e)}, 10.0
    
    def _query_veriphone(self, phone_number: str, timeout: float) -> Tuple[Dict, float]:
        """Query Veriphone API for phone validation"""
        try:
            from utils.osint_utils import load_api_keys
            
            api_keys = load_api_keys()
            if 'veriphone' not in api_keys:
                return {'error': 'API key not available'}, 0.0
            
            # Format phone number
            clean_phone = re.sub(r'[^\d+]', '', phone_number)
            if not clean_phone.startswith('+'):
                if len(clean_phone) == 10 and clean_phone[0] in ['6', '7', '8', '9']:
                    clean_phone = f'+91{clean_phone}'
            
            url = f"https://api.veriphone.io/v2/verify?phone={clean_phone}&key={api_keys['veriphone']['api_key']}"
            
            response = requests.get(url, timeout=timeout)
            if response.status_code == 200:
                data = response.json()
                
                # Calculate confidence
                confidence = 75.0 if data.get('phone_valid') else 35.0
                
                return data, confidence
            else:
                return {'error': f'HTTP {response.status_code}'}, 20.0
                
        except Exception as e:
            return {'error': str(e)}, 10.0
    
    def _query_whois(self, phone_number: str, timeout: float) -> Tuple[Dict, float]:
        """Query WHOIS databases for domain linkage"""
        try:
            # Perform WHOIS investigation
            whois_result = self.whois_checker.investigate_phone_whois(phone_number)
            
            if whois_result.total_domains == 0:
                return {'error': 'No domains found'}, 20.0
            
            # Convert WHOIS result to dictionary format
            data = {
                'domains_found': [
                    {
                        'domain': d.domain,
                        'registrar': d.registrar,
                        'status': d.status,
                        'creation_date': d.creation_date.isoformat() if d.creation_date else None,
                        'expiration_date': d.expiration_date.isoformat() if d.expiration_date else None,
                        'registrant_org': d.registrant_org,
                        'registrant_name': d.registrant_name,
                        'confidence': d.confidence
                    }
                    for d in whois_result.domains_found
                ],
                'business_connections': [
                    {
                        'organization': bc.organization,
                        'contact_type': bc.contact_type,
                        'domains': bc.domains,
                        'phone_numbers': bc.phone_numbers,
                        'confidence': bc.confidence
                    }
                    for bc in whois_result.business_connections
                ],
                'total_domains': whois_result.total_domains,
                'active_domains': whois_result.active_domains,
                'expired_domains': whois_result.expired_domains,
                'parked_domains': whois_result.parked_domains,
                'historical_changes': whois_result.historical_changes,
                'business_intelligence': self.whois_checker.generate_business_intelligence_summary(whois_result)
            }
            
            # Calculate confidence based on investigation results
            confidence = whois_result.investigation_confidence
            
            return data, confidence
            
        except Exception as e:
            return {'error': str(e)}, 10.0
    
    def _query_pattern_analysis(self, phone_number: str, country_code: str, timeout: float) -> Tuple[Dict, float]:
        """Query pattern analysis engine for related numbers and patterns"""
        try:
            # Perform comprehensive pattern analysis
            related_numbers = self.pattern_engine.find_related_numbers(phone_number, country_code)
            bulk_registration = self.pattern_engine.detect_bulk_registration(phone_number, country_code)
            sequential_patterns = self.pattern_engine.analyze_sequential_patterns(phone_number, country_code)
            carrier_block = self.pattern_engine.analyze_carrier_block(phone_number, country_code)
            
            # Compile all pattern analysis results
            data = {
                'related_numbers': [
                    {
                        'number': rn.number,
                        'relationship_type': rn.relationship_type,
                        'confidence_score': rn.confidence_score,
                        'evidence': rn.evidence,
                        'investigation_priority': rn.investigation_priority
                    }
                    for rn in related_numbers
                ],
                'bulk_registration': bulk_registration,
                'sequential_patterns': sequential_patterns,
                'carrier_block': carrier_block,
                'total_related_numbers': len(related_numbers),
                'high_confidence_related': len([rn for rn in related_numbers if rn.confidence_score >= 0.7]),
                'investigation_priorities': self.pattern_engine.suggest_investigation_priorities({
                    'related_numbers': related_numbers,
                    'bulk_registration': bulk_registration,
                    'sequential_patterns': sequential_patterns,
                    'carrier_block': carrier_block
                })
            }
            
            # Calculate overall confidence based on pattern analysis results
            confidence = 50.0  # Base confidence
            
            # Boost confidence based on findings
            if bulk_registration.get('detected'):
                confidence += bulk_registration.get('confidence_score', 0) * 0.3
            
            if sequential_patterns.get('found'):
                confidence += sequential_patterns.get('confidence_score', 0) * 0.2
            
            if carrier_block.get('detected'):
                confidence += carrier_block.get('confidence_score', 0) * 0.2
            
            if len(related_numbers) > 0:
                avg_related_confidence = sum(rn.confidence_score for rn in related_numbers) / len(related_numbers)
                confidence += avg_related_confidence * 0.3
            
            return data, min(confidence, 95.0)
            
        except Exception as e:
            return {'error': str(e)}, 10.0
    
    def _merge_intelligence_data(self, results: List[IntelligenceResult]) -> Dict[str, Any]:
        """
        Merge intelligence data from multiple sources using confidence-weighted voting
        
        Args:
            results: List of intelligence results from different sources
            
        Returns:
            Merged data dictionary with best values from all sources
        """
        merged = {}
        
        # Get successful results only
        successful_results = [r for r in results if r.success and r.data]
        
        if not successful_results:
            return merged
        
        # For each field, find the best value based on source priority and confidence
        all_fields = set()
        for result in successful_results:
            all_fields.update(result.data.keys())
        
        for field in all_fields:
            if field == 'error':  # Skip error fields
                continue
                
            field_values = []
            
            # Collect all values for this field with their confidence scores
            for result in successful_results:
                if field in result.data and result.data[field] is not None:
                    value = result.data[field]
                    
                    # Calculate weighted confidence
                    source_weight = self.source_weights.get(result.source, 0.5)
                    weighted_confidence = result.confidence * source_weight
                    
                    # Apply field priority bonus
                    priority_sources = self.field_priorities.get(field, [])
                    if result.source in priority_sources:
                        priority_bonus = (len(priority_sources) - priority_sources.index(result.source)) * 5
                        weighted_confidence += priority_bonus
                    
                    field_values.append({
                        'value': value,
                        'confidence': weighted_confidence,
                        'source': result.source.value
                    })
            
            if field_values:
                # Sort by confidence (highest first)
                field_values.sort(key=lambda x: x['confidence'], reverse=True)
                
                # Use the highest confidence value
                best_value = field_values[0]
                merged[field] = best_value['value']
                merged[f'{field}_confidence'] = best_value['confidence']
                merged[f'{field}_source'] = best_value['source']
                
                # For critical fields, also store alternative values
                if field in ['is_valid', 'country', 'carrier'] and len(field_values) > 1:
                    merged[f'{field}_alternatives'] = [
                        {'value': fv['value'], 'confidence': fv['confidence'], 'source': fv['source']}
                        for fv in field_values[1:3]  # Store top 2 alternatives
                    ]
        
        return merged
    
    def _calculate_overall_confidence(self, results: List[IntelligenceResult]) -> float:
        """
        Calculate overall confidence score based on all results
        
        Args:
            results: List of intelligence results
            
        Returns:
            Overall confidence score (0-100)
        """
        if not results:
            return 0.0
        
        successful_results = [r for r in results if r.success]
        
        if not successful_results:
            return 0.0
        
        # Calculate weighted average confidence
        total_weight = 0.0
        weighted_confidence = 0.0
        
        for result in successful_results:
            source_weight = self.source_weights.get(result.source, 0.5)
            total_weight += source_weight
            weighted_confidence += result.confidence * source_weight
        
        if total_weight == 0:
            return 0.0
        
        base_confidence = weighted_confidence / total_weight
        
        # Apply bonuses/penalties
        success_rate = len(successful_results) / len(results)
        success_bonus = success_rate * 10  # Up to 10% bonus for high success rate
        
        # Penalty for low number of sources
        if len(successful_results) < 2:
            source_penalty = 15  # 15% penalty for single source
        elif len(successful_results) < 3:
            source_penalty = 5   # 5% penalty for only 2 sources
        else:
            source_penalty = 0
        
        final_confidence = base_confidence + success_bonus - source_penalty
        
        return max(0.0, min(100.0, final_confidence))
    
    def get_confidence_level(self, confidence_score: float) -> ConfidenceLevel:
        """
        Convert confidence score to confidence level enum
        
        Args:
            confidence_score: Numeric confidence score (0-100)
            
        Returns:
            ConfidenceLevel enum
        """
        if confidence_score >= 95:
            return ConfidenceLevel.CRITICAL
        elif confidence_score >= 80:
            return ConfidenceLevel.HIGH
        elif confidence_score >= 60:
            return ConfidenceLevel.MEDIUM
        elif confidence_score >= 40:
            return ConfidenceLevel.LOW
        elif confidence_score >= 20:
            return ConfidenceLevel.VERY_LOW
        else:
            return ConfidenceLevel.UNRELIABLE
    
    def generate_intelligence_report(self, aggregated: AggregatedIntelligence) -> str:
        """
        Generate a comprehensive intelligence report
        
        Args:
            aggregated: Aggregated intelligence data
            
        Returns:
            Formatted intelligence report string
        """
        report = []
        
        # Header
        report.append("📊 MULTI-SOURCE INTELLIGENCE REPORT")
        report.append("=" * 50)
        report.append(f"📱 Phone Number: {aggregated.phone_number}")
        report.append(f"🌍 Country Context: {aggregated.country_code}")
        report.append(f"⏱️ Processing Time: {aggregated.processing_time:.2f}s")
        report.append(f"🎯 Overall Confidence: {aggregated.overall_confidence:.1f}% ({self.get_confidence_level(aggregated.overall_confidence).name})")
        report.append("")
        
        # Source Summary
        report.append("📋 SOURCE SUMMARY")
        report.append("-" * 30)
        report.append(f"Total Sources: {aggregated.total_sources}")
        report.append(f"Successful Sources: {aggregated.successful_sources}")
        report.append(f"Success Rate: {(aggregated.successful_sources/aggregated.total_sources)*100:.1f}%")
        report.append(f"Sources Used: {', '.join(aggregated.sources_used)}")
        report.append("")
        
        # Merged Data
        if aggregated.merged_data:
            report.append("🔍 INTELLIGENCE DATA")
            report.append("-" * 30)
            
            # Key fields first
            key_fields = ['is_valid', 'country', 'carrier', 'line_type', 'location', 'operator']
            for field in key_fields:
                if field in aggregated.merged_data:
                    value = aggregated.merged_data[field]
                    confidence = aggregated.merged_data.get(f'{field}_confidence', 0)
                    source = aggregated.merged_data.get(f'{field}_source', 'Unknown')
                    report.append(f"  {field.replace('_', ' ').title()}: {value} (Confidence: {confidence:.1f}%, Source: {source})")
            
            report.append("")
        
        # Individual Source Results
        report.append("📊 INDIVIDUAL SOURCE RESULTS")
        report.append("-" * 40)
        
        for result in aggregated.results:
            status = "✅ SUCCESS" if result.success else "❌ FAILED"
            report.append(f"{result.source.value}: {status} (Confidence: {result.confidence:.1f}%, Time: {result.response_time:.2f}s)")
            
            if result.error:
                report.append(f"  Error: {result.error}")
            elif result.data:
                # Show key data points
                key_data = {k: v for k, v in result.data.items() if k in ['is_valid', 'carrier', 'country', 'line_type'] and v}
                if key_data:
                    report.append(f"  Data: {key_data}")
        
        report.append("")
        
        # Errors
        if aggregated.errors:
            report.append("⚠️ ERRORS ENCOUNTERED")
            report.append("-" * 30)
            for error in aggregated.errors:
                report.append(f"  • {error}")
            report.append("")
        
        # Recommendations
        report.append("💡 RECOMMENDATIONS")
        report.append("-" * 25)
        
        confidence_level = self.get_confidence_level(aggregated.overall_confidence)
        
        if confidence_level == ConfidenceLevel.CRITICAL:
            report.append("  • Data is highly reliable - proceed with confidence")
        elif confidence_level == ConfidenceLevel.HIGH:
            report.append("  • Data is reliable - good for most use cases")
        elif confidence_level == ConfidenceLevel.MEDIUM:
            report.append("  • Data is moderately reliable - verify critical information")
        elif confidence_level == ConfidenceLevel.LOW:
            report.append("  • Data reliability is low - use with caution")
        else:
            report.append("  • Data reliability is very low - manual verification recommended")
        
        if aggregated.successful_sources < 2:
            report.append("  • Consider adding more data sources for better reliability")
        
        if aggregated.errors:
            report.append("  • Some sources failed - check API keys and network connectivity")
        
        return "\n".join(report) 
   
    def _store_historical_data(self, phone_number: str, aggregated: AggregatedIntelligence) -> None:
        """
        Store current investigation data for historical tracking
        
        Args:
            phone_number: Phone number investigated
            aggregated: Aggregated intelligence results
        """
        try:
            # Convert aggregated intelligence to format expected by historical manager
            intelligence_data = {
                'technical_intelligence': {
                    'country_code': aggregated.merged_data.get('country_code', ''),
                    'location': aggregated.merged_data.get('location', ''),
                    'number_type': aggregated.merged_data.get('line_type', ''),
                    'is_valid': aggregated.merged_data.get('is_valid', False),
                    'is_mobile': aggregated.merged_data.get('line_type', '').lower() == 'mobile'
                },
                'carrier_intelligence': {
                    'carrier_name': aggregated.merged_data.get('carrier', '')
                },
                'security_intelligence': {
                    'reputation_score': self._calculate_reputation_score(aggregated.merged_data)
                },
                'social_intelligence': {
                    'whatsapp_presence': aggregated.merged_data.get('whatsapp_presence', False),
                    'telegram_presence': aggregated.merged_data.get('telegram_presence', False)
                },
                'business_intelligence': {
                    'domains': aggregated.merged_data.get('domains_found', []),
                    'business_connections': aggregated.merged_data.get('business_connections', [])
                },
                'api_sources_used': aggregated.sources_used,
                'confidence_score': aggregated.overall_confidence / 100.0,  # Convert to 0-1 scale
                'processing_time': aggregated.processing_time,
                'total_sources': aggregated.total_sources,
                'successful_sources': aggregated.successful_sources,
                'errors': aggregated.errors
            }
            
            # Store in historical database
            self.historical_manager.store_investigation_data(phone_number, intelligence_data)
            
        except Exception as e:
            raise Exception(f"Failed to store historical data: {str(e)}")
    
    def _calculate_reputation_score(self, merged_data: Dict) -> float:
        """
        Calculate reputation score based on available data
        
        Args:
            merged_data: Merged intelligence data
            
        Returns:
            Reputation score between 0.0 and 1.0
        """
        score = 0.5  # Base neutral score
        
        # Adjust based on validation status
        if merged_data.get('is_valid'):
            score += 0.2
        else:
            score -= 0.3
        
        # Adjust based on carrier information availability
        if merged_data.get('carrier'):
            score += 0.1
        
        # Adjust based on business connections
        business_connections = merged_data.get('business_connections', [])
        if business_connections:
            # More business connections might indicate legitimate use
            score += min(len(business_connections) * 0.05, 0.2)
        
        # Adjust based on domain associations
        domains = merged_data.get('domains_found', [])
        if domains:
            # Domain associations can be positive or negative
            active_domains = len([d for d in domains if d.get('status') == 'active'])
            if active_domains > 0:
                score += min(active_domains * 0.03, 0.15)
        
        # Ensure score is within bounds
        return max(0.0, min(1.0, score))
    
    def get_enhanced_intelligence_with_history(self, phone_number: str, country_code: str = 'IN', 
                                             sources: Optional[List[DataSource]] = None) -> Dict:
        """
        Get enhanced intelligence that includes historical analysis
        
        Args:
            phone_number: Phone number to investigate
            country_code: Country context for investigation
            sources: Specific sources to use (None = use all available)
            
        Returns:
            Dict containing current intelligence plus historical analysis
        """
        # Get current intelligence
        current_intelligence = self.aggregate_intelligence(phone_number, country_code, sources)
        
        # Get historical analysis
        historical_data = self.historical_manager.get_historical_data(phone_number)
        change_timeline = self.historical_manager.generate_change_timeline(phone_number)
        porting_analysis = self.historical_manager.detect_number_porting(phone_number)
        ownership_analysis = self.historical_manager.detect_ownership_changes(phone_number)
        confidence_analysis = self.historical_manager.calculate_change_confidence_scoring(phone_number)
        
        # Detect changes if historical data exists
        changes_detected = {}
        if historical_data['total_records'] > 0:
            current_data = {
                'phone_number': phone_number,
                'carrier_name': current_intelligence.merged_data.get('carrier', ''),
                'location': current_intelligence.merged_data.get('location', ''),
                'number_type': current_intelligence.merged_data.get('line_type', ''),
                'is_valid': current_intelligence.merged_data.get('is_valid', False),
                'reputation_score': self._calculate_reputation_score(current_intelligence.merged_data)
            }
            changes_detected = self.historical_manager.detect_changes(current_data, historical_data)
        
        return {
            'phone_number': phone_number,
            'investigation_timestamp': time.time(),
            
            # Current intelligence
            'current_intelligence': {
                'merged_data': current_intelligence.merged_data,
                'overall_confidence': current_intelligence.overall_confidence,
                'sources_used': current_intelligence.sources_used,
                'successful_sources': current_intelligence.successful_sources,
                'total_sources': current_intelligence.total_sources,
                'processing_time': current_intelligence.processing_time,
                'errors': current_intelligence.errors
            },
            
            # Historical analysis
            'historical_analysis': {
                'historical_data': historical_data,
                'change_timeline': change_timeline,
                'changes_detected': changes_detected,
                'porting_analysis': porting_analysis,
                'ownership_analysis': ownership_analysis,
                'confidence_analysis': confidence_analysis
            },
            
            # Enhanced insights
            'enhanced_insights': self._generate_enhanced_insights(
                current_intelligence, historical_data, porting_analysis, ownership_analysis
            ),
            
            # Investigation recommendations
            'investigation_recommendations': self._generate_investigation_recommendations(
                current_intelligence, changes_detected, porting_analysis, ownership_analysis, confidence_analysis
            )
        }
    
    def _generate_enhanced_insights(self, current_intelligence: AggregatedIntelligence, 
                                  historical_data: Dict, porting_analysis: Dict, 
                                  ownership_analysis: Dict) -> Dict:
        """
        Generate enhanced insights based on current and historical data
        
        Args:
            current_intelligence: Current investigation results
            historical_data: Historical investigation data
            porting_analysis: Number porting analysis
            ownership_analysis: Ownership change analysis
            
        Returns:
            Dict containing enhanced insights
        """
        insights = {
            'stability_assessment': 'Unknown',
            'risk_indicators': [],
            'investigation_priority': 'Medium',
            'data_quality': 'Unknown',
            'reliability_score': 0.0
        }
        
        # Assess stability based on historical data
        total_investigations = historical_data.get('metadata', {}).get('total_investigations', 0)
        if total_investigations >= 5:
            insights['stability_assessment'] = 'High - Extensive historical data'
            insights['data_quality'] = 'High'
        elif total_investigations >= 2:
            insights['stability_assessment'] = 'Medium - Some historical data'
            insights['data_quality'] = 'Medium'
        else:
            insights['stability_assessment'] = 'Low - Limited historical data'
            insights['data_quality'] = 'Low'
        
        # Check for risk indicators
        if porting_analysis.get('porting_detected'):
            insights['risk_indicators'].append('Number porting detected')
            insights['investigation_priority'] = 'High'
        
        if ownership_analysis.get('ownership_changes_detected'):
            insights['risk_indicators'].append('Potential ownership changes')
            insights['investigation_priority'] = 'High'
        
        if current_intelligence.overall_confidence < 50:
            insights['risk_indicators'].append('Low confidence in current data')
        
        if current_intelligence.successful_sources < current_intelligence.total_sources * 0.5:
            insights['risk_indicators'].append('High API failure rate')
        
        # Calculate reliability score
        confidence_factor = current_intelligence.overall_confidence / 100.0
        historical_factor = min(total_investigations / 10.0, 1.0)  # Max factor at 10 investigations
        source_factor = current_intelligence.successful_sources / max(current_intelligence.total_sources, 1)
        
        insights['reliability_score'] = (confidence_factor + historical_factor + source_factor) / 3.0
        
        return insights
    
    def _generate_investigation_recommendations(self, current_intelligence: AggregatedIntelligence,
                                              changes_detected: Dict, porting_analysis: Dict,
                                              ownership_analysis: Dict, confidence_analysis: Dict) -> List[str]:
        """
        Generate investigation recommendations based on all available data
        
        Args:
            current_intelligence: Current investigation results
            changes_detected: Detected changes
            porting_analysis: Number porting analysis
            ownership_analysis: Ownership change analysis
            confidence_analysis: Confidence analysis
            
        Returns:
            List of investigation recommendations
        """
        recommendations = []
        
        # Based on current intelligence quality
        if current_intelligence.overall_confidence < 60:
            recommendations.append("Low confidence detected - verify through additional sources")
        
        if current_intelligence.successful_sources < 3:
            recommendations.append("Limited source coverage - consider additional API sources")
        
        # Based on changes detected
        if changes_detected.get('total_changes', 0) > 0:
            recommendations.append(f"Recent changes detected ({changes_detected['total_changes']}) - manual verification recommended")
        
        # Based on porting analysis
        if porting_analysis.get('porting_detected'):
            recommendations.append("Number porting detected - verify current carrier through direct channels")
        
        # Based on ownership analysis
        if ownership_analysis.get('ownership_changes_detected'):
            recommendations.append("Potential ownership changes - consider enhanced verification procedures")
        
        # Based on confidence analysis
        risk_level = confidence_analysis.get('risk_level', 'Unknown')
        if risk_level in ['High Risk', 'Medium Risk']:
            recommendations.append(f"Classified as {risk_level} - implement enhanced monitoring")
        
        # Based on data patterns
        domains = current_intelligence.merged_data.get('domains_found', [])
        if len(domains) > 10:
            recommendations.append("High domain association count - investigate for bulk registration patterns")
        
        related_numbers = current_intelligence.merged_data.get('related_numbers', [])
        if len(related_numbers) > 5:
            recommendations.append("Multiple related numbers found - investigate for coordinated activities")
        
        # Default recommendation if no specific issues found
        if not recommendations:
            recommendations.append("No significant issues detected - continue standard monitoring")
        
        return recommendations
    
    def get_historical_summary(self, phone_number: str) -> Dict:
        """
        Get comprehensive historical summary for a phone number
        
        Args:
            phone_number: Phone number to analyze
            
        Returns:
            Dict containing historical summary
        """
        return self.historical_manager.get_investigation_history_summary(phone_number)
    
    def cleanup_historical_data(self, retention_days: int = 365) -> Dict:
        """
        Clean up old historical data
        
        Args:
            retention_days: Number of days to retain data
            
        Returns:
            Dict containing cleanup results
        """
        return self.historical_manager.cleanup_old_data(retention_days)