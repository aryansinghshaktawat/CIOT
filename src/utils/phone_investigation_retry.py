"""
Phone Investigation Retry Logic
Handles transient API failures with intelligent retry strategies
"""

import time
import random
import asyncio
import logging
from typing import Dict, Any, Callable, Optional, List
from functools import wraps
from dataclasses import dataclass
from enum import Enum

from .phone_investigation_exceptions import (
    APIConnectionError, 
    RateLimitExceededError, 
    InvestigationTimeoutError,
    create_api_error
)

logger = logging.getLogger(__name__)


class RetryStrategy(Enum):
    """Retry strategy types"""
    EXPONENTIAL_BACKOFF = "exponential_backoff"
    LINEAR_BACKOFF = "linear_backoff"
    FIXED_DELAY = "fixed_delay"
    IMMEDIATE = "immediate"


@dataclass
class RetryConfig:
    """Configuration for retry behavior"""
    max_attempts: int = 3
    base_delay: float = 1.0
    max_delay: float = 60.0
    strategy: RetryStrategy = RetryStrategy.EXPONENTIAL_BACKOFF
    jitter: bool = True
    backoff_multiplier: float = 2.0
    timeout_seconds: float = 30.0
    retryable_errors: List[str] = None
    
    def __post_init__(self):
        if self.retryable_errors is None:
            self.retryable_errors = [
                'connection',
                'timeout',
                'temporary',
                'service unavailable',
                'internal server error',
                'bad gateway',
                'gateway timeout'
            ]


