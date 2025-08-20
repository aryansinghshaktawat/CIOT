"""
Tests for Phone Investigation Error Handling System
Comprehensive tests for exceptions, guidance, retry logic, and error handling
"""

import pytest
import asyncio
import time
from unittest.mock import Mock, patch, MagicMock
from typing import Dict, Any

# Import the error handling components
from src.utils.phone_investigation_exceptions import (
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

from src.utils.phone_investigation_guidance import (
    PhoneInvestigationGuidanceSystem,
    CountryGuidance,
    guidance_system,
    get_country_guidance,
    get_format_examples,
    get_input_guidance,
    validate_number_format
)

from src.utils.phone_investigation_retry import (
    RetryManager,
    RetryConfig,
    RetryStrategy,
    retry_manager,
    with_retry,
    with_async_retry
)

from src.utils.phone_investigation_error_handler import (
    PhoneInvestigationErrorHandler,
    error_handler,
    handle_investigation_error,
    validate_and_warn_number,
    create_safe_investigation_wrapper
)


class TestPhoneInvestigationExceptions:
    """Test custom exception classes"""
    
    def test_base_exception(self):
        """Test base PhoneInvestigationError"""
        error = PhoneInvestigationError(
            "Test error", 
            "TEST_ERROR", 
            ["Try this", "Try that"]
        )
        
        assert error.message == "Test error"
        assert error.error_code == "TEST_ERROR"
        assert error.suggestions == ["Try this", "Try that"]
        
        error_dict = error.to_dict()
        assert error_dict['error'] is True
        assert error_dict['error_code'] == "TEST_ERROR"
        assert error_dict['message'] == "Test error"
        assert error_dict['suggestions'] == ["Try this", "Try that"]
    
    def test_invalid_phone_number_error(self):
        """Test InvalidPhoneNumberError"""
        error = InvalidPhoneNumberError(
            "1234567890", 
            ["Direct IN format", "Clean digits IN"], 
            "IN"
        )
        
        assert error.phone_number == "1234567890"
        assert error.attempted_formats == ["Direct IN format", "Clean digits IN"]
        assert error.country_code == "IN"
        assert error.error_code == "INVALID_PHONE_FORMAT"
        assert len(error.suggestions) > 0
        assert any("9876543210" in suggestion for suggestion in error.suggestions)
    
    def test_country_not_supported_error(self):
        """Test CountryNotSupportedError"""
        supported = ["IN", "US", "GB"]
        error = CountryNotSupportedError("XX", supported)
        
        assert error.country_code == "XX"
        assert error.supported_countries == supported
        assert error.error_code == "COUNTRY_NOT_SUPPORTED"
        assert any("supported countries" in suggestion for suggestion in error.suggestions)
    
    def test_api_connection_error(self):
        """Test APIConnectionError"""
        error = APIConnectionError("TestAPI", "Connection failed", is_transient=True)
        
        assert error.api_name == "TestAPI"
        assert error.error_message == "Connection failed"
        assert error.is_transient is True
        assert error.error_code == "API_CONNECTION_ERROR"
        assert any("temporary" in suggestion for suggestion in error.suggestions)
    
    def test_rate_limit_exceeded_error(self):
        """Test RateLimitExceededError"""
        error = RateLimitExceededError("TestAPI", retry_after=60)
        
        assert error.api_name == "TestAPI"
        assert error.retry_after == 60
        assert error.error_code == "RATE_LIMIT_EXCEEDED"
        assert any("60 seconds" in suggestion for suggestion in error.suggestions)
    
    def test_suspicious_number_warning(self):
        """Test SuspiciousNumberWarning"""
        reasons = ["Repeated digits pattern", "High spam risk (85%)"]
        error = SuspiciousNumberWarning("9999999999", reasons)
        
        assert error.phone_number == "9999999999"
        assert error.warning_reasons == reasons
        assert error.error_code == "SUSPICIOUS_NUMBER_WARNING"
        assert any("verify" in suggestion.lower() for suggestion in error.suggestions)
    
    def test_data_quality_warning(self):
        """Test DataQualityWarning"""
        issues = ["No carrier information", "Low confidence results"]
        error = DataQualityWarning("9876543210", issues, 35.5)
        
        assert error.phone_number == "9876543210"
        assert error.quality_issues == issues
        assert error.confidence_score == 35.5
        assert error.error_code == "DATA_QUALITY_WARNING"
    
    def test_create_parsing_error(self):
        """Test create_parsing_error helper function"""
        parsing_attempts = [
            {'method': 'Direct IN format', 'success': False, 'error': 'Invalid'},
            {'method': 'Clean digits IN', 'success': False, 'error': 'Invalid'}
        ]
        
        error = create_parsing_error("1234567890", parsing_attempts, "IN")
        
        assert isinstance(error, InvalidPhoneNumberError)
        assert error.phone_number == "1234567890"
        assert error.attempted_formats == ['Direct IN format', 'Clean digits IN']
        assert error.country_code == "IN"
    
    def test_create_api_error(self):
        """Test create_api_error helper function"""
        # Test rate limit error
        error_details = {'status_code': 429, 'message': 'Rate limit exceeded', 'retry_after': 30}
        error = create_api_error("TestAPI", error_details)
        assert isinstance(error, RateLimitExceededError)
        assert error.retry_after == 30
        
        # Test server error
        error_details = {'status_code': 500, 'message': 'Internal server error'}
        error = create_api_error("TestAPI", error_details)
        assert isinstance(error, APIConnectionError)
        assert error.is_transient is True
        
        # Test auth error
        error_details = {'status_code': 401, 'message': 'Unauthorized'}
        error = create_api_error("TestAPI", error_details)
        assert isinstance(error, APIConnectionError)
        assert error.is_transient is False
    
    def test_validate_number_for_suspicious_patterns(self):
        """Test suspicious pattern detection"""
        # Test repeated digits
        warning = validate_number_for_suspicious_patterns("9999999999", {})
        assert warning is not None
        assert "Repeated digits pattern" in warning.warning_reasons
        
        # Test sequential digits
        warning = validate_number_for_suspicious_patterns("1234567890", {})
        assert warning is not None
        assert "Sequential digits pattern" in warning.warning_reasons
        
        # Test high spam risk
        investigation_data = {
            'security_intelligence': {'spam_risk_score': 85}
        }
        warning = validate_number_for_suspicious_patterns("9876543210", investigation_data)
        assert warning is not None
        assert any("High spam risk" in reason for reason in warning.warning_reasons)
        
        # Test normal number
        warning = validate_number_for_suspicious_patterns("9876543210", {})
        assert warning is None
    
    def test_assess_data_quality(self):
        """Test data quality assessment"""
        # Test low quality data
        investigation_data = {
            'technical_intelligence': {'is_valid': False, 'confidence_score': 20},
            'carrier_intelligence': {'carrier_name': ''},
            'api_sources_used': ['source1'],
            'total_sources': 5
        }
        
        warning = assess_data_quality(investigation_data, "9876543210")
        assert warning is not None
        assert "Invalid number format" in warning.quality_issues
        assert "No carrier information" in warning.quality_issues
        assert "Limited API sources available" in warning.quality_issues
        
        # Test good quality data
        investigation_data = {
            'technical_intelligence': {'is_valid': True, 'confidence_score': 85},
            'carrier_intelligence': {'carrier_name': 'Airtel'},
            'api_sources_used': ['source1', 'source2', 'source3'],
            'total_sources': 4
        }
        
        warning = assess_data_quality(investigation_data, "9876543210")
        assert warning is None


class TestPhoneInvestigationGuidance:
    """Test guidance system"""
    
    def test_guidance_system_initialization(self):
        """Test guidance system initialization"""
        system = PhoneInvestigationGuidanceSystem()
        
        assert 'IN' in system.country_guidance
        assert 'US' in system.country_guidance
        assert 'GB' in system.country_guidance
        
        india_guidance = system.country_guidance['IN']
        assert india_guidance.country_code == 'IN'
        assert india_guidance.country_name == 'India'
        assert len(india_guidance.format_examples) > 0
        assert len(india_guidance.validation_tips) > 0
    
    def test_get_country_guidance(self):
        """Test getting country-specific guidance"""
        guidance = get_country_guidance('IN')
        assert guidance is not None
        assert guidance.country_code == 'IN'
        assert guidance.country_name == 'India'
        
        guidance = get_country_guidance('XX')
        assert guidance is None
    
    def test_get_format_examples(self):
        """Test getting format examples"""
        examples = get_format_examples('IN')
        assert len(examples) > 0
        assert any('9876543210' in example for example in examples)
        assert any('+91' in example for example in examples)
        
        examples = get_format_examples('US')
        assert len(examples) > 0
        assert any('555' in example for example in examples)
    
    def test_suggest_country_from_number(self):
        """Test country suggestion from number patterns"""
        system = PhoneInvestigationGuidanceSystem()
        
        # Test Indian numbers
        assert system.suggest_country_from_number('+91 9876543210') == 'IN'
        assert system.suggest_country_from_number('919876543210') == 'IN'
        assert system.suggest_country_from_number('9876543210') == 'IN'
        
        # Test US numbers
        assert system.suggest_country_from_number('+1 555 123 4567') == 'US'
        assert system.suggest_country_from_number('15551234567') == 'US'
        
        # Test UK numbers
        assert system.suggest_country_from_number('+44 20 7946 0958') == 'GB'
        
        # Test unknown pattern
        assert system.suggest_country_from_number('123') is None
    
    def test_validate_number_format(self):
        """Test number format validation"""
        # Test valid Indian number
        result = validate_number_format('9876543210', 'IN')
        assert result['is_valid_format'] is True
        assert len(result['issues']) == 0
        
        # Test invalid Indian number
        result = validate_number_format('1234567890', 'IN')
        assert result['is_valid_format'] is False
        assert len(result['issues']) > 0
        assert any('must start with 6, 7, 8, or 9' in issue for issue in result['issues'])
        
        # Test US number with invalid area code
        result = validate_number_format('0551234567', 'US')
        assert result['is_valid_format'] is False
        assert any('cannot start with 0 or 1' in issue for issue in result['issues'])
        
        # Test UK number with leading zero and country code
        result = validate_number_format('+44 020 7946 0958', 'GB')
        assert result['is_valid_format'] is False
        assert any('Remove leading zero' in issue for issue in result['issues'])
    
    def test_get_input_guidance(self):
        """Test comprehensive input guidance"""
        guidance = get_input_guidance('9876543210', 'IN')
        
        assert guidance['suggested_country'] == 'IN'
        assert guidance['country_name'] == 'India'
        assert len(guidance['format_examples']) > 0
        assert len(guidance['validation_tips']) > 0
        assert len(guidance['carrier_info']) > 0
        
        # Test auto-detection
        guidance = get_input_guidance('+1 555 123 4567')
        assert guidance['suggested_country'] == 'US'


class TestRetryManager:
    """Test retry logic system"""
    
    def test_retry_config(self):
        """Test retry configuration"""
        config = RetryConfig(
            max_attempts=5,
            base_delay=2.0,
            strategy=RetryStrategy.EXPONENTIAL_BACKOFF
        )
        
        assert config.max_attempts == 5
        assert config.base_delay == 2.0
        assert config.strategy == RetryStrategy.EXPONENTIAL_BACKOFF
        assert len(config.retryable_errors) > 0
    
    def test_retry_manager_initialization(self):
        """Test retry manager initialization"""
        manager = RetryManager()
        
        assert 'abstractapi' in manager.api_configs
        assert 'default' in manager.api_configs
        
        config = manager.get_config('abstractapi')
        assert config.max_attempts > 0
        assert config.base_delay > 0
    
    def test_calculate_delay(self):
        """Test delay calculation for different strategies"""
        manager = RetryManager()
        
        # Test exponential backoff
        config = RetryConfig(
            base_delay=1.0,
            strategy=RetryStrategy.EXPONENTIAL_BACKOFF,
            backoff_multiplier=2.0,
            jitter=False
        )
        
        assert manager.calculate_delay(1, config) == 1.0
        assert manager.calculate_delay(2, config) == 2.0
        assert manager.calculate_delay(3, config) == 4.0
        
        # Test linear backoff
        config.strategy = RetryStrategy.LINEAR_BACKOFF
        assert manager.calculate_delay(1, config) == 1.0
        assert manager.calculate_delay(2, config) == 2.0
        assert manager.calculate_delay(3, config) == 3.0
        
        # Test fixed delay
        config.strategy = RetryStrategy.FIXED_DELAY
        assert manager.calculate_delay(1, config) == 1.0
        assert manager.calculate_delay(2, config) == 1.0
        assert manager.calculate_delay(3, config) == 1.0
    
    def test_is_retryable_error(self):
        """Test retryable error detection"""
        manager = RetryManager()
        config = RetryConfig()
        
        # Test retryable errors
        assert manager.is_retryable_error(RateLimitExceededError('test'), config) is True
        assert manager.is_retryable_error(Exception('connection error'), config) is True
        assert manager.is_retryable_error(Exception('timeout occurred'), config) is True
        
        # Test non-retryable errors
        assert manager.is_retryable_error(Exception('invalid input'), config) is False
        assert manager.is_retryable_error(ValueError('bad value'), config) is False
    
    @patch('time.sleep')
    def test_retry_decorator_success(self, mock_sleep):
        """Test retry decorator with successful retry"""
        manager = RetryManager()
        call_count = 0
        
        @manager.retry_with_backoff('test_api')
        def test_function():
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise APIConnectionError('test_api', 'connection error', is_transient=True)
            return {'success': True, 'attempt': call_count}
        
        result = test_function()
        assert result['success'] is True
        assert result['attempt'] == 3
        assert call_count == 3
        assert mock_sleep.call_count == 2  # Two retries
    
    @patch('time.sleep')
    def test_retry_decorator_failure(self, mock_sleep):
        """Test retry decorator with ultimate failure"""
        manager = RetryManager()
        call_count = 0
        
        @manager.retry_with_backoff('test_api')
        def test_function():
            nonlocal call_count
            call_count += 1
            raise APIConnectionError('test_api', 'persistent error', is_transient=True)
        
        with pytest.raises(APIConnectionError):
            test_function()
        
        config = manager.get_config('test_api')
        assert call_count == config.max_attempts
    
    @patch('time.sleep')
    def test_retry_decorator_non_retryable(self, mock_sleep):
        """Test retry decorator with non-retryable error"""
        manager = RetryManager()
        call_count = 0
        
        @manager.retry_with_backoff('test_api')
        def test_function():
            nonlocal call_count
            call_count += 1
            raise ValueError('invalid input')
        
        with pytest.raises(APIConnectionError):  # Converted to API error
            test_function()
        
        assert call_count == 1  # No retries for non-retryable error
        assert mock_sleep.call_count == 0
    
    @pytest.mark.asyncio
    @patch('asyncio.sleep')
    async def test_async_retry_decorator(self, mock_sleep):
        """Test async retry decorator"""
        manager = RetryManager()
        call_count = 0
        
        @manager.async_retry_with_backoff('test_async_api')
        async def test_async_function():
            nonlocal call_count
            call_count += 1
            if call_count < 2:
                raise APIConnectionError('test_async_api', 'async connection error', is_transient=True)
            return {'success': True, 'attempt': call_count}
        
        result = await test_async_function()
        assert result['success'] is True
        assert result['attempt'] == 2
        assert call_count == 2


class TestPhoneInvestigationErrorHandler:
    """Test comprehensive error handler"""
    
    def test_error_handler_initialization(self):
        """Test error handler initialization"""
        handler = PhoneInvestigationErrorHandler()
        
        assert handler.error_stats['total_errors'] == 0
        assert handler.error_stats['parsing_errors'] == 0
        assert handler.error_stats['api_errors'] == 0
    
    def test_handle_investigation_error(self):
        """Test handling PhoneInvestigationError"""
        handler = PhoneInvestigationErrorHandler()
        
        error = InvalidPhoneNumberError('1234567890', ['method1', 'method2'], 'IN')
        context = {
            'phone_number': '1234567890',
            'country_code': 'IN',
            'timestamp': '2024-01-01T00:00:00Z'
        }
        
        response = handler.handle_error(error, context)
        
        assert response['success'] is False
        assert response['error'] is True
        assert response['error_code'] == 'INVALID_PHONE_FORMAT'
        assert response['error_type'] == 'InvalidPhoneNumberError'
        assert response['phone_number'] == '1234567890'
        assert response['country_code'] == 'IN'
        assert len(response['suggestions']) > 0
        assert 'input_guidance' in response
        assert 'format_validation' in response
        assert 'attempted_formats' in response
        
        # Check statistics update
        assert handler.error_stats['total_errors'] == 1
        assert handler.error_stats['parsing_errors'] == 1
    
    def test_handle_api_error(self):
        """Test handling API errors"""
        handler = PhoneInvestigationErrorHandler()
        
        error = APIConnectionError('TestAPI', 'Connection failed', is_transient=True)
        context = {'phone_number': '9876543210', 'country_code': 'IN'}
        
        response = handler.handle_error(error, context)
        
        assert response['error_code'] == 'API_CONNECTION_ERROR'
        assert 'retry_info' in response
        assert response['retry_info']['is_retryable'] is True
        assert response['retry_info']['api_name'] == 'TestAPI'
        
        # Check statistics update
        assert handler.error_stats['api_errors'] == 1
    
    def test_handle_rate_limit_error(self):
        """Test handling rate limit errors"""
        handler = PhoneInvestigationErrorHandler()
        
        error = RateLimitExceededError('TestAPI', retry_after=60)
        context = {'phone_number': '9876543210'}
        
        response = handler.handle_error(error, context)
        
        assert response['error_code'] == 'RATE_LIMIT_EXCEEDED'
        assert 'retry_info' in response
        assert response['retry_info']['retry_after'] == 60
        
        # Check statistics update
        assert handler.error_stats['rate_limit_errors'] == 1
    
    def test_handle_generic_error(self):
        """Test handling generic Python exceptions"""
        handler = PhoneInvestigationErrorHandler()
        
        error = ConnectionError('Network connection failed')
        context = {'phone_number': '9876543210', 'country_code': 'IN'}
        
        response = handler.handle_error(error, context)
        
        assert response['error_code'] == 'API_CONNECTION_ERROR'  # Converted
        assert 'retry_info' in response
        assert response['retry_info']['is_retryable'] is True
    
    def test_validate_and_warn(self):
        """Test validation and warning generation"""
        handler = PhoneInvestigationErrorHandler()
        
        # Test with suspicious number
        warnings = handler.validate_and_warn('9999999999', {}, 'IN')
        assert len(warnings) > 0
        
        # Find suspicious warning
        suspicious_warning = next(
            (w for w in warnings if w.get('error_code') == 'SUSPICIOUS_NUMBER_WARNING'), 
            None
        )
        assert suspicious_warning is not None
        
        # Test with good number and data
        investigation_data = {
            'technical_intelligence': {'is_valid': True, 'confidence_score': 85},
            'carrier_intelligence': {'carrier_name': 'Airtel'},
            'api_sources_used': ['source1', 'source2'],
            'total_sources': 3
        }
        
        warnings = handler.validate_and_warn('9876543210', investigation_data, 'IN')
        # Should have fewer or no warnings for good data
        assert len(warnings) <= 1  # Might have format validation warning
    
    def test_create_safe_wrapper(self):
        """Test safe wrapper creation"""
        handler = PhoneInvestigationErrorHandler()
        
        def test_function(phone_number: str):
            if phone_number == 'fail':
                raise ValueError('Test error')
            return {'success': True, 'phone_number': phone_number}
        
        safe_function = handler.create_safe_wrapper(test_function)
        
        # Test successful call
        result = safe_function('9876543210')
        assert result['success'] is True
        
        # Test error handling
        result = safe_function('fail')
        assert result['success'] is False
        assert result['error'] is True
        assert 'error_code' in result
    
    def test_generate_error_report(self):
        """Test error report generation"""
        handler = PhoneInvestigationErrorHandler()
        
        errors = [
            {
                'error_code': 'INVALID_PHONE_FORMAT',
                'message': 'Invalid format',
                'suggestions': ['Try +91 format', 'Check digits']
            },
            {
                'error_code': 'SUSPICIOUS_NUMBER_WARNING',
                'message': 'Suspicious pattern',
                'suggestions': ['Verify manually', 'Check source']
            },
            {
                'error_code': 'API_CONNECTION_ERROR',
                'message': 'API failed',
                'suggestions': ['Retry later', 'Check connection']
            }
        ]
        
        report = handler.generate_error_report('9876543210', errors)
        
        assert report['phone_number'] == '9876543210'
        assert report['has_errors'] is True
        assert report['error_count'] == 3
        assert 'summary' in report
        assert 'error_categories' in report
        assert len(report['error_categories']['critical']) == 1  # INVALID_PHONE_FORMAT
        assert len(report['error_categories']['warnings']) == 1   # SUSPICIOUS_NUMBER_WARNING
        assert len(report['error_categories']['informational']) == 1  # API_CONNECTION_ERROR
        assert len(report['top_suggestions']) > 0
        assert 'investigation_guidance' in report
    
    def test_error_statistics(self):
        """Test error statistics tracking"""
        handler = PhoneInvestigationErrorHandler()
        
        # Generate some errors
        handler.handle_error(InvalidPhoneNumberError('123', [], 'IN'), {})
        handler.handle_error(APIConnectionError('test', 'error'), {})
        handler.handle_error(RateLimitExceededError('test'), {})
        
        stats = handler.get_error_stats()
        
        assert stats['total_errors'] == 3
        assert stats['error_breakdown']['parsing_errors'] == 1
        assert stats['error_breakdown']['api_errors'] == 1
        assert stats['error_breakdown']['rate_limit_errors'] == 1
        assert stats['error_rates']['parsing_error_rate'] == 1/3
        assert stats['error_rates']['api_error_rate'] == 1/3


class TestIntegration:
    """Integration tests for the complete error handling system"""
    
    def test_complete_error_handling_flow(self):
        """Test complete error handling flow from exception to user response"""
        # Simulate a phone investigation that encounters multiple issues
        phone_number = "1234567890"  # Invalid Indian number
        country_code = "IN"
        
        # Create parsing error
        parsing_attempts = [
            {'method': 'Direct IN format', 'success': False, 'error': 'Invalid'},
            {'method': 'Clean digits IN', 'success': False, 'error': 'Invalid'}
        ]
        parsing_error = create_parsing_error(phone_number, parsing_attempts, country_code)
        
        # Handle the error
        context = {
            'phone_number': phone_number,
            'country_code': country_code,
            'investigation_id': 'test-123'
        }
        
        response = handle_investigation_error(parsing_error, context)
        
        # Verify comprehensive response
        assert response['success'] is False
        assert response['error'] is True
        assert response['error_code'] == 'INVALID_PHONE_FORMAT'
        assert response['phone_number'] == phone_number
        assert response['country_code'] == country_code
        assert response['investigation_id'] == 'test-123'
        
        # Verify guidance is included
        assert 'input_guidance' in response
        assert 'format_validation' in response
        assert 'attempted_formats' in response
        assert 'help' in response
        
        # Verify suggestions are helpful
        assert len(response['suggestions']) > 0
        assert any('9876543210' in suggestion for suggestion in response['suggestions'])
        
        # Verify format validation details
        format_validation = response['format_validation']
        assert format_validation['is_valid_format'] is False
        assert len(format_validation['issues']) > 0
        assert len(format_validation['format_examples']) > 0
    
    def test_warning_system_integration(self):
        """Test integration of warning system with investigation"""
        phone_number = "9999999999"  # Suspicious pattern
        
        # Create investigation data with quality issues
        investigation_data = {
            'technical_intelligence': {'is_valid': True, 'confidence_score': 25},
            'carrier_intelligence': {'carrier_name': ''},
            'security_intelligence': {'spam_risk_score': 90},
            'api_sources_used': ['source1'],
            'total_sources': 5
        }
        
        # Validate and generate warnings
        warnings = validate_and_warn_number(phone_number, investigation_data, 'IN')
        
        # Should have multiple warnings
        assert len(warnings) > 0
        
        # Check for suspicious number warning
        suspicious_warnings = [w for w in warnings if w.get('error_code') == 'SUSPICIOUS_NUMBER_WARNING']
        assert len(suspicious_warnings) > 0
        
        # Check for data quality warning
        quality_warnings = [w for w in warnings if w.get('error_code') == 'DATA_QUALITY_WARNING']
        assert len(quality_warnings) > 0
        
        # Generate comprehensive error report
        report = generate_investigation_error_report(phone_number, warnings)
        
        assert report['has_errors'] is True
        assert report['error_count'] == len(warnings)
        assert 'error_categories' in report
        assert len(report['top_suggestions']) > 0
    
    @patch('time.sleep')
    def test_retry_integration_with_error_handling(self, mock_sleep):
        """Test integration of retry logic with error handling"""
        call_count = 0
        
        @create_safe_investigation_wrapper
        @with_retry('test_integration_api')
        def test_investigation_function(phone_number: str):
            nonlocal call_count
            call_count += 1
            
            if call_count < 3:
                raise APIConnectionError('test_integration_api', 'Temporary failure', is_transient=True)
            
            return {
                'success': True,
                'phone_number': phone_number,
                'attempt': call_count
            }
        
        # Should succeed after retries
        result = test_investigation_function('9876543210')
        assert result['success'] is True
        assert result['attempt'] == 3
        assert call_count == 3
        
        # Reset for failure test
        call_count = 0
        
        @create_safe_investigation_wrapper
        @with_retry('test_integration_api')
        def test_failing_function(phone_number: str):
            nonlocal call_count
            call_count += 1
            raise APIConnectionError('test_integration_api', 'Persistent failure', is_transient=True)
        
        # Should return error response after all retries fail
        result = test_failing_function('9876543210')
        assert result['success'] is False
        assert result['error'] is True
        assert result['error_code'] == 'API_CONNECTION_ERROR'
        assert 'retry_info' in result


if __name__ == '__main__':
    pytest.main([__file__, '-v'])