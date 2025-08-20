"""
Asynchronous Intelligence Aggregator
Enhanced multi-source intelligence aggregation with async processing and caching
"""

import asyncio
import time
import threading
from typing import Dict, List, Optional, Any, Tuple, Callable
from dataclasses import dataclass, field
from concurrent.futures import ThreadPoolExecutor, as_completed
import logging

from .performance_cache import (
    cached, AsyncAPIClient, ProgressTracker, 
    performance_optimizer, PerformanceMetrics
)
from .cached_phone_formatter import cached_phone_formatter
from .intelligence_aggregator import (
    IntelligenceResult, AggregatedIntelligence, 
    DataSource, ConfidenceLevel
)

logger = logging.getLogger(__name__)


@dataclass
class AsyncInvestigationTask:
    """Task for asynchronous investigation"""
    source: DataSource
    phone_number: str
    country_code: str
    priority: int = 1
    timeout: float = 30.0
    retry_count: int = 3


class AsyncIntelligenceAggregator:
    """
    Asynchronous intelligence aggregator with performance optimization
    """
    
    def __init__(self, max_concurrent: int = 10, default_timeout: float = 30.0):
        self.max_concurrent = max_concurrent
        self.default_timeout = default_timeout
        
        # Async client for parallel API calls
        self.async_client = AsyncAPIClient(
            max_concurrent=max_concurrent,
            timeout=default_timeout
        )
        
        # Thread pool for CPU-bound tasks
        self.thread_pool = ThreadPoolExecutor(max_workers=5)
        
        # Progress tracking
        self.active_investigations: Dict[str, ProgressTracker] = {}
        self.investigation_lock = threading.Lock()
        
        # Performance metrics
        self.stats = {
            'total_investigations': 0,
            'successful_investigations': 0,
            'failed_investigations': 0,
            'total_processing_time': 0.0,
            'average_sources_per_investigation': 0.0,
            'cache_hit_rate': 0.0
        }
        self.stats_lock = threading.Lock()
    
    @cached("async_phone_investigation", ttl=1800)  # Cache for 30 minutes
    async def investigate_phone_async(
        self, 
        phone_number: str, 
        country_code: str = 'IN',
        sources: Optional[List[DataSource]] = None,
        progress_callback: Optional[Callable[[Dict[str, Any]], None]] = None
    ) -> AggregatedIntelligence:
        """
        Asynchronous phone number investigation with parallel processing
        
        Args:
            phone_number: Phone number to investigate
            country_code: Country context for investigation
            sources: Specific sources to use (None = use all available)
            progress_callback: Callback for progress updates
            
        Returns:
            AggregatedIntelligence with merged data and confidence scores
        """
        start_time = time.time()
        investigation_id = f"{phone_number}_{int(start_time)}"
        
        # Initialize progress tracking
        if sources is None:
            sources = [
                DataSource.LIBPHONENUMBER,
                DataSource.ABSTRACTAPI,
                DataSource.NEUTRINO,
                DataSource.FINDANDTRACE,
                DataSource.WHOIS,
                DataSource.PATTERN_ANALYSIS
            ]
        
        progress_tracker = ProgressTracker(
            total_steps=len(sources) + 2,  # +2 for formatting and merging
            operation_name=f"Phone Investigation: {phone_number}"
        )
        
        if progress_callback:
            progress_tracker.add_callback(progress_callback)
        
        with self.investigation_lock:
            self.active_investigations[investigation_id] = progress_tracker
        
        try:
            # Step 1: Enhanced phone formatting (cached)
            progress_tracker.update("Formatting phone number...")
            formatting_result = await self._async_phone_formatting(phone_number, country_code)
            
            # Step 2: Create investigation tasks
            progress_tracker.update("Preparing investigation tasks...")
            tasks = self._create_investigation_tasks(phone_number, country_code, sources)
            
            # Step 3: Execute tasks in parallel
            results = await self._execute_parallel_investigation(tasks, progress_tracker)
            
            # Step 4: Merge results
            progress_tracker.update("Merging intelligence data...")
            aggregated = self._merge_async_results(
                phone_number, country_code, results, formatting_result
            )
            
            # Update statistics
            processing_time = time.time() - start_time
            aggregated.processing_time = processing_time
            
            with self.stats_lock:
                self.stats['total_investigations'] += 1
                self.stats['successful_investigations'] += 1
                self.stats['total_processing_time'] += processing_time
                self.stats['average_sources_per_investigation'] = (
                    (self.stats['average_sources_per_investigation'] * (self.stats['total_investigations'] - 1) + len(sources)) /
                    self.stats['total_investigations']
                )
            
            progress_tracker.complete()
            
            return aggregated
            
        except Exception as e:
            logger.error(f"Async investigation failed: {e}")
            
            with self.stats_lock:
                self.stats['total_investigations'] += 1
                self.stats['failed_investigations'] += 1
            
            # Return partial results if available
            return AggregatedIntelligence(
                phone_number=phone_number,
                country_code=country_code,
                errors=[str(e)],
                processing_time=time.time() - start_time
            )
            
        finally:
            with self.investigation_lock:
                self.active_investigations.pop(investigation_id, None)
    
    async def _async_phone_formatting(self, phone_number: str, country_code: str) -> Dict[str, Any]:
        """Asynchronous phone number formatting"""
        loop = asyncio.get_event_loop()
        
        # Run phone formatting in thread pool (CPU-bound task)
        formatting_result = await loop.run_in_executor(
            self.thread_pool,
            cached_phone_formatter.format_phone_number,
            phone_number,
            country_code
        )
        
        return formatting_result
    
    def _create_investigation_tasks(
        self, 
        phone_number: str, 
        country_code: str, 
        sources: List[DataSource]
    ) -> List[AsyncInvestigationTask]:
        """Create investigation tasks with priorities"""
        tasks = []
        
        # Priority mapping (higher = more important)
        source_priorities = {
            DataSource.LIBPHONENUMBER: 10,  # Highest priority - local processing
            DataSource.ABSTRACTAPI: 8,     # High priority - reliable API
            DataSource.NEUTRINO: 7,        # Good priority - carrier info
            DataSource.FINDANDTRACE: 6,    # Medium priority - Indian data
            DataSource.WHOIS: 5,           # Lower priority - domain linkage
            DataSource.PATTERN_ANALYSIS: 9 # High priority - algorithmic analysis
        }
        
        for source in sources:
            task = AsyncInvestigationTask(
                source=source,
                phone_number=phone_number,
                country_code=country_code,
                priority=source_priorities.get(source, 1),
                timeout=self._get_source_timeout(source)
            )
            tasks.append(task)
        
        # Sort by priority (highest first)
        tasks.sort(key=lambda x: x.priority, reverse=True)
        
        return tasks
    
    def _get_source_timeout(self, source: DataSource) -> float:
        """Get timeout for specific source"""
        timeouts = {
            DataSource.LIBPHONENUMBER: 5.0,   # Local processing - fast
            DataSource.ABSTRACTAPI: 15.0,    # API call
            DataSource.NEUTRINO: 15.0,       # API call
            DataSource.FINDANDTRACE: 20.0,   # Web scraping - slower
            DataSource.WHOIS: 30.0,          # WHOIS lookups - can be slow
            DataSource.PATTERN_ANALYSIS: 10.0 # Pattern analysis - local processing
        }
        return timeouts.get(source, self.default_timeout)
    
    async def _execute_parallel_investigation(
        self, 
        tasks: List[AsyncInvestigationTask], 
        progress_tracker: ProgressTracker
    ) -> List[IntelligenceResult]:
        """Execute investigation tasks in parallel with progress tracking"""
        results = []
        
        # Group tasks by priority for staged execution
        priority_groups = {}
        for task in tasks:
            if task.priority not in priority_groups:
                priority_groups[task.priority] = []
            priority_groups[task.priority].append(task)
        
        # Execute high-priority tasks first, then lower priority
        for priority in sorted(priority_groups.keys(), reverse=True):
            group_tasks = priority_groups[priority]
            
            # Execute tasks in this priority group concurrently
            async_tasks = [
                self._execute_single_task(task) 
                for task in group_tasks
            ]
            
            group_results = await asyncio.gather(*async_tasks, return_exceptions=True)
            
            # Process results and update progress
            for i, result in enumerate(group_results):
                if isinstance(result, Exception):
                    # Create failed result
                    failed_result = IntelligenceResult(
                        source=group_tasks[i].source,
                        data={},
                        confidence=0.0,
                        timestamp=time.time(),
                        success=False,
                        error=str(result)
                    )
                    results.append(failed_result)
                else:
                    results.append(result)
                
                # Update progress
                progress_tracker.update(f"Completed {group_tasks[i].source.value}")
        
        return results
    
    async def _execute_single_task(self, task: AsyncInvestigationTask) -> IntelligenceResult:
        """Execute a single investigation task"""
        start_time = time.time()
        
        try:
            if task.source == DataSource.LIBPHONENUMBER:
                data, confidence = await self._query_libphonenumber_async(
                    task.phone_number, task.country_code
                )
            elif task.source == DataSource.ABSTRACTAPI:
                data, confidence = await self._query_abstractapi_async(
                    task.phone_number, task.timeout
                )
            elif task.source == DataSource.NEUTRINO:
                data, confidence = await self._query_neutrino_async(
                    task.phone_number, task.country_code, task.timeout
                )
            elif task.source == DataSource.FINDANDTRACE:
                data, confidence = await self._query_findandtrace_async(
                    task.phone_number, task.timeout
                )
            elif task.source == DataSource.WHOIS:
                data, confidence = await self._query_whois_async(
                    task.phone_number, task.timeout
                )
            elif task.source == DataSource.PATTERN_ANALYSIS:
                data, confidence = await self._query_pattern_analysis_async(
                    task.phone_number, task.country_code, task.timeout
                )
            else:
                raise ValueError(f"Unsupported source: {task.source}")
            
            response_time = time.time() - start_time
            
            return IntelligenceResult(
                source=task.source,
                data=data,
                confidence=confidence,
                timestamp=time.time(),
                success=True,
                response_time=response_time
            )
            
        except Exception as e:
            response_time = time.time() - start_time
            
            return IntelligenceResult(
                source=task.source,
                data={},
                confidence=0.0,
                timestamp=time.time(),
                success=False,
                error=str(e),
                response_time=response_time
            )
    
    async def _query_libphonenumber_async(
        self, phone_number: str, country_code: str
    ) -> Tuple[Dict[str, Any], float]:
        """Async libphonenumber query"""
        loop = asyncio.get_event_loop()
        
        # Run in thread pool since libphonenumber is CPU-bound
        result = await loop.run_in_executor(
            self.thread_pool,
            self._query_libphonenumber_sync,
            phone_number,
            country_code
        )
        
        return result
    
    def _query_libphonenumber_sync(
        self, phone_number: str, country_code: str
    ) -> Tuple[Dict[str, Any], float]:
        """Synchronous libphonenumber query"""
        try:
            import phonenumbers
            from phonenumbers import geocoder, carrier, timezone
            
            parsed_number = phonenumbers.parse(phone_number, country_code)
            
            if not phonenumbers.is_valid_number(parsed_number):
                return {}, 20.0
            
            data = {
                'is_valid': phonenumbers.is_valid_number(parsed_number),
                'is_possible': phonenumbers.is_possible_number(parsed_number),
                'country': geocoder.description_for_number(parsed_number, 'en'),
                'country_code': parsed_number.country_code,
                'national_number': parsed_number.national_number,
                'international_format': phonenumbers.format_number(
                    parsed_number, phonenumbers.PhoneNumberFormat.INTERNATIONAL
                ),
                'national_format': phonenumbers.format_number(
                    parsed_number, phonenumbers.PhoneNumberFormat.NATIONAL
                ),
                'e164_format': phonenumbers.format_number(
                    parsed_number, phonenumbers.PhoneNumberFormat.E164
                ),
                'carrier': carrier.name_for_number(parsed_number, 'en'),
                'location': geocoder.description_for_number(parsed_number, 'en'),
                'timezones': timezone.time_zones_for_number(parsed_number),
                'line_type': phonenumbers.number_type(parsed_number).name,
                'region_code': phonenumbers.region_code_for_number(parsed_number)
            }
            
            confidence = 95.0 if data['is_valid'] else 85.0
            return data, confidence
            
        except Exception as e:
            return {'error': str(e)}, 10.0
    
    async def _query_abstractapi_async(
        self, phone_number: str, timeout: float
    ) -> Tuple[Dict[str, Any], float]:
        """Async AbstractAPI query"""
        try:
            from src.utils.osint_utils import load_api_keys
            
            api_keys = load_api_keys()
            if 'abstractapi' not in api_keys:
                return {'error': 'API key not available'}, 0.0
            
            # Format phone number
            import re
            clean_phone = re.sub(r'[^\d+]', '', phone_number)
            if not clean_phone.startswith('+'):
                if len(clean_phone) == 10 and clean_phone[0] in ['6', '7', '8', '9']:
                    clean_phone = f'+91{clean_phone}'
                elif len(clean_phone) == 12 and clean_phone.startswith('91'):
                    clean_phone = f'+{clean_phone}'
            
            url = f"https://phonevalidation.abstractapi.com/v1/?api_key={api_keys['abstractapi']['api_key']}&phone={clean_phone}"
            
            success, response = await self.async_client.make_request('GET', url)
            
            if success and response.get('status_code') == 200:
                data = response['data']
                confidence = 85.0 if data.get('valid') else 40.0
                if data.get('carrier') and data.get('carrier') != 'Unknown':
                    confidence += 10.0
                
                return data, min(confidence, 95.0)
            else:
                error_msg = response.get('error', f"HTTP {response.get('status_code', 'Unknown')}")
                return {'error': error_msg}, 20.0
                
        except Exception as e:
            return {'error': str(e)}, 10.0
    
    async def _query_neutrino_async(
        self, phone_number: str, country_code: str, timeout: float
    ) -> Tuple[Dict[str, Any], float]:
        """Async Neutrino API query"""
        try:
            from src.utils.osint_utils import load_api_keys
            
            api_keys = load_api_keys()
            if 'neutrino' not in api_keys:
                return {'error': 'API key not available'}, 0.0
            
            # Format phone number
            import re
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
            
            success, response = await self.async_client.make_request('POST', url, data=data)
            
            if success and response.get('status_code') == 200:
                result = response['data']
                confidence = 80.0 if result.get('valid') else 30.0
                if result.get('prefix-network'):
                    confidence += 10.0
                
                return result, min(confidence, 90.0)
            else:
                error_msg = response.get('error', f"HTTP {response.get('status_code', 'Unknown')}")
                return {'error': error_msg}, 20.0
                
        except Exception as e:
            return {'error': str(e)}, 10.0
    
    async def _query_findandtrace_async(
        self, phone_number: str, timeout: float
    ) -> Tuple[Dict[str, Any], float]:
        """Async Find and Trace query"""
        loop = asyncio.get_event_loop()
        
        # Run in thread pool since this involves web scraping
        result = await loop.run_in_executor(
            self.thread_pool,
            self._query_findandtrace_sync,
            phone_number
        )
        
        return result
    
    def _query_findandtrace_sync(self, phone_number: str) -> Tuple[Dict[str, Any], float]:
        """Synchronous Find and Trace query"""
        try:
            from src.utils.osint_utils import get_findandtrace_data
            
            import re
            clean_phone = re.sub(r'[^\d]', '', phone_number)
            
            # Only for Indian numbers
            if len(clean_phone) == 10 and clean_phone[0] in ['6', '7', '8', '9']:
                data = get_findandtrace_data(clean_phone)
                
                if data.get('success'):
                    confidence = 70.0
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
    
    async def _query_whois_async(
        self, phone_number: str, timeout: float
    ) -> Tuple[Dict[str, Any], float]:
        """Async WHOIS query"""
        loop = asyncio.get_event_loop()
        
        # Run in thread pool since WHOIS queries can be blocking
        result = await loop.run_in_executor(
            self.thread_pool,
            self._query_whois_sync,
            phone_number
        )
        
        return result
    
    def _query_whois_sync(self, phone_number: str) -> Tuple[Dict[str, Any], float]:
        """Synchronous WHOIS query"""
        try:
            from .whois_checker import WHOISChecker
            
            whois_checker = WHOISChecker()
            whois_result = whois_checker.investigate_phone_whois(phone_number)
            
            if whois_result.total_domains == 0:
                return {'error': 'No domains found'}, 20.0
            
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
                'business_intelligence': whois_checker.generate_business_intelligence_summary(whois_result)
            }
            
            confidence = whois_result.investigation_confidence
            return data, confidence
            
        except Exception as e:
            return {'error': str(e)}, 10.0
    
    async def _query_pattern_analysis_async(
        self, phone_number: str, country_code: str, timeout: float
    ) -> Tuple[Dict[str, Any], float]:
        """Async pattern analysis query"""
        loop = asyncio.get_event_loop()
        
        # Run in thread pool since pattern analysis is CPU-bound
        result = await loop.run_in_executor(
            self.thread_pool,
            self._query_pattern_analysis_sync,
            phone_number,
            country_code
        )
        
        return result
    
    def _query_pattern_analysis_sync(
        self, phone_number: str, country_code: str
    ) -> Tuple[Dict[str, Any], float]:
        """Synchronous pattern analysis query"""
        try:
            from .pattern_analysis import PatternAnalysisEngine
            
            pattern_engine = PatternAnalysisEngine()
            
            related_numbers = pattern_engine.find_related_numbers(phone_number, country_code)
            bulk_registration = pattern_engine.detect_bulk_registration(phone_number, country_code)
            sequential_patterns = pattern_engine.analyze_sequential_patterns(phone_number, country_code)
            carrier_block = pattern_engine.analyze_carrier_block(phone_number, country_code)
            
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
                'investigation_priorities': pattern_engine.suggest_investigation_priorities({
                    'related_numbers': related_numbers,
                    'bulk_registration': bulk_registration,
                    'sequential_patterns': sequential_patterns,
                    'carrier_block': carrier_block
                })
            }
            
            # Calculate confidence
            confidence = 50.0
            
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
    
    def _merge_async_results(
        self, 
        phone_number: str, 
        country_code: str, 
        results: List[IntelligenceResult],
        formatting_result: Dict[str, Any]
    ) -> AggregatedIntelligence:
        """Merge async investigation results"""
        aggregated = AggregatedIntelligence(
            phone_number=phone_number,
            country_code=country_code,
            results=results
        )
        
        # Get successful results
        successful_results = [r for r in results if r.success and r.data]
        aggregated.successful_sources = len(successful_results)
        aggregated.total_sources = len(results)
        aggregated.sources_used = [r.source.value for r in results]
        
        # Collect errors
        aggregated.errors = [r.error for r in results if r.error]
        
        # Merge data using existing logic from intelligence_aggregator
        from .intelligence_aggregator import IntelligenceAggregator
        base_aggregator = IntelligenceAggregator()
        aggregated.merged_data = base_aggregator._merge_intelligence_data(results)
        
        # Calculate overall confidence
        aggregated.overall_confidence = base_aggregator._calculate_overall_confidence(results)
        
        # Add formatting results
        if formatting_result.get('success'):
            aggregated.merged_data['formatting'] = formatting_result
        
        return aggregated
    
    def get_stats(self) -> Dict[str, Any]:
        """Get async aggregator statistics"""
        with self.stats_lock:
            return {
                **self.stats,
                'async_client_stats': self.async_client.get_stats(),
                'active_investigations': len(self.active_investigations)
            }
    
    def get_active_investigations(self) -> Dict[str, Dict[str, Any]]:
        """Get information about active investigations"""
        with self.investigation_lock:
            return {
                inv_id: {
                    'operation_name': tracker.operation_name,
                    'current_step': tracker.current_step,
                    'total_steps': tracker.total_steps,
                    'progress_percent': (tracker.current_step / tracker.total_steps) * 100,
                    'elapsed_time': time.time() - tracker.start_time
                }
                for inv_id, tracker in self.active_investigations.items()
            }
    
    async def shutdown(self):
        """Shutdown async aggregator"""
        self.thread_pool.shutdown(wait=True)


# Global async aggregator instance
async_intelligence_aggregator = AsyncIntelligenceAggregator()


async def investigate_phone_async(
    phone_number: str, 
    country_code: str = 'IN',
    sources: Optional[List[DataSource]] = None,
    progress_callback: Optional[Callable[[Dict[str, Any]], None]] = None
) -> AggregatedIntelligence:
    """
    Asynchronous phone investigation with performance optimization
    
    Args:
        phone_number: Phone number to investigate
        country_code: Country context for investigation
        sources: Specific sources to use
        progress_callback: Callback for progress updates
        
    Returns:
        AggregatedIntelligence with comprehensive investigation results
    """
    return await async_intelligence_aggregator.investigate_phone_async(
        phone_number, country_code, sources, progress_callback
    )


def get_async_aggregator_stats() -> Dict[str, Any]:
    """Get async aggregator statistics"""
    return async_intelligence_aggregator.get_stats()


def get_active_investigations() -> Dict[str, Dict[str, Any]]:
    """Get active investigations status"""
    return async_intelligence_aggregator.get_active_investigations()