class RetryManager:
    """
    Manages retry logic for API calls with different strategies
    """
    
    def __init__(self):
        self.api_configs = self._initialize_api_configs()
        self.stats = {
            'total_attempts': 0,
            'successful_retries': 0,
            'failed_retries': 0,
            'rate_limit_hits': 0,
            'timeout_errors': 0
        }
    
    def _initialize_api_configs(self) -> Dict[str, RetryConfig]:
        """Initialize API-specific retry configurations"""
        return {
            'abstractapi': RetryConfig(
                max_attempts=3,
                base_delay=2.0,
                max_delay=30.0,
                strategy=RetryStrategy.EXPONENTIAL_BACKOFF
            ),
            'neutrino': RetryConfig(
                max_attempts=2,
                base_delay=1.5,
                max_delay=20.0,
                strategy=RetryStrategy.EXPONENTIAL_BACKOFF
            ),
            'findandtrace': RetryConfig(
                max_attempts=3,
                base_delay=1.0,
                max_delay=15.0,
                strategy=RetryStrategy.LINEAR_BACKOFF
            ),
            'whois': RetryConfig(
                max_attempts=2,
                base_delay=0.5,
                max_delay=10.0,
                strategy=RetryStrategy.FIXED_DELAY
            ),
            'social_media': RetryConfig(
                max_attempts=2,
                base_delay=3.0,
                max_delay=30.0,
                strategy=RetryStrategy.EXPONENTIAL_BACKOFF
            ),
            'breach_check': RetryConfig(
                max_attempts=3,
                base_delay=2.0,
                max_delay=45.0,
                strategy=RetryStrategy.EXPONENTIAL_BACKOFF
            ),
            'reputation': RetryConfig(
                max_attempts=2,
                base_delay=1.0,
                max_delay=20.0,
                strategy=RetryStrategy.LINEAR_BACKOFF
            ),
            'default': RetryConfig(
                max_attempts=3,
                base_delay=1.0,
                max_delay=30.0,
                strategy=RetryStrategy.EXPONENTIAL_BACKOFF
            )
        }
    
    def get_config(self, api_name: str) -> RetryConfig:
        """Get retry configuration for specific API"""
        return self.api_configs.get(api_name.lower(), self.api_configs['default'])
    
    def calculate_delay(self, attempt: int, config: RetryConfig) -> float:
        """Calculate delay for retry attempt"""
        if config.strategy == RetryStrategy.EXPONENTIAL_BACKOFF:
            delay = config.base_delay * (config.backoff_multiplier ** (attempt - 1))
        elif config.strategy == RetryStrategy.LINEAR_BACKOFF:
            delay = config.base_delay * attempt
        elif config.strategy == RetryStrategy.FIXED_DELAY:
            delay = config.base_delay
        else:  # IMMEDIATE
            delay = 0.0
        
        # Apply maximum delay limit
        delay = min(delay, config.max_delay)
        
        # Add jitter to prevent thundering herd
        if config.jitter and delay > 0:
            jitter_amount = delay * 0.1  # 10% jitter
            delay += random.uniform(-jitter_amount, jitter_amount)
        
        return max(0.0, delay)
    
    def is_retryable_error(self, error: Exception, config: RetryConfig) -> bool:
        """Check if error is retryable based on configuration"""
        error_message = str(error).lower()
        
        # Always retry rate limit errors (with appropriate delay)
        if isinstance(error, RateLimitExceededError):
            return True
        
        # Check for retryable error patterns
        for pattern in config.retryable_errors:
            if pattern.lower() in error_message:
                return True
        
        # Check for specific HTTP status codes if available
        if hasattr(error, 'status_code'):
            # Retry on 5xx server errors and some 4xx errors
            retryable_codes = [429, 500, 502, 503, 504, 520, 521, 522, 523, 524]
            if error.status_code in retryable_codes:
                return True
        
        return False
    
    def retry_with_backoff(self, api_name: str):
        """Decorator for adding retry logic to functions"""
        def decorator(func: Callable):
            @wraps(func)
            def wrapper(*args, **kwargs):
                return self._execute_with_retry(func, api_name, *args, **kwargs)
            return wrapper
        return decorator
    
    def _execute_with_retry(self, func: Callable, api_name: str, *args, **kwargs) -> Any:
        """Execute function with retry logic"""
        config = self.get_config(api_name)
        last_error = None
        
        for attempt in range(1, config.max_attempts + 1):
            try:
                self.stats['total_attempts'] += 1
                
                # Set timeout for the operation
                start_time = time.time()
                result = func(*args, **kwargs)
                
                # Check if operation took too long
                elapsed_time = time.time() - start_time
                if elapsed_time > config.timeout_seconds:
                    raise InvestigationTimeoutError(
                        phone_number=kwargs.get('phone_number', 'unknown'),
                        timeout_seconds=config.timeout_seconds,
                        completed_sources=[api_name]
                    )
                
                # Success - log retry success if this wasn't the first attempt
                if attempt > 1:
                    self.stats['successful_retries'] += 1
                    logger.info(f"API {api_name} succeeded on attempt {attempt}")
                
                return result
                
            except Exception as error:
                last_error = error
                
                # Handle rate limiting specially
                if isinstance(error, RateLimitExceededError):
                    self.stats['rate_limit_hits'] += 1
                    if attempt < config.max_attempts:
                        delay = error.retry_after or config.base_delay * 2
                        logger.warning(f"Rate limit hit for {api_name}, waiting {delay}s")
                        time.sleep(delay)
                        continue
                
                # Handle timeout errors
                if isinstance(error, InvestigationTimeoutError):
                    self.stats['timeout_errors'] += 1
                    logger.error(f"Timeout error for {api_name}: {error}")
                    break  # Don't retry timeout errors
                
                # Check if error is retryable
                if not self.is_retryable_error(error, config):
                    logger.error(f"Non-retryable error for {api_name}: {error}")
                    break
                
                # Calculate delay for next attempt
                if attempt < config.max_attempts:
                    delay = self.calculate_delay(attempt, config)
                    logger.warning(f"API {api_name} failed (attempt {attempt}), retrying in {delay:.1f}s: {error}")
                    time.sleep(delay)
                else:
                    self.stats['failed_retries'] += 1
                    logger.error(f"API {api_name} failed after {config.max_attempts} attempts: {error}")
        
        # All attempts failed - raise the last error
        if isinstance(last_error, (APIConnectionError, RateLimitExceededError, InvestigationTimeoutError)):
            raise last_error
        else:
            # Convert to appropriate API error
            raise create_api_error(api_name, {
                'message': str(last_error),
                'status_code': getattr(last_error, 'status_code', 0)
            })
    
    async def async_retry_with_backoff(self, api_name: str):
        """Async decorator for adding retry logic to async functions"""
        def decorator(func: Callable):
            @wraps(func)
            async def wrapper(*args, **kwargs):
                return await self._execute_async_with_retry(func, api_name, *args, **kwargs)
            return wrapper
        return decorator
    
    async def _execute_async_with_retry(self, func: Callable, api_name: str, *args, **kwargs) -> Any:
        """Execute async function with retry logic"""
        config = self.get_config(api_name)
        last_error = None
        
        for attempt in range(1, config.max_attempts + 1):
            try:
                self.stats['total_attempts'] += 1
                
                # Set timeout for the operation
                start_time = time.time()
                result = await asyncio.wait_for(func(*args, **kwargs), timeout=config.timeout_seconds)
                
                # Success - log retry success if this wasn't the first attempt
                if attempt > 1:
                    self.stats['successful_retries'] += 1
                    logger.info(f"Async API {api_name} succeeded on attempt {attempt}")
                
                return result
                
            except asyncio.TimeoutError:
                last_error = InvestigationTimeoutError(
                    phone_number=kwargs.get('phone_number', 'unknown'),
                    timeout_seconds=config.timeout_seconds,
                    completed_sources=[api_name]
                )
                self.stats['timeout_errors'] += 1
                logger.error(f"Async timeout error for {api_name}")
                break  # Don't retry timeout errors
                
            except Exception as error:
                last_error = error
                
                # Handle rate limiting specially
                if isinstance(error, RateLimitExceededError):
                    self.stats['rate_limit_hits'] += 1
                    if attempt < config.max_attempts:
                        delay = error.retry_after or config.base_delay * 2
                        logger.warning(f"Rate limit hit for async {api_name}, waiting {delay}s")
                        await asyncio.sleep(delay)
                        continue
                
                # Check if error is retryable
                if not self.is_retryable_error(error, config):
                    logger.error(f"Non-retryable error for async {api_name}: {error}")
                    break
                
                # Calculate delay for next attempt
                if attempt < config.max_attempts:
                    delay = self.calculate_delay(attempt, config)
                    logger.warning(f"Async API {api_name} failed (attempt {attempt}), retrying in {delay:.1f}s: {error}")
                    await asyncio.sleep(delay)
                else:
                    self.stats['failed_retries'] += 1
                    logger.error(f"Async API {api_name} failed after {config.max_attempts} attempts: {error}")
        
        # All attempts failed - raise the last error
        if isinstance(last_error, (APIConnectionError, RateLimitExceededError, InvestigationTimeoutError)):
            raise last_error
        else:
            # Convert to appropriate API error
            raise create_api_error(api_name, {
                'message': str(last_error),
                'status_code': getattr(last_error, 'status_code', 0)
            })
    
    def get_stats(self) -> Dict[str, Any]:
        """Get retry statistics"""
        total_attempts = self.stats['total_attempts']
        if total_attempts == 0:
            return {
                'total_attempts': 0,
                'success_rate': 0.0,
                'retry_success_rate': 0.0,
                'rate_limit_rate': 0.0,
                'timeout_rate': 0.0
            }
        
        return {
            'total_attempts': total_attempts,
            'successful_retries': self.stats['successful_retries'],
            'failed_retries': self.stats['failed_retries'],
            'rate_limit_hits': self.stats['rate_limit_hits'],
            'timeout_errors': self.stats['timeout_errors'],
            'success_rate': (total_attempts - self.stats['failed_retries']) / total_attempts,
            'retry_success_rate': self.stats['successful_retries'] / max(1, self.stats['successful_retries'] + self.stats['failed_retries']),
            'rate_limit_rate': self.stats['rate_limit_hits'] / total_attempts,
            'timeout_rate': self.stats['timeout_errors'] / total_attempts
        }
    
    def reset_stats(self):
        """Reset retry statistics"""
        self.stats = {
            'total_attempts': 0,
            'successful_retries': 0,
            'failed_retries': 0,
            'rate_limit_hits': 0,
            'timeout_errors': 0
        }


