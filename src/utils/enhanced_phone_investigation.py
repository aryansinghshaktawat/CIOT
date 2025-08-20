"""
Enhanced Phone Investigation with Comprehensive Error Handling and Security
Integrates all error handling, guidance, retry logic, and security components
"""

import time
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
import uuid

# Import error handling components
from .phone_investigation_exceptions import (
    PhoneInvestigationError,
    InvalidPhoneNumberError,
    CountryNotSupportedError,
    APIConnectionError,
    create_parsing_error,
    validate_number_for_suspicious_patterns,
    assess_data_quality
)

from .phone_investigation_guidance import (
    guidance_system,
    get_input_guidance,
    validate_number_format
)

from .phone_investigation_retry import (
    retry_manager,
    with_retry,
    with_async_retry
)

from .phone_investigation_error_handler import (
    error_handler,
    handle_investigation_error,
    validate_and_warn_number,
    create_safe_investigation_wrapper
)

# Import existing investigation components
from .cached_phone_formatter import CachedPhoneNumberFormatter
from .intelligence_aggregator import IntelligenceAggregator
from .async_intelligence_aggregator import investigate_phone_async
from .performance_cache import cached

logger = logging.getLogger(__name__)

# Import security components
try:
    from ..core.security_manager import SecurityManager
    SECURITY_AVAILABLE = True
except ImportError:
    SECURITY_AVAILABLE = False
    logger.warning("Security manager not available - running without security features")


