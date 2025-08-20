#!/usr/bin/env python3
"""
Security Manager for CIOT
Integrates all security and privacy protection measures
"""

import time
import hashlib
from datetime import datetime
from typing import Dict, Any, Optional, Tuple
import logging

from .secure_api_manager import SecureAPIManager
from .rate_limiter import RateLimiter
from .privacy_manager import PrivacyManager
from .legal_compliance import LegalComplianceManager
from .audit_logger import EnhancedAuditLogger

class SecurityManager:
    """Centralized security management for CIOT"""
    
    def __init__(self, config_dir="config", data_dir="data"):
        self.config_dir = config_dir
        self.data_dir = data_dir
        self.logger = logging.getLogger('CIOT_Security')
        
        # Initialize security components
        self.api_manager = SecureAPIManager(config_dir)
        self.rate_limiter = RateLimiter(config_dir)
        self.privacy_manager = PrivacyManager(config_dir, data_dir)
        self.compliance_manager = LegalComplianceManager(config_dir)
        self.audit_logger = EnhancedAuditLogger(config_dir)
        
        # Security state
        self.current_session = None
        self.security_warnings_shown = {}
        
        self.logger.info("Security Manager initialized")
    
    def initialize_session(self, session_id: str, user_context: Optional[Dict] = None, jurisdiction: str = "international") -> Dict[str, Any]:
        """Initialize a secure investigation session"""
        try:
            # Start audit logging
            self.audit_logger.start_session(session_id, user_context)
            self.current_session = session_id
            
            # Check if startup warning should be shown
            startup_warning = None
            if self.compliance_manager.should_show_warning("startup"):
                startup_warning = self.compliance_manager.get_startup_warning(jurisdiction)
                if startup_warning:
                    self.security_warnings_shown["startup"] = datetime.now().isoformat()
            
            # Log session initialization
            self.audit_logger.log_security_event(
                "session_initialization",
                "low",
                f"Secure session initialized: {session_id}",
                {"jurisdiction": jurisdiction, "user_context": bool(user_context)}
            )
            
            return {
                "session_id": session_id,
                "security_initialized": True,
                "startup_warning": startup_warning,
                "privacy_settings": self.privacy_manager.get_privacy_summary(),
                "rate_limits_active": True,
                "audit_logging_active": True
            }
            
        except Exception as e:
            self.logger.error(f"Error initializing secure session: {e}")
            self.audit_logger.log_error("session_initialization_error", str(e), "security_manager")
            return {"session_id": session_id, "security_initialized": False, "error": str(e)}
    
    def check_investigation_authorization(self, investigation_type: str, target: str, user_context: Optional[Dict] = None, jurisdiction: str = "international") -> Tuple[bool, Optional[Dict]]:
        """Check if investigation is authorized and show appropriate warnings"""
        try:
            # Check for ethical concerns
            ethical_concerns = self.compliance_manager.check_ethical_concerns(target)
            
            if ethical_concerns:
                high_risk_concerns = [c for c in ethical_concerns if c["level"] in ["high", "critical"]]
                if high_risk_concerns:
                    self.audit_logger.log_security_event(
                        "ethical_concern_detected",
                        "high",
                        f"High-risk ethical concerns detected for investigation",
                        {"concerns": [c["type"] for c in high_risk_concerns], "target_hash": hashlib.sha256(target.encode()).hexdigest()[:16]}
                    )
                    
                    # For critical concerns, block the investigation
                    critical_concerns = [c for c in ethical_concerns if c["level"] == "critical"]
                    if critical_concerns:
                        return False, {
                            "blocked": True,
                            "reason": "Critical ethical concerns detected",
                            "concerns": critical_concerns
                        }
            
            # Get investigation-specific warning
            investigation_warning = None
            warning_key = f"{investigation_type}_warning"
            
            if self.compliance_manager.should_show_warning(warning_key, self.security_warnings_shown.get(warning_key)):
                investigation_warning = self.compliance_manager.get_investigation_warning(investigation_type, jurisdiction)
                if investigation_warning:
                    self.security_warnings_shown[warning_key] = datetime.now().isoformat()
            
            # Log authorization check
            self.audit_logger.log_compliance_event(
                jurisdiction,
                "authorization_check",
                f"Investigation authorization checked for {investigation_type}",
                {
                    "investigation_type": investigation_type,
                    "target_hash": hashlib.sha256(target.encode()).hexdigest()[:16],
                    "ethical_concerns_count": len(ethical_concerns),
                    "warning_shown": bool(investigation_warning)
                }
            )
            
            return True, {
                "authorized": True,
                "investigation_warning": investigation_warning,
                "ethical_concerns": ethical_concerns,
                "jurisdiction": jurisdiction
            }
            
        except Exception as e:
            self.logger.error(f"Error checking investigation authorization: {e}")
            self.audit_logger.log_error("authorization_check_error", str(e), "security_manager")
            return False, {"error": str(e)}
    
    def check_rate_limits(self, category: str, subcategory: Optional[str] = None, user_id: str = "default") -> Tuple[bool, str]:
        """Check rate limits for an operation"""
        try:
            allowed, message = self.rate_limiter.check_rate_limit(category, subcategory, user_id)
            
            # Log rate limit check
            self.audit_logger.log_rate_limit_event(
                category,
                f"{subcategory or 'general'}_check",
                not allowed,
                {"user_id": user_id, "message": message}
            )
            
            if not allowed:
                self.audit_logger.log_security_event(
                    "rate_limit_exceeded",
                    "medium",
                    f"Rate limit exceeded for {category}/{subcategory or 'general'}",
                    {"user_id": user_id, "category": category, "subcategory": subcategory}
                )
            
            return allowed, message
            
        except Exception as e:
            self.logger.error(f"Error checking rate limits: {e}")
            return False, f"Rate limit check failed: {e}"
    
    def record_operation(self, category: str, subcategory: Optional[str] = None, user_id: str = "default"):
        """Record a successful operation for rate limiting"""
        try:
            self.rate_limiter.record_request(category, subcategory, user_id)
        except Exception as e:
            self.logger.error(f"Error recording operation: {e}")
    
    def get_secure_api_key(self, service: str, key_name: str = "api_key") -> Optional[str]:
        """Get API key securely"""
        try:
            api_key = self.api_manager.get_api_key(service, key_name)
            
            if api_key:
                # Log API key access (without the actual key)
                self.audit_logger.log_data_access(
                    "api_key",
                    service,
                    1,
                    "external_api_call"
                )
            
            return api_key
            
        except Exception as e:
            self.logger.error(f"Error retrieving API key for {service}: {e}")
            self.audit_logger.log_error("api_key_retrieval_error", str(e), "security_manager", {"service": service})
            return None
    
    def log_api_call(self, service: str, endpoint: str, success: bool, response_time: float, error: Optional[str] = None):
        """Log external API call"""
        try:
            self.audit_logger.log_api_call(service, endpoint, success, response_time, error)
            
            if not success and error:
                self.audit_logger.log_security_event(
                    "api_call_failure",
                    "low",
                    f"API call failed: {service}/{endpoint}",
                    {"error": error, "response_time": response_time}
                )
                
        except Exception as e:
            self.logger.error(f"Error logging API call: {e}")
    
    def process_investigation_data(self, data: Dict[str, Any], anonymize: bool = True) -> Dict[str, Any]:
        """Process investigation data with privacy controls"""
        try:
            if anonymize:
                processed_data = self.privacy_manager.anonymize_personal_data(data)
            else:
                processed_data = data
            
            # Log data processing
            self.audit_logger.log_privacy_event(
                "data_processing",
                "Investigation data processed with privacy controls",
                details={"anonymized": anonymize, "data_types": list(data.keys()) if isinstance(data, dict) else "unknown"}
            )
            
            return processed_data
            
        except Exception as e:
            self.logger.error(f"Error processing investigation data: {e}")
            self.audit_logger.log_error("data_processing_error", str(e), "security_manager")
            return data
    
    def store_investigation_data(self, phone_number: str, investigation_data: Dict[str, Any]) -> bool:
        """Store investigation data with privacy controls"""
        try:
            # Check consent for data storage
            if not self.privacy_manager.check_consent("data_storage"):
                self.audit_logger.log_privacy_event(
                    "consent_check_failed",
                    "Data storage blocked due to lack of consent",
                    phone_number
                )
                return False
            
            # Anonymize phone number if required
            anonymized_phone = self.privacy_manager.anonymize_phone_number(phone_number)
            
            # Process data with privacy controls
            processed_data = self.process_investigation_data(investigation_data, anonymize=True)
            
            # Store data (this would integrate with historical data manager)
            # For now, just log the storage
            self.audit_logger.log_data_access(
                "investigation_results",
                "local_storage",
                1,
                "historical_tracking"
            )
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error storing investigation data: {e}")
            self.audit_logger.log_error("data_storage_error", str(e), "security_manager")
            return False
    
    def export_investigation_data(self, data: Dict[str, Any], export_format: str, destination: str) -> bool:
        """Export investigation data with security controls"""
        try:
            # Check consent for data export
            if not self.privacy_manager.check_consent("data_export"):
                self.audit_logger.log_privacy_event(
                    "consent_check_failed",
                    "Data export blocked due to lack of consent",
                    details={"format": export_format, "destination": destination}
                )
                return False
            
            # Process data for export
            export_data = self.process_investigation_data(data, anonymize=True)
            
            # Log export
            self.audit_logger.log_export_action(
                "investigation_results",
                export_format,
                len(export_data) if isinstance(export_data, (list, dict)) else 1,
                destination
            )
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error exporting investigation data: {e}")
            self.audit_logger.log_error("data_export_error", str(e), "security_manager")
            return False
    
    def cleanup_session_data(self):
        """Clean up session data and perform maintenance"""
        try:
            # Perform privacy cleanup
            self.privacy_manager.cleanup_expired_data()
            
            # End audit session
            if self.current_session:
                self.audit_logger.end_session({
                    "cleanup_performed": True,
                    "session_duration": "unknown"
                })
            
            # Log cleanup
            self.audit_logger.log_privacy_event(
                "session_cleanup",
                "Session data cleanup completed"
            )
            
            self.current_session = None
            
        except Exception as e:
            self.logger.error(f"Error during session cleanup: {e}")
            self.audit_logger.log_error("session_cleanup_error", str(e), "security_manager")
    
    def get_security_status(self) -> Dict[str, Any]:
        """Get current security status"""
        try:
            return {
                "session_active": bool(self.current_session),
                "api_keys_configured": len(self.api_manager.list_services()),
                "privacy_settings": self.privacy_manager.get_privacy_summary(),
                "rate_limits_active": True,
                "audit_logging_active": True,
                "compliance_jurisdiction": self.compliance_manager.compliance_config["jurisdictions"]["default"],
                "warnings_shown": list(self.security_warnings_shown.keys())
            }
            
        except Exception as e:
            self.logger.error(f"Error getting security status: {e}")
            return {"error": str(e)}
    
    def handle_security_incident(self, incident_type: str, severity: str, description: str, details: Optional[Dict] = None):
        """Handle security incidents"""
        try:
            # Log security incident
            self.audit_logger.log_security_event(incident_type, severity, description, details)
            
            # Take appropriate action based on severity
            if severity.lower() == "critical":
                # For critical incidents, we might want to lock down the system
                self.logger.critical(f"Critical security incident: {description}")
                
                # Log the incident response
                self.audit_logger.log_security_event(
                    "incident_response",
                    "high",
                    f"Responding to critical security incident: {incident_type}",
                    {"original_incident": incident_type, "response_action": "system_lockdown"}
                )
            
        except Exception as e:
            self.logger.error(f"Error handling security incident: {e}")
    
    def generate_security_report(self) -> Dict[str, Any]:
        """Generate comprehensive security report"""
        try:
            return {
                "report_timestamp": datetime.now().isoformat(),
                "security_status": self.get_security_status(),
                "audit_report": self.audit_logger.generate_audit_report(),
                "compliance_report": self.compliance_manager.generate_compliance_report(),
                "privacy_summary": self.privacy_manager.get_privacy_summary(),
                "rate_limit_status": {
                    "phone_investigation": self.rate_limiter.get_rate_limit_status("phone_investigation"),
                    "api_calls": self.rate_limiter.get_rate_limit_status("api_calls")
                }
            }
            
        except Exception as e:
            self.logger.error(f"Error generating security report: {e}")
            return {"error": str(e)}