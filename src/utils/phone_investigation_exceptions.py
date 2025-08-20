"""
Phone Investigation Exception Classes
Custom exceptions for enhanced phone investigation with user-friendly error handling
"""

from typing import List, Dict, Optional, Any
import phonenumbers


class PhoneInvestigationError(Exception):
    """Base exception for phone investigation errors"""
    
    def __init__(self, message: str, error_code: str = None, suggestions: List[str] = None):
        self.message = message
        self.error_code = error_code or "PHONE_INVESTIGATION_ERROR"
        self.suggestions = suggestions or []
        super().__init__(self.message)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert exception to dictionary for API responses"""
        return {
            'error': True,
            'error_code': self.error_code,
            'message': self.message,
            'suggestions': self.suggestions
        }


class InvalidPhoneNumberError(PhoneInvestigationError):
    """Raised when phone number format is invalid"""
    
    def __init__(self, phone_number: str, attempted_formats: List[str], country_code: str = 'IN'):
        self.phone_number = phone_number
        self.attempted_formats = attempted_formats
        self.country_code = country_code
        
        # Generate country-specific suggestions
        suggestions = self._generate_format_suggestions(country_code)
        
        message = f"Invalid phone number format: '{phone_number}'. Tried {len(attempted_formats)} parsing methods."
        super().__init__(message, "INVALID_PHONE_FORMAT", suggestions)
    
    def _generate_format_suggestions(self, country_code: str) -> List[str]:
        """Generate country-specific format suggestions"""
        format_examples = {
            'IN': [
                "Try: 9876543210 (10-digit mobile)",
                "Try: +91 9876543210 (international format)",
                "Try: 09876543210 (with leading zero)",
                "Try: (+91) 98765-43210 (formatted with brackets)",
                "Ensure the number starts with 6, 7, 8, or 9 for mobile numbers"
            ],
            'US': [
                "Try: (555) 123-4567 (standard US format)",
                "Try: +1 555 123 4567 (international format)",
                "Try: 5551234567 (10-digit format)",
                "Try: 1-555-123-4567 (with country code)",
                "Ensure area code is valid (not starting with 0 or 1)"
            ],
            'GB': [
                "Try: +44 20 7946 0958 (international format)",
                "Try: 020 7946 0958 (national format)",
                "Try: 07911 123456 (mobile format)",
                "Try: +44 7911 123456 (international mobile)",
                "Remove leading zero when using country code"
            ],
            'CA': [
                "Try: (416) 555-0123 (standard Canadian format)",
                "Try: +1 416 555 0123 (international format)",
                "Try: 4165550123 (10-digit format)",
                "Try: 1-416-555-0123 (with country code)"
            ],
            'AU': [
                "Try: +61 4 1234 5678 (international mobile)",
                "Try: 04 1234 5678 (national mobile)",
                "Try: +61 2 9876 5432 (international landline)",
                "Try: (02) 9876 5432 (national landline)"
            ]
        }
        
        return format_examples.get(country_code, format_examples['IN'])


class CountryNotSupportedError(PhoneInvestigationError):
    """Raised when selected country is not supported"""
    
    def __init__(self, country_code: str, supported_countries: List[str]):
        self.country_code = country_code
        self.supported_countries = supported_countries
        
        suggestions = [
            f"Try one of these supported countries: {', '.join(supported_countries[:5])}",
            "Use 'Auto-Detect (Global)' for automatic country detection",
            "Check if your country code is correct (e.g., 'IN' for India, 'US' for United States)"
        ]
        
        message = f"Country '{country_code}' is not supported. Supported countries: {', '.join(supported_countries[:10])}"
        super().__init__(message, "COUNTRY_NOT_SUPPORTED", suggestions)


class APIConnectionError(PhoneInvestigationError):
    """Raised when external API calls fail"""
    
    def __init__(self, api_name: str, error_message: str, is_transient: bool = True):
        self.api_name = api_name
        self.error_message = error_message
        self.is_transient = is_transient
        
        suggestions = []
        if is_transient:
            suggestions.extend([
                "This appears to be a temporary issue. Please try again in a few moments.",
                "Check your internet connection",
                "The service may be experiencing high traffic"
            ])
        else:
            suggestions.extend([
                "This appears to be a configuration issue",
                "Check API key configuration",
                "Verify service availability"
            ])
        
        message = f"API '{api_name}' failed: {error_message}"
        super().__init__(message, "API_CONNECTION_ERROR", suggestions)


class RateLimitExceededError(PhoneInvestigationError):
    """Raised when API rate limits are exceeded"""
    
    def __init__(self, api_name: str, retry_after: Optional[int] = None):
        self.api_name = api_name
        self.retry_after = retry_after
        
        suggestions = [
            f"Rate limit exceeded for {api_name}",
            f"Please wait {retry_after} seconds before trying again" if retry_after else "Please wait before trying again",
            "Consider upgrading your API plan for higher limits",
            "Try investigating a different phone number"
        ]
        
        message = f"Rate limit exceeded for {api_name}"
        if retry_after:
            message += f". Retry after {retry_after} seconds"
        
        super().__init__(message, "RATE_LIMIT_EXCEEDED", suggestions)


class SuspiciousNumberWarning(PhoneInvestigationError):
    """Warning for suspicious or unusual numbers"""
    
    def __init__(self, phone_number: str, warning_reasons: List[str]):
        self.phone_number = phone_number
        self.warning_reasons = warning_reasons
        
        suggestions = [
            "Verify the number with the person directly",
            "Check for recent number porting or changes",
            "Be cautious when contacting this number",
            "Consider additional verification methods"
        ]
        
        message = f"Suspicious number detected: {phone_number}. Reasons: {', '.join(warning_reasons)}"
        super().__init__(message, "SUSPICIOUS_NUMBER_WARNING", suggestions)


class DataQualityWarning(PhoneInvestigationError):
    """Warning for low data quality or incomplete results"""
    
    def __init__(self, phone_number: str, quality_issues: List[str], confidence_score: float):
        self.phone_number = phone_number
        self.quality_issues = quality_issues
        self.confidence_score = confidence_score
        
        suggestions = [
            "Results may be incomplete or inaccurate",
            "Try investigating with a different country selection",
            "Verify results through multiple sources",
            "Consider manual verification methods"
        ]
        
        message = f"Low data quality for {phone_number} (confidence: {confidence_score:.1f}%). Issues: {', '.join(quality_issues)}"
        super().__init__(message, "DATA_QUALITY_WARNING", suggestions)


class InvestigationTimeoutError(PhoneInvestigationError):
    """Raised when investigation takes too long"""
    
    def __init__(self, phone_number: str, timeout_seconds: int, completed_sources: List[str]):
        self.phone_number = phone_number
        self.timeout_seconds = timeout_seconds
        self.completed_sources = completed_sources
        
        suggestions = [
            f"Investigation timed out after {timeout_seconds} seconds",
            f"Partial results available from: {', '.join(completed_sources)}",
            "Try again with fewer investigation sources",
            "Check your internet connection speed"
        ]
        
        message = f"Investigation timeout for {phone_number} after {timeout_seconds}s"
        super().__init__(message, "INVESTIGATION_TIMEOUT", suggestions)


class ConfigurationError(PhoneInvestigationError):
    """Raised when there are configuration issues"""
    
    def __init__(self, config_issue: str, affected_features: List[str]):
        self.config_issue = config_issue
        self.affected_features = affected_features
        
        suggestions = [
            "Check your API key configuration",
            "Verify config/api_keys.json file exists and is valid",
            "Ensure all required API keys are configured",
            "Check the user guide for configuration instructions"
        ]
        
        message = f"Configuration error: {config_issue}. Affected features: {', '.join(affected_features)}"
        super().__init__(message, "CONFIGURATION_ERROR", suggestions)


class NumberTypeNotSupportedError(PhoneInvestigationError):
    """Raised when number type is not supported for certain operations"""
    
    def __init__(self, phone_number: str, number_type: str, operation: str):
        self.phone_number = phone_number
        self.number_type = number_type
        self.operation = operation
        
        suggestions = [
            f"Operation '{operation}' is not supported for {number_type} numbers",
            "Try with a mobile number for full investigation features",
            "Some features are limited for landline/VoIP numbers",
            "Basic information is still available"
        ]
        
        message = f"Number type '{number_type}' not supported for operation '{operation}'"
        super().__init__(message, "NUMBER_TYPE_NOT_SUPPORTED", suggestions)


def create_parsing_error(phone_number: str, parsing_attempts: List[Dict], country_code: str = 'IN') -> InvalidPhoneNumberError:
    """
    Create a comprehensive parsing error with detailed information
    
    Args:
        phone_number: The phone number that failed to parse
        parsing_attempts: List of parsing attempts with results
        country_code: Country code used for parsing
        
    Returns:
        InvalidPhoneNumberError with detailed information
    """
    attempted_formats = [attempt.get('method', 'Unknown') for attempt in parsing_attempts]
    return InvalidPhoneNumberError(phone_number, attempted_formats, country_code)


def create_api_error(api_name: str, error_details: Dict) -> PhoneInvestigationError:
    """
    Create appropriate API error based on error details
    
    Args:
        api_name: Name of the API that failed
        error_details: Dictionary with error information
        
    Returns:
        Appropriate PhoneInvestigationError subclass
    """
    status_code = error_details.get('status_code', 0)
    error_message = error_details.get('message', 'Unknown error')
    
    # Rate limit errors
    if status_code == 429:
        retry_after = error_details.get('retry_after')
        return RateLimitExceededError(api_name, retry_after)
    
    # Transient errors (5xx, connection issues)
    if status_code >= 500 or 'connection' in error_message.lower() or 'timeout' in error_message.lower():
        return APIConnectionError(api_name, error_message, is_transient=True)
    
    # Configuration errors (401, 403)
    if status_code in [401, 403]:
        return APIConnectionError(api_name, f"Authentication failed: {error_message}", is_transient=False)
    
    # General API error
    return APIConnectionError(api_name, error_message, is_transient=False)


def validate_number_for_suspicious_patterns(phone_number: str, investigation_data: Dict) -> Optional[SuspiciousNumberWarning]:
    """
    Check for suspicious patterns in phone number and investigation data
    
    Args:
        phone_number: Phone number to check
        investigation_data: Investigation results
        
    Returns:
        SuspiciousNumberWarning if suspicious patterns detected, None otherwise
    """
    warning_reasons = []
    
    # Check for suspicious patterns
    clean_number = ''.join(filter(str.isdigit, phone_number))
    
    # Repeated digits (e.g., 9999999999)
    if len(set(clean_number)) <= 2 and len(clean_number) >= 8:
        warning_reasons.append("Repeated digits pattern")
    
    # Sequential numbers (e.g., 1234567890)
    if len(clean_number) >= 8:
        is_sequential = all(
            int(clean_number[i]) == int(clean_number[i-1]) + 1 
            for i in range(1, min(6, len(clean_number)))
        )
        if is_sequential:
            warning_reasons.append("Sequential digits pattern")
    
    # Check investigation data for suspicious indicators
    if investigation_data:
        # High spam risk
        spam_risk = investigation_data.get('security_intelligence', {}).get('spam_risk_score', 0)
        if spam_risk > 70:
            warning_reasons.append(f"High spam risk ({spam_risk}%)")
        
        # Multiple breach incidents
        breach_count = len(investigation_data.get('security_intelligence', {}).get('breach_data', []))
        if breach_count > 3:
            warning_reasons.append(f"Multiple data breaches ({breach_count})")
        
        # Bulk registration indicators
        bulk_status = investigation_data.get('pattern_intelligence', {}).get('bulk_registration_status', {})
        if bulk_status.get('is_bulk_registration', False):
            warning_reasons.append("Bulk registration detected")
    
    if warning_reasons:
        return SuspiciousNumberWarning(phone_number, warning_reasons)
    
    return None


def assess_data_quality(investigation_data: Dict, phone_number: str) -> Optional[DataQualityWarning]:
    """
    Assess data quality and create warning if quality is low
    
    Args:
        investigation_data: Investigation results
        phone_number: Phone number investigated
        
    Returns:
        DataQualityWarning if quality is low, None otherwise
    """
    quality_issues = []
    confidence_scores = []
    
    # Check technical intelligence quality
    tech_intel = investigation_data.get('technical_intelligence', {})
    if not tech_intel.get('is_valid', False):
        quality_issues.append("Invalid number format")
    
    tech_confidence = tech_intel.get('confidence_score', 0)
    confidence_scores.append(tech_confidence)
    
    # Check carrier intelligence quality
    carrier_intel = investigation_data.get('carrier_intelligence', {})
    if not carrier_intel.get('carrier_name'):
        quality_issues.append("No carrier information")
    
    # Check API source availability
    api_sources = investigation_data.get('api_sources_used', [])
    total_sources = investigation_data.get('total_sources', 1)
    
    if len(api_sources) < total_sources * 0.5:
        quality_issues.append("Limited API sources available")
    
    # Calculate overall confidence
    if confidence_scores:
        overall_confidence = sum(confidence_scores) / len(confidence_scores)
    else:
        overall_confidence = 0
    
    # Add confidence-based issues
    if overall_confidence < 30:
        quality_issues.append("Very low confidence results")
    elif overall_confidence < 50:
        quality_issues.append("Low confidence results")
    
    # Create warning if quality issues exist
    if quality_issues and overall_confidence < 60:
        return DataQualityWarning(phone_number, quality_issues, overall_confidence)
    
    return None