# Global retry manager instance
retry_manager = RetryManager()


def with_retry(api_name: str):
    """Decorator for adding retry logic to functions"""
    return retry_manager.retry_with_backoff(api_name)


def with_async_retry(api_name: str):
    """Decorator for adding retry logic to async functions"""
    def decorator(func):
        return retry_manager.async_retry_with_backoff(api_name)(func)
    return decorator


def get_retry_stats() -> Dict[str, Any]:
    """Get retry statistics"""
    return retry_manager.get_stats()


def configure_api_retry(api_name: str, config: RetryConfig):
    """Configure retry behavior for specific API"""
    retry_manager.api_configs[api_name.lower()] = config


# Example usage functions for testing retry logic
def create_test_api_call():
    """Create test function for retry logic"""
    @with_retry('test_api')
    def test_api_call(phone_number: str, fail_count: int = 0) -> Dict[str, Any]:
        """Test function for retry logic"""
        if fail_count > 0:
            # Simulate failures
            import random
            if random.random() < 0.7:  # 70% chance of failure
                raise APIConnectionError('test_api', 'Simulated connection error')
        
        return {
            'success': True,
            'phone_number': phone_number,
            'data': 'Test data'
        }
    return test_api_call


def create_test_async_api_call():
    """Create test async function for retry logic"""
    @with_async_retry('test_async_api')
    async def test_async_api_call(phone_number: str, fail_count: int = 0) -> Dict[str, Any]:
        """Test async function for retry logic"""
        if fail_count > 0:
            # Simulate failures
            import random
            if random.random() < 0.7:  # 70% chance of failure
                raise APIConnectionError('test_async_api', 'Simulated async connection error')
        
        # Simulate async work
        await asyncio.sleep(0.1)
        
        return {
            'success': True,
            'phone_number': phone_number,
            'data': 'Test async data'
        }
    return test_async_api_call