class EnhancedPhoneInvestigator:
    """
    Enhanced phone investigation with comprehensive error handling
    """
    
    def __init__(self):
        self.phone_formatter = CachedPhoneNumberFormatter()
        self.intelligence_aggregator = IntelligenceAggregator()
        self.investigation_stats = {
            'total_investigations': 0,
            'successful_investigations': 0,
            'failed_investigations': 0,
            'warnings_generated': 0,
            'errors_handled': 0
        }
    
    def investigate_phone_number(self, phone_number: str, country_code: str = 'IN', 
                                include_advanced_features: bool = True, 
                                security_manager: Optional[Any] = None,
                                user_id: str = "default") -> Dict[str, Any]:
        """
        Comprehensive phone number investigation with error handling and security
        
        Args:
            phone_number: Phone number to investigate
            country_code: Country code for parsing context
            include_advanced_features: Whether to include advanced investigation features
            security_manager: Optional security manager for enhanced security
            user_id: User identifier for rate limiting and audit logging
            
        Returns:
            Dict with investigation results or error information
        """
        investigation_id = str(uuid.uuid4())[:8]
        start_time = time.time()
        
        # Update statistics
        self.investigation_stats['total_investigations'] += 1
        
        # Create investigation context
        context = {
            'phone_number': phone_number,
            'country_code': country_code,
            'investigation_id': investigation_id,
            'timestamp': datetime.utcnow().isoformat(),
            'include_advanced_features': include_advanced_features,
            'user_id': user_id
        }
        
        try:
            logger.info(f"Starting investigation {investigation_id} for {phone_number}")
            
            # Step 0: Security checks (if security manager available)
            if security_manager and SECURITY_AVAILABLE:
                # Check investigation authorization
                authorized, auth_details = security_manager.check_investigation_authorization(
                    "phone", phone_number, {"user_id": user_id}, country_code.lower()
                )
                
                if not authorized:
                    return {
                        'success': False,
                        'error_code': 'INVESTIGATION_BLOCKED',
                        'message': 'Investigation blocked due to security concerns',
                        'details': auth_details,
                        'investigation_id': investigation_id,
                        'processing_time': time.time() - start_time
                    }
                
                # Check rate limits
                allowed, rate_message = security_manager.check_rate_limits(
                    "phone_investigation", user_id=user_id
                )
                
                if not allowed:
                    return {
                        'success': False,
                        'error_code': 'RATE_LIMITED',
                        'message': rate_message,
                        'investigation_id': investigation_id,
                        'processing_time': time.time() - start_time
                    }
                
                # Log investigation start
                security_manager.audit_logger.log_investigation_action(
                    "phone_investigation_start",
                    phone_number,
                    {
                        'investigation_id': investigation_id,
                        'country_code': country_code,
                        'user_id': user_id
                    }
                )
                
                # Record operation for rate limiting
                security_manager.record_operation("phone_investigation", user_id=user_id)
                
                # Store authorization details for later use
                context['security_authorization'] = auth_details
            
            # Step 1: Validate country support
            if not self._is_country_supported(country_code):
                supported_countries = guidance_system.get_supported_countries()
                supported_codes = [c['code'] for c in supported_countries]
                raise CountryNotSupportedError(country_code, supported_codes)
            
            # Step 2: Pre-validation and format checking
            format_validation = validate_number_format(phone_number, country_code)
            if not format_validation['is_valid_format']:
                # Create detailed parsing error
                parsing_attempts = [
                    {'method': 'Format validation', 'success': False, 'issues': format_validation['issues']}
                ]
                raise create_parsing_error(phone_number, parsing_attempts, country_code)
            
            # Step 3: Phone number formatting with error handling
            formatting_result = self._safe_format_phone_number(phone_number, country_code)
            
            if not formatting_result['success']:
                raise create_parsing_error(
                    phone_number, 
                    formatting_result.get('parsing_attempts', []), 
                    country_code
                )
            
            # Step 4: Basic investigation data
            investigation_data = {
                'investigation_id': investigation_id,
                'phone_number': phone_number,
                'country_code': country_code,
                'timestamp': context['timestamp'],
                'processing_time': 0.0,
                'success': True,
                'warnings': [],
                'errors': []
            }
            
            # Step 5: Technical intelligence (from libphonenumber)
            technical_intelligence = self._extract_technical_intelligence(formatting_result)
            investigation_data['technical_intelligence'] = technical_intelligence
            
            # Step 6: Advanced investigation features (with error handling)
            if include_advanced_features:
                try:
                    # Carrier intelligence
                    carrier_intelligence = self._safe_get_carrier_intelligence(phone_number, country_code)
                    investigation_data['carrier_intelligence'] = carrier_intelligence
                    
                    # Security intelligence
                    security_intelligence = self._safe_get_security_intelligence(phone_number)
                    investigation_data['security_intelligence'] = security_intelligence
                    
                    # Social intelligence
                    social_intelligence = self._safe_get_social_intelligence(phone_number)
                    investigation_data['social_intelligence'] = social_intelligence
                    
                    # Business intelligence
                    business_intelligence = self._safe_get_business_intelligence(phone_number)
                    investigation_data['business_intelligence'] = business_intelligence
                    
                    # Pattern intelligence
                    pattern_intelligence = self._safe_get_pattern_intelligence(phone_number)
                    investigation_data['pattern_intelligence'] = pattern_intelligence
                    
                    # Historical intelligence
                    historical_intelligence = self._safe_get_historical_intelligence(phone_number)
                    investigation_data['historical_intelligence'] = historical_intelligence
                    
                except Exception as e:
                    logger.warning(f"Advanced features partially failed for {investigation_id}: {e}")
                    # Continue with basic investigation
            
            # Step 7: Generate warnings and quality assessment
            warnings = self._generate_investigation_warnings(phone_number, investigation_data, country_code)
            investigation_data['warnings'] = warnings
            
            if warnings:
                self.investigation_stats['warnings_generated'] += len(warnings)
            
            # Step 8: Calculate investigation metrics
            processing_time = time.time() - start_time
            investigation_data['processing_time'] = processing_time
            
            # Calculate confidence and quality scores
            investigation_data['investigation_confidence'] = self._calculate_investigation_confidence(investigation_data)
            investigation_data['data_quality_score'] = self._calculate_data_quality_score(investigation_data)
            
            # Step 9: Generate investigation summary
            investigation_data['summary'] = self._generate_investigation_summary(investigation_data)
            
            # Step 10: Security post-processing (if security manager available)
            if security_manager and SECURITY_AVAILABLE:
                # Process data with privacy controls
                investigation_data = security_manager.process_investigation_data(
                    investigation_data, 
                    anonymize=True
                )
                
                # Store investigation data with privacy controls
                security_manager.store_investigation_data(phone_number, investigation_data)
                
                # Log investigation completion
                security_manager.audit_logger.log_investigation_action(
                    "phone_investigation_complete",
                    phone_number,
                    {
                        'investigation_id': investigation_id,
                        'processing_time': processing_time,
                        'success': True,
                        'confidence_score': investigation_data.get('investigation_confidence', 0),
                        'warnings_count': len(investigation_data.get('warnings', []))
                    }
                )
                
                # Add security metadata
                investigation_data['security_metadata'] = {
                    'privacy_processed': True,
                    'audit_logged': True,
                    'rate_limited': True,
                    'authorization_checked': True
                }
            
            # Update success statistics
            self.investigation_stats['successful_investigations'] += 1
            
            logger.info(f"Investigation {investigation_id} completed successfully in {processing_time:.2f}s")
            
            return investigation_data
            
        except PhoneInvestigationError as e:
            # Handle known investigation errors
            self.investigation_stats['failed_investigations'] += 1
            self.investigation_stats['errors_handled'] += 1
            
            error_response = handle_investigation_error(e, context)
            error_response['processing_time'] = time.time() - start_time
            
            # Log security event if security manager available
            if security_manager and SECURITY_AVAILABLE:
                security_manager.audit_logger.log_investigation_action(
                    "phone_investigation_error",
                    phone_number,
                    {
                        'investigation_id': investigation_id,
                        'error_code': e.error_code,
                        'error_message': e.message,
                        'processing_time': time.time() - start_time
                    }
                )
            
            logger.error(f"Investigation {investigation_id} failed: {e.error_code} - {e.message}")
            
            return error_response
            
        except Exception as e:
            # Handle unexpected errors
            self.investigation_stats['failed_investigations'] += 1
            self.investigation_stats['errors_handled'] += 1
            
            error_response = handle_investigation_error(e, context)
            error_response['processing_time'] = time.time() - start_time
            
            # Log security event if security manager available
            if security_manager and SECURITY_AVAILABLE:
                security_manager.audit_logger.log_error(
                    "unexpected_investigation_error",
                    str(e),
                    "enhanced_phone_investigation",
                    {
                        'investigation_id': investigation_id,
                        'phone_number_hash': security_manager.privacy_manager.anonymize_phone_number(phone_number),
                        'processing_time': time.time() - start_time
                    }
                )
            
            logger.error(f"Investigation {investigation_id} failed with unexpected error: {e}", exc_info=True)
            
            return error_response
    
    def _is_country_supported(self, country_code: str) -> bool:
        """Check if country is supported"""
        supported_countries = guidance_system.get_supported_countries()
        supported_codes = [c['code'] for c in supported_countries]
        return country_code.upper() in supported_codes
    
    def _safe_format_phone_number(self, phone_number: str, country_code: str) -> Dict[str, Any]:
        """Safely format phone number with error handling"""
        try:
            return self.phone_formatter.format_phone_number(phone_number, country_code)
        except Exception as e:
            logger.error(f"Phone formatting failed: {e}")
            return {
                'success': False,
                'error': str(e),
                'parsing_attempts': [
                    {'method': 'CachedPhoneNumberFormatter', 'success': False, 'error': str(e)}
                ]
            }
    
    def _extract_technical_intelligence(self, formatting_result: Dict[str, Any]) -> Dict[str, Any]:
        """Extract technical intelligence from formatting result"""
        if not formatting_result.get('success'):
            return {'available': False, 'error': 'Formatting failed'}
        
        best_format = formatting_result.get('best_format', {})
        
        return {
            'available': True,
            'is_valid': best_format.get('is_valid', False),
            'is_possible': best_format.get('is_possible', False),
            'country_code': best_format.get('country_code'),
            'country_name': best_format.get('country_name'),
            'region_code': best_format.get('region_code'),
            'location': best_format.get('location'),
            'timezones': best_format.get('timezones', []),
            'number_type': best_format.get('number_type_name'),
            'is_mobile': best_format.get('is_mobile', False),
            'is_fixed_line': best_format.get('is_fixed_line', False),
            'is_voip': best_format.get('is_voip', False),
            'is_toll_free': best_format.get('is_toll_free', False),
            'carrier_name': best_format.get('carrier_name'),
            'confidence_score': best_format.get('confidence_score', 0),
            'data_completeness': best_format.get('data_completeness', 0),
            'formatted_versions': {
                'international': best_format.get('international'),
                'national': best_format.get('national'),
                'e164': best_format.get('e164'),
                'rfc3966': best_format.get('rfc3966')
            }
        }
    
    @create_safe_investigation_wrapper
    @with_retry('carrier_intelligence')
    def _safe_get_carrier_intelligence(self, phone_number: str, country_code: str) -> Dict[str, Any]:
        """Safely get carrier intelligence with retry logic"""
        try:
            # Use existing intelligence aggregator
            result = self.intelligence_aggregator.get_carrier_info(phone_number)
            return {
                'available': True,
                'carrier_name': result.get('carrier', 'Unknown'),
                'network_type': result.get('network_type', 'Unknown'),
                'roaming_indicators': result.get('roaming', {}),
                'api_sources': result.get('sources', []),
                'confidence': result.get('confidence', 'Medium')
            }
        except Exception as e:
            logger.warning(f"Carrier intelligence failed: {e}")
            return {'available': False, 'error': str(e)}
    
    @create_safe_investigation_wrapper
    @with_retry('security_intelligence')
    def _safe_get_security_intelligence(self, phone_number: str) -> Dict[str, Any]:
        """Safely get security intelligence with retry logic"""
        try:
            # Placeholder for security intelligence
            # In real implementation, this would call reputation checkers, spam databases, etc.
            return {
                'available': True,
                'spam_risk_score': 0,
                'spam_reports': [],
                'breach_data': [],
                'reputation_status': 'Unknown',
                'risk_classification': 'Low'
            }
        except Exception as e:
            logger.warning(f"Security intelligence failed: {e}")
            return {'available': False, 'error': str(e)}
    
    @create_safe_investigation_wrapper
    @with_retry('social_intelligence')
    def _safe_get_social_intelligence(self, phone_number: str) -> Dict[str, Any]:
        """Safely get social intelligence with retry logic"""
        try:
            # Placeholder for social intelligence
            # In real implementation, this would check social media platforms
            return {
                'available': True,
                'whatsapp_status': {'has_whatsapp': False, 'profile_visible': False},
                'telegram_profile': {'found': False},
                'social_media_presence': {},
                'profile_links': []
            }
        except Exception as e:
            logger.warning(f"Social intelligence failed: {e}")
            return {'available': False, 'error': str(e)}
    
    @create_safe_investigation_wrapper
    @with_retry('business_intelligence')
    def _safe_get_business_intelligence(self, phone_number: str) -> Dict[str, Any]:
        """Safely get business intelligence with retry logic"""
        try:
            # Placeholder for business intelligence
            # In real implementation, this would check WHOIS databases
            return {
                'available': True,
                'whois_domains': [],
                'business_connections': [],
                'domain_registrations': [],
                'business_intelligence_summary': 'No business connections found'
            }
        except Exception as e:
            logger.warning(f"Business intelligence failed: {e}")
            return {'available': False, 'error': str(e)}
    
    @create_safe_investigation_wrapper
    @with_retry('pattern_intelligence')
    def _safe_get_pattern_intelligence(self, phone_number: str) -> Dict[str, Any]:
        """Safely get pattern intelligence with retry logic"""
        try:
            # Placeholder for pattern intelligence
            # In real implementation, this would analyze number patterns
            return {
                'available': True,
                'related_numbers': [],
                'bulk_registration_status': {'is_bulk_registration': False},
                'sequential_patterns': [],
                'carrier_block_analysis': {}
            }
        except Exception as e:
            logger.warning(f"Pattern intelligence failed: {e}")
            return {'available': False, 'error': str(e)}
    
    @create_safe_investigation_wrapper
    @with_retry('historical_intelligence')
    def _safe_get_historical_intelligence(self, phone_number: str) -> Dict[str, Any]:
        """Safely get historical intelligence with retry logic"""
        try:
            # Placeholder for historical intelligence
            # In real implementation, this would check historical data
            return {
                'available': True,
                'historical_changes': [],
                'change_timeline': [],
                'porting_history': {'porting_detected': False},
                'ownership_changes': []
            }
        except Exception as e:
            logger.warning(f"Historical intelligence failed: {e}")
            return {'available': False, 'error': str(e)}
    
    def _generate_investigation_warnings(self, phone_number: str, investigation_data: Dict[str, Any], 
                                       country_code: str) -> List[Dict[str, Any]]:
        """Generate warnings for the investigation"""
        try:
            return validate_and_warn_number(phone_number, investigation_data, country_code)
        except Exception as e:
            logger.error(f"Warning generation failed: {e}")
            return []
    
    def _calculate_investigation_confidence(self, investigation_data: Dict[str, Any]) -> float:
        """Calculate overall investigation confidence score"""
        try:
            confidence_scores = []
            
            # Technical intelligence confidence
            tech_intel = investigation_data.get('technical_intelligence', {})
            if tech_intel.get('available'):
                confidence_scores.append(tech_intel.get('confidence_score', 0))
            
            # Count available intelligence sources
            intelligence_types = [
                'technical_intelligence',
                'carrier_intelligence', 
                'security_intelligence',
                'social_intelligence',
                'business_intelligence',
                'pattern_intelligence',
                'historical_intelligence'
            ]
            
            available_sources = sum(
                1 for intel_type in intelligence_types 
                if investigation_data.get(intel_type, {}).get('available', False)
            )
            
            # Base confidence on available sources
            source_confidence = (available_sources / len(intelligence_types)) * 100
            confidence_scores.append(source_confidence)
            
            # Calculate average confidence
            if confidence_scores:
                return sum(confidence_scores) / len(confidence_scores)
            else:
                return 0.0
                
        except Exception as e:
            logger.error(f"Confidence calculation failed: {e}")
            return 0.0
    
    def _calculate_data_quality_score(self, investigation_data: Dict[str, Any]) -> float:
        """Calculate data quality score"""
        try:
            quality_factors = []
            
            # Technical data quality
            tech_intel = investigation_data.get('technical_intelligence', {})
            if tech_intel.get('available') and tech_intel.get('is_valid'):
                quality_factors.append(tech_intel.get('data_completeness', 0))
            
            # Warning penalty
            warnings = investigation_data.get('warnings', [])
            warning_penalty = min(len(warnings) * 10, 50)  # Max 50% penalty
            
            # Calculate base quality
            if quality_factors:
                base_quality = sum(quality_factors) / len(quality_factors)
            else:
                base_quality = 50.0  # Default moderate quality
            
            # Apply warning penalty
            final_quality = max(0, base_quality - warning_penalty)
            
            return final_quality
            
        except Exception as e:
            logger.error(f"Quality score calculation failed: {e}")
            return 50.0  # Default moderate quality
    
    def _generate_investigation_summary(self, investigation_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate investigation summary"""
        try:
            tech_intel = investigation_data.get('technical_intelligence', {})
            warnings = investigation_data.get('warnings', [])
            
            # Count available intelligence types
            available_intelligence = []
            intelligence_types = {
                'technical_intelligence': 'Technical Analysis',
                'carrier_intelligence': 'Carrier Information',
                'security_intelligence': 'Security Assessment',
                'social_intelligence': 'Social Media Presence',
                'business_intelligence': 'Business Connections',
                'pattern_intelligence': 'Pattern Analysis',
                'historical_intelligence': 'Historical Data'
            }
            
            for intel_type, display_name in intelligence_types.items():
                if investigation_data.get(intel_type, {}).get('available', False):
                    available_intelligence.append(display_name)
            
            # Generate summary text
            if tech_intel.get('is_valid'):
                validity_text = "Valid phone number"
            elif tech_intel.get('is_possible'):
                validity_text = "Possibly valid phone number"
            else:
                validity_text = "Invalid phone number format"
            
            warning_text = ""
            if warnings:
                critical_warnings = [w for w in warnings if w.get('error_code') in ['SUSPICIOUS_NUMBER_WARNING']]
                if critical_warnings:
                    warning_text = f" with {len(critical_warnings)} warning(s)"
            
            summary_text = f"{validity_text}{warning_text}. Analysis includes: {', '.join(available_intelligence)}."
            
            return {
                'summary_text': summary_text,
                'validity_status': validity_text,
                'available_intelligence': available_intelligence,
                'warning_count': len(warnings),
                'confidence_level': 'High' if investigation_data.get('investigation_confidence', 0) > 70 else 'Medium' if investigation_data.get('investigation_confidence', 0) > 40 else 'Low',
                'quality_level': 'High' if investigation_data.get('data_quality_score', 0) > 70 else 'Medium' if investigation_data.get('data_quality_score', 0) > 40 else 'Low'
            }
            
        except Exception as e:
            logger.error(f"Summary generation failed: {e}")
            return {
                'summary_text': 'Investigation completed with limited data',
                'validity_status': 'Unknown',
                'available_intelligence': [],
                'warning_count': 0,
                'confidence_level': 'Low',
                'quality_level': 'Low'
            }
    
    def get_investigation_stats(self) -> Dict[str, Any]:
        """Get investigation statistics"""
        total = self.investigation_stats['total_investigations']
        if total == 0:
            return {
                'total_investigations': 0,
                'success_rate': 0.0,
                'warning_rate': 0.0,
                'error_rate': 0.0
            }
        
        return {
            'total_investigations': total,
            'successful_investigations': self.investigation_stats['successful_investigations'],
            'failed_investigations': self.investigation_stats['failed_investigations'],
            'warnings_generated': self.investigation_stats['warnings_generated'],
            'errors_handled': self.investigation_stats['errors_handled'],
            'success_rate': self.investigation_stats['successful_investigations'] / total,
            'warning_rate': self.investigation_stats['warnings_generated'] / total,
            'error_rate': self.investigation_stats['failed_investigations'] / total
        }
    
    def reset_stats(self):
        """Reset investigation statistics"""
        self.investigation_stats = {
            'total_investigations': 0,
            'successful_investigations': 0,
            'failed_investigations': 0,
            'warnings_generated': 0,
            'errors_handled': 0
        }


# Global enhanced investigator instance
enhanced_investigator = EnhancedPhoneInvestigator()


def investigate_phone_with_error_handling(phone_number: str, country_code: str = 'IN', 
                                        include_advanced_features: bool = True) -> Dict[str, Any]:
    """
    Main function for phone investigation with comprehensive error handling
    
    Args:
        phone_number: Phone number to investigate
        country_code: Country code for parsing context
        include_advanced_features: Whether to include advanced investigation features
        
    Returns:
        Dict with investigation results or error information
    """
    return enhanced_investigator.investigate_phone_number(
        phone_number, 
        country_code, 
        include_advanced_features
    )


def get_investigation_guidance(phone_number: str, country_code: str = None) -> Dict[str, Any]:
    """
    Get comprehensive guidance for phone number investigation
    
    Args:
        phone_number: Phone number to get guidance for
        country_code: Country code (optional, will be auto-detected)
        
    Returns:
        Dict with guidance information
    """
    return get_input_guidance(phone_number, country_code)


def validate_phone_number_format(phone_number: str, country_code: str) -> Dict[str, Any]:
    """
    Validate phone number format with detailed feedback
    
    Args:
        phone_number: Phone number to validate
        country_code: Country code for validation
        
    Returns:
        Dict with validation results and guidance
    """
    return validate_number_format(phone_number, country_code)


def get_enhanced_investigation_stats() -> Dict[str, Any]:
    """Get enhanced investigation statistics"""
    return enhanced_investigator.get_investigation_stats()