#!/usr/bin/env python3
"""
Rate Limiter for CIOT
Prevents abuse of investigation features with configurable limits
"""

import time
import json
import threading
from pathlib import Path
from collections import defaultdict, deque
from datetime import datetime, timedelta
import logging

class RateLimiter:
    """Rate limiting system for API calls and investigations"""
    
    def __init__(self, config_dir="config"):
        self.config_dir = Path(config_dir)
        self.config_dir.mkdir(exist_ok=True)
        self.rate_limits_file = self.config_dir / "rate_limits.json"
        self.logger = logging.getLogger('CIOT_RateLimit')
        
        # Thread-safe storage for rate limiting data
        self._lock = threading.Lock()
        self._request_history = defaultdict(deque)
        self._blocked_until = defaultdict(float)
        
        # Load rate limiting configuration
        self.limits = self._load_rate_limits()
        
        # Start cleanup thread
        self._start_cleanup_thread()
    
    def _load_rate_limits(self):
        """Load rate limiting configuration"""
        default_limits = {
            "phone_investigation": {
                "requests_per_minute": 10,
                "requests_per_hour": 100,
                "requests_per_day": 500,
                "burst_limit": 5,
                "cooldown_seconds": 60
            },
            "api_calls": {
                "abstractapi": {
                    "requests_per_minute": 5,
                    "requests_per_hour": 50,
                    "requests_per_day": 200
                },
                "neutrino": {
                    "requests_per_minute": 10,
                    "requests_per_hour": 100,
                    "requests_per_day": 1000
                },
                "numverify": {
                    "requests_per_minute": 2,
                    "requests_per_hour": 20,
                    "requests_per_day": 100
                },
                "telnyx": {
                    "requests_per_minute": 1,
                    "requests_per_hour": 10,
                    "requests_per_day": 50
                }
            },
            "social_media_search": {
                "requests_per_minute": 5,
                "requests_per_hour": 30,
                "requests_per_day": 100
            },
            "breach_check": {
                "requests_per_minute": 3,
                "requests_per_hour": 20,
                "requests_per_day": 50
            },
            "whois_lookup": {
                "requests_per_minute": 10,
                "requests_per_hour": 100,
                "requests_per_day": 500
            }
        }
        
        try:
            if self.rate_limits_file.exists():
                with open(self.rate_limits_file, 'r') as f:
                    limits = json.load(f)
                # Merge with defaults for new limits
                for key, value in default_limits.items():
                    if key not in limits:
                        limits[key] = value
                return limits
            else:
                self._save_rate_limits(default_limits)
                return default_limits
                
        except Exception as e:
            self.logger.error(f"Error loading rate limits: {e}")
            return default_limits
    
    def _save_rate_limits(self, limits=None):
        """Save rate limiting configuration"""
        if limits is None:
            limits = self.limits
        
        try:
            with open(self.rate_limits_file, 'w') as f:
                json.dump(limits, f, indent=2)
        except Exception as e:
            self.logger.error(f"Error saving rate limits: {e}")
    
    def _start_cleanup_thread(self):
        """Start background thread to clean up old request history"""
        def cleanup():
            while True:
                try:
                    time.sleep(300)  # Clean up every 5 minutes
                    self._cleanup_old_requests()
                except Exception as e:
                    self.logger.error(f"Error in cleanup thread: {e}")
        
        cleanup_thread = threading.Thread(target=cleanup, daemon=True)
        cleanup_thread.start()
    
    def _cleanup_old_requests(self):
        """Remove old request history to prevent memory leaks"""
        with self._lock:
            current_time = time.time()
            cutoff_time = current_time - 86400  # Keep 24 hours of history
            
            for key in list(self._request_history.keys()):
                history = self._request_history[key]
                while history and history[0] < cutoff_time:
                    history.popleft()
                
                # Remove empty histories
                if not history:
                    del self._request_history[key]
    
    def check_rate_limit(self, category, subcategory=None, user_id="default"):
        """Check if request is within rate limits"""
        key = f"{category}:{subcategory}:{user_id}" if subcategory else f"{category}:{user_id}"
        
        with self._lock:
            current_time = time.time()
            
            # Check if currently blocked
            if key in self._blocked_until and current_time < self._blocked_until[key]:
                remaining = int(self._blocked_until[key] - current_time)
                return False, f"Rate limited. Try again in {remaining} seconds."
            
            # Get rate limits for this category
            if subcategory and category in self.limits and subcategory in self.limits[category]:
                limits = self.limits[category][subcategory]
            elif category in self.limits:
                limits = self.limits[category]
            else:
                # No limits configured, allow request
                return True, "OK"
            
            # Check various time windows
            history = self._request_history[key]
            
            # Check per-minute limit
            if "requests_per_minute" in limits:
                minute_ago = current_time - 60
                recent_requests = sum(1 for t in history if t > minute_ago)
                if recent_requests >= limits["requests_per_minute"]:
                    self._blocked_until[key] = current_time + 60
                    return False, f"Rate limit exceeded: {limits['requests_per_minute']} requests per minute"
            
            # Check per-hour limit
            if "requests_per_hour" in limits:
                hour_ago = current_time - 3600
                recent_requests = sum(1 for t in history if t > hour_ago)
                if recent_requests >= limits["requests_per_hour"]:
                    self._blocked_until[key] = current_time + 300  # 5 minute cooldown
                    return False, f"Rate limit exceeded: {limits['requests_per_hour']} requests per hour"
            
            # Check per-day limit
            if "requests_per_day" in limits:
                day_ago = current_time - 86400
                recent_requests = sum(1 for t in history if t > day_ago)
                if recent_requests >= limits["requests_per_day"]:
                    self._blocked_until[key] = current_time + 3600  # 1 hour cooldown
                    return False, f"Rate limit exceeded: {limits['requests_per_day']} requests per day"
            
            # Check burst limit
            if "burst_limit" in limits:
                burst_window = 10  # 10 seconds
                burst_ago = current_time - burst_window
                burst_requests = sum(1 for t in history if t > burst_ago)
                if burst_requests >= limits["burst_limit"]:
                    cooldown = limits.get("cooldown_seconds", 30)
                    self._blocked_until[key] = current_time + cooldown
                    return False, f"Burst limit exceeded: {limits['burst_limit']} requests in {burst_window} seconds"
            
            return True, "OK"
    
    def record_request(self, category, subcategory=None, user_id="default"):
        """Record a successful request"""
        key = f"{category}:{subcategory}:{user_id}" if subcategory else f"{category}:{user_id}"
        
        with self._lock:
            current_time = time.time()
            self._request_history[key].append(current_time)
            
            # Log the request
            log_key = f"{category}/{subcategory}" if subcategory else category
            self.logger.info(f"Request recorded: {log_key} for user {user_id}")
    
    def get_rate_limit_status(self, category, subcategory=None, user_id="default"):
        """Get current rate limit status for a category"""
        key = f"{category}:{subcategory}:{user_id}" if subcategory else f"{category}:{user_id}"
        
        with self._lock:
            current_time = time.time()
            history = self._request_history[key]
            
            # Get limits
            if subcategory and category in self.limits and subcategory in self.limits[category]:
                limits = self.limits[category][subcategory]
            elif category in self.limits:
                limits = self.limits[category]
            else:
                return {"status": "no_limits", "remaining": "unlimited"}
            
            status = {}
            
            # Check remaining requests for each time window
            if "requests_per_minute" in limits:
                minute_ago = current_time - 60
                used = sum(1 for t in history if t > minute_ago)
                status["minute"] = {
                    "limit": limits["requests_per_minute"],
                    "used": used,
                    "remaining": max(0, limits["requests_per_minute"] - used)
                }
            
            if "requests_per_hour" in limits:
                hour_ago = current_time - 3600
                used = sum(1 for t in history if t > hour_ago)
                status["hour"] = {
                    "limit": limits["requests_per_hour"],
                    "used": used,
                    "remaining": max(0, limits["requests_per_hour"] - used)
                }
            
            if "requests_per_day" in limits:
                day_ago = current_time - 86400
                used = sum(1 for t in history if t > day_ago)
                status["day"] = {
                    "limit": limits["requests_per_day"],
                    "used": used,
                    "remaining": max(0, limits["requests_per_day"] - used)
                }
            
            # Check if blocked
            if key in self._blocked_until and current_time < self._blocked_until[key]:
                status["blocked_until"] = self._blocked_until[key]
                status["blocked_seconds"] = int(self._blocked_until[key] - current_time)
            
            return status
    
    def reset_rate_limits(self, category=None, subcategory=None, user_id="default"):
        """Reset rate limits for debugging/admin purposes"""
        with self._lock:
            if category:
                key = f"{category}:{subcategory}:{user_id}" if subcategory else f"{category}:{user_id}"
                if key in self._request_history:
                    del self._request_history[key]
                if key in self._blocked_until:
                    del self._blocked_until[key]
                self.logger.warning(f"Rate limits reset for {key}")
            else:
                # Reset all
                self._request_history.clear()
                self._blocked_until.clear()
                self.logger.warning("All rate limits reset")
    
    def update_limits(self, category, new_limits):
        """Update rate limits for a category"""
        self.limits[category] = new_limits
        self._save_rate_limits()
        self.logger.info(f"Updated rate limits for {category}")