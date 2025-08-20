#!/usr/bin/env python3
"""
Enhanced Audit Logger for CIOT
Handles comprehensive audit logging for investigations with security features
"""

import logging
import datetime
import json
import hashlib
import os
from pathlib import Path
from typing import Dict, Any, Optional

class EnhancedAuditLogger:
    """Enhanced professional audit logging system with security features"""
    
    def __init__(self, config_dir="config"):
        self.config_dir = Path(config_dir)
        self.config_dir.mkdir(exist_ok=True)
        self.audit_config_file = self.config_dir / "audit_config.json"
        
        # Load audit configuration
        self.audit_config = self._load_audit_config()
        
        # Setup loggers
        self.setup_loggers()
        
        # Session tracking
        self.current_session = None
        self.session_start_time = None
    
    def _load_audit_config(self):
        """Load audit logging configuration"""
        default_config = {
            "logging_levels": {
                "investigation": "INFO",
                "security": "WARNING",
                "privacy": "INFO",
                "compliance": "INFO",
                "system": "ERROR"
            },
            "log_retention_days": 365,
            "log_rotation_size_mb": 10,
            "anonymize_sensitive_data": True,
            "include_system_info": True,
            "log_api_calls": True,
            "log_user_actions": True,
            "log_data_access": True,
            "log_exports": True,
            "log_errors": True,
            "log_security_events": True,
            "separate_log_files": True
        }
        
        try:
            if self.audit_config_file.exists():
                with open(self.audit_config_file, 'r') as f:
                    config = json.load(f)
                # Merge with defaults
                for key, value in default_config.items():
                    if key not in config:
                        config[key] = value
                return config
            else:
                self._save_audit_config(default_config)
                return default_config
                
        except Exception as e:
            print(f"Error loading audit config: {e}")
            return default_config
    
    def _save_audit_config(self, config=None):
        """Save audit configuration"""
        if config is None:
            config = self.audit_config
        
        try:
            with open(self.audit_config_file, 'w') as f:
                json.dump(config, f, indent=2)
        except Exception as e:
            print(f"Error saving audit config: {e}")
    
    def setup_loggers(self):
        """Setup comprehensive audit logging system"""
        # Create logs directory
        logs_dir = Path("logs")
        logs_dir.mkdir(exist_ok=True)
        
        # Setup different loggers for different types of events
        self.loggers = {}
        
        log_types = [
            "investigation",
            "security", 
            "privacy",
            "compliance",
            "system"
        ]
        
        for log_type in log_types:
            logger = logging.getLogger(f'CIOT_{log_type.title()}')
            logger.setLevel(getattr(logging, self.audit_config["logging_levels"][log_type]))
            
            # Clear existing handlers
            logger.handlers.clear()
            
            # File handler
            if self.audit_config["separate_log_files"]:
                log_file = logs_dir / f"{log_type}_{datetime.datetime.now().strftime('%Y%m%d')}.log"
            else:
                log_file = logs_dir / f"audit_{datetime.datetime.now().strftime('%Y%m%d')}.log"
            
            handler = logging.FileHandler(log_file)
            
            # Enhanced formatter with more context
            formatter = logging.Formatter(
                '%(asctime)s | %(name)s | %(levelname)s | %(funcName)s:%(lineno)d | %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            
            self.loggers[log_type] = logger
    
    def _anonymize_data(self, data: Any) -> Any:
        """Anonymize sensitive data for logging"""
        if not self.audit_config["anonymize_sensitive_data"]:
            return data
        
        if isinstance(data, str):
            # Check if it looks like a phone number
            if data.replace('+', '').replace('-', '').replace(' ', '').replace('(', '').replace(')', '').isdigit():
                if len(data.replace('+', '').replace('-', '').replace(' ', '').replace('(', '').replace(')', '')) >= 10:
                    # Hash phone number
                    return f"PHONE_HASH_{hashlib.sha256(data.encode()).hexdigest()[:16]}"
            
            # Check if it looks like an email
            if '@' in data and '.' in data:
                return f"EMAIL_HASH_{hashlib.sha256(data.encode()).hexdigest()[:16]}"
        
        elif isinstance(data, dict):
            anonymized = {}
            for key, value in data.items():
                if key.lower() in ['phone', 'email', 'name', 'address', 'ip']:
                    anonymized[key] = self._anonymize_data(value)
                else:
                    anonymized[key] = value
            return anonymized
        
        return data
    
    def _get_session_context(self) -> Dict[str, Any]:
        """Get current session context for logging"""
        context = {
            "session_id": self.current_session,
            "timestamp": datetime.datetime.now().isoformat(),
            "process_id": os.getpid()
        }
        
        if self.audit_config["include_system_info"]:
            context.update({
                "platform": os.name,
                "working_directory": str(Path.cwd())
            })
        
        return context
    
    def start_session(self, session_id: str, user_context: Optional[Dict] = None):
        """Start a new investigation session"""
        self.current_session = session_id
        self.session_start_time = datetime.datetime.now()
        
        context = self._get_session_context()
        if user_context:
            context["user_context"] = self._anonymize_data(user_context)
        
        self.loggers["investigation"].info(
            f"SESSION_START | Session: {session_id} | Context: {json.dumps(context)}"
        )
    
    def end_session(self, session_summary: Optional[Dict] = None):
        """End current investigation session"""
        if not self.current_session:
            return
        
        duration = None
        if self.session_start_time:
            duration = (datetime.datetime.now() - self.session_start_time).total_seconds()
        
        context = self._get_session_context()
        context["duration_seconds"] = duration
        
        if session_summary:
            context["summary"] = self._anonymize_data(session_summary)
        
        self.loggers["investigation"].info(
            f"SESSION_END | Session: {self.current_session} | Context: {json.dumps(context)}"
        )
        
        self.current_session = None
        self.session_start_time = None
    
    def log_investigation_action(self, action: str, target: str, details: Optional[Dict] = None):
        """Log investigation action"""
        context = self._get_session_context()
        context.update({
            "action": action,
            "target": self._anonymize_data(target),
            "details": self._anonymize_data(details) if details else None
        })
        
        self.loggers["investigation"].info(
            f"INVESTIGATION_ACTION | {action} | Target: {self._anonymize_data(target)} | Context: {json.dumps(context)}"
        )
    
    def log_api_call(self, service: str, endpoint: str, success: bool, response_time: float, error: Optional[str] = None):
        """Log external API calls"""
        if not self.audit_config["log_api_calls"]:
            return
        
        context = self._get_session_context()
        context.update({
            "service": service,
            "endpoint": endpoint,
            "success": success,
            "response_time_ms": round(response_time * 1000, 2),
            "error": error
        })
        
        level = "INFO" if success else "WARNING"
        log_message = f"API_CALL | {service} | {endpoint} | Success: {success} | Time: {response_time:.3f}s"
        
        if error:
            log_message += f" | Error: {error}"
        
        getattr(self.loggers["investigation"], level.lower())(
            f"{log_message} | Context: {json.dumps(context)}"
        )
    
    def log_data_access(self, data_type: str, source: str, records_accessed: int, purpose: str):
        """Log data access events"""
        if not self.audit_config["log_data_access"]:
            return
        
        context = self._get_session_context()
        context.update({
            "data_type": data_type,
            "source": source,
            "records_accessed": records_accessed,
            "purpose": purpose
        })
        
        self.loggers["privacy"].info(
            f"DATA_ACCESS | Type: {data_type} | Source: {source} | Records: {records_accessed} | Purpose: {purpose} | Context: {json.dumps(context)}"
        )
    
    def log_export_action(self, export_type: str, format: str, records_count: int, destination: str):
        """Log data export actions"""
        if not self.audit_config["log_exports"]:
            return
        
        context = self._get_session_context()
        context.update({
            "export_type": export_type,
            "format": format,
            "records_count": records_count,
            "destination": self._anonymize_data(destination)
        })
        
        self.loggers["investigation"].info(
            f"DATA_EXPORT | Type: {export_type} | Format: {format} | Records: {records_count} | Context: {json.dumps(context)}"
        )
    
    def log_security_event(self, event_type: str, severity: str, description: str, details: Optional[Dict] = None):
        """Log security events"""
        if not self.audit_config["log_security_events"]:
            return
        
        context = self._get_session_context()
        context.update({
            "event_type": event_type,
            "severity": severity,
            "description": description,
            "details": self._anonymize_data(details) if details else None
        })
        
        level_map = {
            "low": "INFO",
            "medium": "WARNING", 
            "high": "ERROR",
            "critical": "CRITICAL"
        }
        
        log_level = level_map.get(severity.lower(), "WARNING")
        
        getattr(self.loggers["security"], log_level.lower())(
            f"SECURITY_EVENT | {event_type} | {severity.upper()} | {description} | Context: {json.dumps(context)}"
        )
    
    def log_privacy_event(self, event_type: str, description: str, data_subject: Optional[str] = None, details: Optional[Dict] = None):
        """Log privacy-related events"""
        context = self._get_session_context()
        context.update({
            "event_type": event_type,
            "description": description,
            "data_subject": self._anonymize_data(data_subject) if data_subject else None,
            "details": self._anonymize_data(details) if details else None
        })
        
        self.loggers["privacy"].info(
            f"PRIVACY_EVENT | {event_type} | {description} | Context: {json.dumps(context)}"
        )
    
    def log_compliance_event(self, jurisdiction: str, event_type: str, description: str, details: Optional[Dict] = None):
        """Log compliance-related events"""
        context = self._get_session_context()
        context.update({
            "jurisdiction": jurisdiction,
            "event_type": event_type,
            "description": description,
            "details": details
        })
        
        self.loggers["compliance"].info(
            f"COMPLIANCE_EVENT | {jurisdiction} | {event_type} | {description} | Context: {json.dumps(context)}"
        )
    
    def log_user_action(self, action: str, component: str, details: Optional[Dict] = None):
        """Log user interface actions"""
        if not self.audit_config["log_user_actions"]:
            return
        
        context = self._get_session_context()
        context.update({
            "action": action,
            "component": component,
            "details": self._anonymize_data(details) if details else None
        })
        
        self.loggers["investigation"].info(
            f"USER_ACTION | {action} | Component: {component} | Context: {json.dumps(context)}"
        )
    
    def log_error(self, error_type: str, error_message: str, component: str, details: Optional[Dict] = None):
        """Log errors with enhanced context"""
        if not self.audit_config["log_errors"]:
            return
        
        context = self._get_session_context()
        context.update({
            "error_type": error_type,
            "component": component,
            "details": self._anonymize_data(details) if details else None
        })
        
        self.loggers["system"].error(
            f"ERROR | {error_type} | {component} | {error_message} | Context: {json.dumps(context)}"
        )
    
    def log_rate_limit_event(self, category: str, action: str, limit_exceeded: bool, details: Optional[Dict] = None):
        """Log rate limiting events"""
        context = self._get_session_context()
        context.update({
            "category": category,
            "action": action,
            "limit_exceeded": limit_exceeded,
            "details": details
        })
        
        level = "WARNING" if limit_exceeded else "INFO"
        
        getattr(self.loggers["security"], level.lower())(
            f"RATE_LIMIT | {category} | {action} | Exceeded: {limit_exceeded} | Context: {json.dumps(context)}"
        )
    
    def generate_audit_report(self, start_date: Optional[datetime.datetime] = None, end_date: Optional[datetime.datetime] = None) -> Dict:
        """Generate audit report for specified date range"""
        if not start_date:
            start_date = datetime.datetime.now() - datetime.timedelta(days=30)
        if not end_date:
            end_date = datetime.datetime.now()
        
        report = {
            "report_period": {
                "start": start_date.isoformat(),
                "end": end_date.isoformat()
            },
            "generated_at": datetime.datetime.now().isoformat(),
            "summary": {
                "total_sessions": 0,
                "total_investigations": 0,
                "total_api_calls": 0,
                "total_exports": 0,
                "security_events": 0,
                "privacy_events": 0,
                "compliance_events": 0,
                "errors": 0
            },
            "configuration": self.audit_config
        }
        
        # In a real implementation, this would parse log files and generate statistics
        # For now, return the template
        
        return report

# Maintain backward compatibility
class AuditLogger(EnhancedAuditLogger):
    """Backward compatibility wrapper"""
    
    def __init__(self):
        super().__init__()
        # Start a default session for backward compatibility
        self.start_session("legacy_session")
    
    def log_session_start(self, session_id):
        """Legacy method - start session"""
        self.start_session(session_id)
    
    def log_action(self, action, details=None):
        """Legacy method - log action"""
        self.log_investigation_action(action, "unknown", details)
    
    def log_evidence(self, evidence_id, evidence_type):
        """Legacy method - log evidence"""
        self.log_investigation_action("evidence_collection", evidence_id, {"type": evidence_type})
    
    def log_error(self, error_message):
        """Legacy method - log error"""
        self.log_error("general_error", error_message, "unknown")