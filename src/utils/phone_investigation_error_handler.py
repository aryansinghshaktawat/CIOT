"""
Phone Investigation Error Handler
Comprehensive error handling system that integrates exceptions, guidance, and retry logic
"""

import logging
import traceback
from typing import Dict, Any, Optional, List, Callable
from functools import wraps

from .phone_investigation_exceptions import (
    PhoneInvestigationError,
    InvalidPhoneNumberError,
    CountryNotSupportedError,
    APIConnectionError,
    RateLimitExceededError,
    SuspiciousNumberWarning,
    DataQualityWarning,
    InvestigationTimeoutError,
    ConfigurationError,
    NumberTypeNotSupportedError,
    create_parsing_error,
    create_api_error,
    validate_number_for_suspicious_patterns,
    assess_data_quality
)

from .phone_investigation_guidance import (
    guidance_system,
    get_error_help,
    get_input_guidance,
    validate_number_format
)

from .phone_investigation_retry import retry_manager

logger = logging.getLogger(__name__)


class PhoneInvestigationErrorHandler:
    """
    Comprehensive error handler for phone investigation operations
    """
    
    def __init__(self):
        self.error_stats = {
            'total_errors': 0,
            'parsing_errors': 0,
            'api_errors': 0,
            'configuration_errors': 0,
            'timeout_errors': 0,
            'rate_limit_errors': 0,
            'suspicious_warnings': 0,
            'quality_warnings': 0
        }
    
    def handle_error(self, error: Exception, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Handle any error and return user-friendly response
        
        Args:
            error: Exception that occurred
            context: Additional context information
            
        Returns:
            Dict with error information and user guidance
        """
        context = context or {}
        phone_number = context.get('phone_number', 'unknown')
        country_code = context.get('country_code', 'IN')
        
        # Update error statistics
        self.error_stats['total_errors'] += 1
        
        # Handle specific error types
        if isinstance(error, PhoneInvestigationError):
            return self._handle_investigation_error(error, context)
        elif isinstance(error, Exception):
            return self._handle_generic_error(error, context)
        else:
            return self._create_unknown_error_response(error, context)
    
    def _handle_investigation_error(self, error: PhoneInvestigationError, context: Dict[str, Any]) -> Dict[str, Any]:
        """Handle PhoneInvestigationError and its subclasses"""
        phone_number = context.get('phone_number', 'unknown')
        country_code = context.get('country_code', 'IN')
        
        # Update specific error statistics
        if isinstance(error, InvalidPhoneNumberError):
            self.error_stats['parsing_errors'] += 1
        elif isinstance(error, APIConnectionError):
            self.error_stats['api_errors'] += 1
        elif isinstance(error, RateLimitExceededError):
            self.error_stats['rate_limit_errors'] += 1
        elif isinstance(error, InvestigationTimeoutError):
            self.error_stats['timeout_errors'] += 1
        elif isinstance(error, ConfigurationError):
            self.error_stats['configuration_errors'] += 1
        elif isinstance(error, SuspiciousNumberWarning):
            self.error_stats['suspicious_warnings'] += 1
        elif isinstance(error, DataQualityWarning):
            self.error_stats['quality_warnings'] += 1
        
        # Get error-specific help
        error_help = get_error_help(error.error_code)
        
        # Get input guidance for the phone number
        input_guidance = get_input_guidance(phone_number, country_code)
        
        # Create comprehensive error response
        response = {
            'success': False,
            'error': True,
            'error_code': error.error_code,
            'error_type': type(error).__name__,
            'message': error.message,
            'phone_number': phone_number,
            'country_code': country_code,
            'suggestions': error.suggestions,
            'timestamp': context.get('timestamp'),
            'investigation_id': context.get('investigation_id')
        }
        
        # Add error-specific help if available
        if error_help:
            response['help'] = error_help
        
        # Add input guidance for parsing errors
        if isinstance(error, InvalidPhoneNumberError):
            response['input_guidance'] = input_guidance
            response['format_validation'] = validate_number_format(phone_number, country_code)
            response['attempted_formats'] = error.attempted_formats
        
        # Add retry information for API errors
        if isinstance(error, (APIConnectionError, RateLimitExceededError)):
            response['retry_info'] = {
                'is_retryable': isinstance(error, APIConnectionError) and error.is_transient,
                'retry_after': getattr(error, 'retry_after', None),
                'api_name': getattr(error, 'api_name', 'unknown')
            }
        
        # Add timeout information
        if isinstance(error, InvestigationTimeoutError):
            response['timeout_info'] = {
                'timeout_seconds': error.timeout_seconds,
                'completed_sources': error.completed_sources,
                'partial_results_available': len(error.completed_sources) > 0
            }
        
        # Add configuration guidance
        if isinstance(error, ConfigurationError):
            response['configuration_help'] = {
                'affected_features': error.affected_features,
                'config_file_path': 'config/api_keys.json',
                'documentation_link': 'docs/user_guide.md#api-configuration'
            }
        
        # Log the error
        logger.error(f"Phone investigation error: {error.error_code} - {error.message}", 
                    extra={'phone_number': phone_number, 'country_code': country_code})
        
        return response
    
    def _handle_generic_error(self, error: Exception, context: Dict[str, Any]) -> Dict[str, Any]:
        """Handle generic Python exceptions"""
        phone_number = context.get('phone_number', 'unknown')
        country_code = context.get('country_code', 'IN')
        
        # Try to convert to appropriate investigation error
        error_message = str(error)
        error_type = type(error).__name__
        
        # Check for common error patterns
        if 'connection' in error_message.lower() or 'network' in error_message.lower():
            investigation_error = APIConnectionError('unknown', error_message, is_transient=True)
            return self._handle_investigation_error(investigation_error, context)
        
        elif 'timeout' in error_message.lower():
            investigation_error = InvestigationTimeoutError(phone_number, 30, [])
            return self._handle_investigation_error(investigation_error, context)
        
        elif 'rate limit' in error_message.lower() or '429' in error_message:
            investigation_error = RateLimitExceededError('unknown')
            return self._handle_investigation_error(investigation_error, context)
        
        # Generic error response
        response = {
            'success': False,
            'error': True,
            'error_code': 'GENERIC_ERROR',
            'error_type': error_type,
            'message': f'An unexpected error occurred: {error_message}',
            'phone_number': phone_number,
            'country_code': country_code,
            'suggestions': [
                'Please try again in a few moments',
                'Check your internet connection',
                'Verify the phone number format',
                'Contact support if the issue persists'
            ],
            'timestamp': context.get('timestamp'),
            'investigation_id': context.get('investigation_id')
        }
        
        # Add input guidance
        response['input_guidance'] = get_input_guidance(phone_number, country_code)
        
        # Log the error with stack trace
        logger.error(f"Generic error in phone investigation: {error_type} - {error_message}", 
                    extra={'phone_number': phone_number, 'country_code': country_code},
                    exc_info=True)
        
        return response
    
    def _create_unknown_error_response(self, error: Any, context: Dict[str, Any]) -> Dict[str, Any]:
        """Create response for unknown error types"""
        phone_number = context.get('phone_number', 'unknown')
        country_code = context.get('country_code', 'IN')
        
        response = {
            'success': False,
            'error': True,
            'error_code': 'UNKNOWN_ERROR',
            'error_type': 'Unknown',
            'message': f'An unknown error occurred: {str(error)}',
            'phone_number': phone_number,
            'country_code': country_code,
            'suggestions': [
                'Please try again',
                'Contact support with error details',
                'Check system logs for more information'
            ],
            'timestamp': context.get('timestamp'),
            'investigation_id': context.get('investigation_id')
        }
        
        logger.error(f"Unknown error in phone investigation: {str(error)}", 
                    extra={'phone_number': phone_number, 'country_code': country_code})
        
        return response
    
    def validate_and_warn(self, phone_number: str, investigation_data: Dict[str, Any] = None, 
                         country_code: str = 'IN') -> List[Dict[str, Any]]:
        """
        Validate phone number and generate warnings
        
        Args:
            phone_number: Phone number to validate
            investigation_data: Investigation results (optional)
            country_code: Country code for validation
            
        Returns:
            List of warnings and validation issues
        """
        warnings = []
        
        # Check for suspicious patterns
        suspicious_warning = validate_number_for_suspicious_patterns(phone_number, investigation_data or {})
        if suspicious_warning:
            warnings.append(self._handle_investigation_error(suspicious_warning, {
                'phone_number': phone_number,
                'country_code': country_code
            }))
        
        # Check data quality if investigation data is available
        if investigation_data:
            quality_warning = assess_data_quality(investigation_data, phone_number)
            if quality_warning:
                warnings.append(self._handle_investigation_error(quality_warning, {
                    'phone_number': phone_number,
                    'country_code': country_code
                }))
        
        # Validate number format
        format_validation = validate_number_format(phone_number, country_code)
        if not format_validation['is_valid_format']:
            parsing_error = InvalidPhoneNumberError(
                phone_number, 
                ['format_validation'], 
                country_code
            )
            warnings.append(self._handle_investigation_error(parsing_error, {
                'phone_number': phone_number,
                'country_code': country_code
            }))
        
        return warnings
    
    def create_safe_wrapper(self, func: Callable, api_name: str = None) -> Callable:
        """
        Create a safe wrapper for functions that handles all errors
        
        Args:
            func: Function to wrap
            api_name: API name for retry logic (optional)
            
        Returns:
            Wrapped function with error handling
        """
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                # Add retry logic if API name is provided
                if api_name:
                    retry_decorator = retry_manager.retry_with_backoff(api_name)
                    func_with_retry = retry_decorator(func)
                    return func_with_retry(*args, **kwargs)
                else:
                    return func(*args, **kwargs)
                    
            except Exception as error:
                # Extract context from kwargs
                context = {
                    'phone_number': kwargs.get('phone_number', args[0] if args else 'unknown'),
                    'country_code': kwargs.get('country_code', 'IN'),
                    'api_name': api_name,
                    'function_name': func.__name__
                }
                
                return self.handle_error(error, context)
        
        return wrapper
    
    def get_error_stats(self) -> Dict[str, Any]:
        """Get error statistics"""
        total_errors = self.error_stats['total_errors']
        if total_errors == 0:
            return {
                'total_errors': 0,
                'error_breakdown': {},
                'error_rates': {}
            }
        
        return {
            'total_errors': total_errors,
            'error_breakdown': {
                'parsing_errors': self.error_stats['parsing_errors'],
                'api_errors': self.error_stats['api_errors'],
                'configuration_errors': self.error_stats['configuration_errors'],
                'timeout_errors': self.error_stats['timeout_errors'],
                'rate_limit_errors': self.error_stats['rate_limit_errors'],
                'suspicious_warnings': self.error_stats['suspicious_warnings'],
                'quality_warnings': self.error_stats['quality_warnings']
            },
            'error_rates': {
                'parsing_error_rate': self.error_stats['parsing_errors'] / total_errors,
                'api_error_rate': self.error_stats['api_errors'] / total_errors,
                'configuration_error_rate': self.error_stats['configuration_errors'] / total_errors,
                'timeout_error_rate': self.error_stats['timeout_errors'] / total_errors,
                'rate_limit_error_rate': self.error_stats['rate_limit_errors'] / total_errors
            }
        }
    
    def reset_stats(self):
        """Reset error statistics"""
        self.error_stats = {
            'total_errors': 0,
            'parsing_errors': 0,
            'api_errors': 0,
            'configuration_errors': 0,
            'timeout_errors': 0,
            'rate_limit_errors': 0,
            'suspicious_warnings': 0,
            'quality_warnings': 0
        }
    
    def generate_error_report(self, phone_number: str, errors: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Generate comprehensive error report for investigation
        
        Args:
            phone_number: Phone number that was investigated
            errors: List of errors that occurred
            
        Returns:
            Comprehensive error report
        """
        if not errors:
            return {
                'phone_number': phone_number,
                'has_errors': False,
                'error_count': 0,
                'summary': 'Investigation completed successfully'
            }
        
        # Categorize errors
        error_categories = {
            'critical': [],
            'warnings': [],
            'informational': []
        }
        
        for error in errors:
            error_code = error.get('error_code', '')
            if error_code in ['INVALID_PHONE_FORMAT', 'COUNTRY_NOT_SUPPORTED', 'CONFIGURATION_ERROR']:
                error_categories['critical'].append(error)
            elif error_code in ['SUSPICIOUS_NUMBER_WARNING', 'DATA_QUALITY_WARNING']:
                error_categories['warnings'].append(error)
            else:
                error_categories['informational'].append(error)
        
        # Generate summary
        summary_parts = []
        if error_categories['critical']:
            summary_parts.append(f"{len(error_categories['critical'])} critical error(s)")
        if error_categories['warnings']:
            summary_parts.append(f"{len(error_categories['warnings'])} warning(s)")
        if error_categories['informational']:
            summary_parts.append(f"{len(error_categories['informational'])} informational message(s)")
        
        summary = f"Investigation completed with {', '.join(summary_parts)}"
        
        # Get most relevant suggestions
        all_suggestions = []
        for error in errors:
            all_suggestions.extend(error.get('suggestions', []))
        
        # Remove duplicates while preserving order
        unique_suggestions = []
        seen = set()
        for suggestion in all_suggestions:
            if suggestion not in seen:
                unique_suggestions.append(suggestion)
                seen.add(suggestion)
        
        return {
            'phone_number': phone_number,
            'has_errors': True,
            'error_count': len(errors),
            'summary': summary,
            'error_categories': error_categories,
            'top_suggestions': unique_suggestions[:5],  # Top 5 suggestions
            'all_errors': errors,
            'investigation_guidance': get_input_guidance(phone_number)
        }


# Global error handler instance
error_handler = PhoneInvestigationErrorHandler()


def handle_investigation_error(error: Exception, context: Dict[str, Any] = None) -> Dict[str, Any]:
    """Handle investigation error with comprehensive response"""
    return error_handler.handle_error(error, context)


def validate_and_warn_number(phone_number: str, investigation_data: Dict[str, Any] = None, 
                           country_code: str = 'IN') -> List[Dict[str, Any]]:
    """Validate phone number and generate warnings"""
    return error_handler.validate_and_warn(phone_number, investigation_data, country_code)


def create_safe_investigation_wrapper(func: Callable, api_name: str = None) -> Callable:
    """Create safe wrapper for investigation functions"""
    return error_handler.create_safe_wrapper(func, api_name)


def get_error_statistics() -> Dict[str, Any]:
    """Get error handling statistics"""
    return error_handler.get_error_stats()


def generate_investigation_error_report(phone_number: str, errors: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Generate comprehensive error report"""
    return error_handler.generate_error_report(phone_number, errors)