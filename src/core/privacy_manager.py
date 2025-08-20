#!/usr/bin/env python3
"""
Privacy Manager for CIOT
Handles data privacy controls and user consent management
"""

import json
import os
import shutil
import hashlib
from pathlib import Path
from datetime import datetime, timedelta
import logging

class PrivacyManager:
    """Manages data privacy controls and user consent"""
    
    def __init__(self, config_dir="config", data_dir="data"):
        self.config_dir = Path(config_dir)
        self.data_dir = Path(data_dir)
        self.config_dir.mkdir(exist_ok=True)
        self.data_dir.mkdir(exist_ok=True)
        
        self.privacy_config_file = self.config_dir / "privacy_settings.json"
        self.consent_file = self.config_dir / "user_consent.json"
        self.logger = logging.getLogger('CIOT_Privacy')
        
        # Load privacy settings
        self.privacy_settings = self._load_privacy_settings()
        self.user_consent = self._load_user_consent()
    
    def _load_privacy_settings(self):
        """Load privacy settings configuration"""
        default_settings = {
            "data_retention": {
                "investigation_history_days": 90,
                "temp_files_hours": 24,
                "cache_data_days": 7,
                "audit_logs_days": 365,
                "auto_cleanup_enabled": True
            },
            "data_anonymization": {
                "hash_phone_numbers": True,
                "hash_personal_data": True,
                "remove_metadata": True,
                "anonymize_exports": False
            },
            "data_sharing": {
                "allow_analytics": False,
                "allow_error_reporting": True,
                "share_threat_intelligence": False,
                "external_api_logging": False
            },
            "security": {
                "encrypt_stored_data": True,
                "secure_deletion": True,
                "require_consent": True,
                "gdpr_compliance": True
            },
            "user_rights": {
                "data_portability": True,
                "right_to_deletion": True,
                "data_access_request": True,
                "consent_withdrawal": True
            }
        }
        
        try:
            if self.privacy_config_file.exists():
                with open(self.privacy_config_file, 'r') as f:
                    settings = json.load(f)
                # Merge with defaults
                for key, value in default_settings.items():
                    if key not in settings:
                        settings[key] = value
                    elif isinstance(value, dict):
                        for subkey, subvalue in value.items():
                            if subkey not in settings[key]:
                                settings[key][subkey] = subvalue
                return settings
            else:
                self._save_privacy_settings(default_settings)
                return default_settings
                
        except Exception as e:
            self.logger.error(f"Error loading privacy settings: {e}")
            return default_settings
    
    def _save_privacy_settings(self, settings=None):
        """Save privacy settings"""
        if settings is None:
            settings = self.privacy_settings
        
        try:
            with open(self.privacy_config_file, 'w') as f:
                json.dump(settings, f, indent=2)
        except Exception as e:
            self.logger.error(f"Error saving privacy settings: {e}")
    
    def _load_user_consent(self):
        """Load user consent records"""
        try:
            if self.consent_file.exists():
                with open(self.consent_file, 'r') as f:
                    return json.load(f)
            else:
                return {}
        except Exception as e:
            self.logger.error(f"Error loading user consent: {e}")
            return {}
    
    def _save_user_consent(self):
        """Save user consent records"""
        try:
            with open(self.consent_file, 'w') as f:
                json.dump(self.user_consent, f, indent=2)
        except Exception as e:
            self.logger.error(f"Error saving user consent: {e}")
    
    def record_consent(self, consent_type, granted=True, details=None):
        """Record user consent for data processing"""
        consent_record = {
            "granted": granted,
            "timestamp": datetime.now().isoformat(),
            "details": details or {},
            "ip_hash": self._get_session_hash(),
            "version": "1.0"
        }
        
        self.user_consent[consent_type] = consent_record
        self._save_user_consent()
        
        self.logger.info(f"User consent recorded: {consent_type} = {granted}")
        return consent_record
    
    def check_consent(self, consent_type):
        """Check if user has granted consent for specific data processing"""
        if not self.privacy_settings["security"]["require_consent"]:
            return True
        
        consent = self.user_consent.get(consent_type, {})
        return consent.get("granted", False)
    
    def withdraw_consent(self, consent_type):
        """Allow user to withdraw consent"""
        if consent_type in self.user_consent:
            self.user_consent[consent_type]["granted"] = False
            self.user_consent[consent_type]["withdrawn_at"] = datetime.now().isoformat()
            self._save_user_consent()
            
            # Trigger data cleanup if required
            if consent_type == "data_storage":
                self.cleanup_user_data()
            
            self.logger.info(f"User consent withdrawn: {consent_type}")
            return True
        
        return False
    
    def _get_session_hash(self):
        """Get anonymized session identifier"""
        # Create a hash that doesn't identify the user but allows session tracking
        session_data = f"{datetime.now().date()}{os.getpid()}"
        return hashlib.sha256(session_data.encode()).hexdigest()[:16]
    
    def anonymize_phone_number(self, phone_number):
        """Anonymize phone number for storage"""
        if not self.privacy_settings["data_anonymization"]["hash_phone_numbers"]:
            return phone_number
        
        # Create a consistent hash for the phone number
        salt = "ciot_phone_salt_2024"  # Fixed salt for consistency
        phone_hash = hashlib.sha256(f"{phone_number}{salt}".encode()).hexdigest()[:16]
        return f"HASH_{phone_hash}"
    
    def anonymize_personal_data(self, data):
        """Anonymize personal data in investigation results"""
        if not self.privacy_settings["data_anonymization"]["hash_personal_data"]:
            return data
        
        if isinstance(data, dict):
            anonymized = {}
            for key, value in data.items():
                if key.lower() in ['name', 'email', 'address', 'owner']:
                    if value and isinstance(value, str):
                        anonymized[key] = self._hash_personal_field(value)
                    else:
                        anonymized[key] = value
                else:
                    anonymized[key] = value
            return anonymized
        
        return data
    
    def _hash_personal_field(self, value):
        """Hash a personal data field"""
        if not value or len(value) < 3:
            return "[REDACTED]"
        
        # Keep first and last character, hash the middle
        if len(value) <= 4:
            return value[0] + "*" * (len(value) - 2) + value[-1]
        
        middle_hash = hashlib.md5(value[1:-1].encode()).hexdigest()[:4]
        return f"{value[0]}***{middle_hash}***{value[-1]}"
    
    def cleanup_expired_data(self):
        """Clean up expired data based on retention policies"""
        if not self.privacy_settings["data_retention"]["auto_cleanup_enabled"]:
            return
        
        try:
            current_time = datetime.now()
            
            # Clean up investigation history
            history_days = self.privacy_settings["data_retention"]["investigation_history_days"]
            if history_days > 0:
                cutoff_date = current_time - timedelta(days=history_days)
                self._cleanup_investigation_history(cutoff_date)
            
            # Clean up temporary files
            temp_hours = self.privacy_settings["data_retention"]["temp_files_hours"]
            if temp_hours > 0:
                cutoff_time = current_time - timedelta(hours=temp_hours)
                self._cleanup_temp_files(cutoff_time)
            
            # Clean up cache data
            cache_days = self.privacy_settings["data_retention"]["cache_data_days"]
            if cache_days > 0:
                cutoff_date = current_time - timedelta(days=cache_days)
                self._cleanup_cache_data(cutoff_date)
            
            # Clean up old audit logs
            audit_days = self.privacy_settings["data_retention"]["audit_logs_days"]
            if audit_days > 0:
                cutoff_date = current_time - timedelta(days=audit_days)
                self._cleanup_audit_logs(cutoff_date)
            
            self.logger.info("Completed automatic data cleanup")
            
        except Exception as e:
            self.logger.error(f"Error during data cleanup: {e}")
    
    def _cleanup_investigation_history(self, cutoff_date):
        """Clean up old investigation history"""
        cases_dir = self.data_dir / "cases"
        if not cases_dir.exists():
            return
        
        for case_file in cases_dir.glob("session_*.json"):
            try:
                file_time = datetime.fromtimestamp(case_file.stat().st_mtime)
                if file_time < cutoff_date:
                    if self.privacy_settings["security"]["secure_deletion"]:
                        self._secure_delete(case_file)
                    else:
                        case_file.unlink()
                    self.logger.info(f"Cleaned up old case file: {case_file.name}")
            except Exception as e:
                self.logger.error(f"Error cleaning up case file {case_file}: {e}")
    
    def _cleanup_temp_files(self, cutoff_time):
        """Clean up temporary files"""
        temp_patterns = ["*.tmp", "*.temp", "temp_*"]
        
        for pattern in temp_patterns:
            for temp_file in self.data_dir.rglob(pattern):
                try:
                    file_time = datetime.fromtimestamp(temp_file.stat().st_mtime)
                    if file_time < cutoff_time:
                        if self.privacy_settings["security"]["secure_deletion"]:
                            self._secure_delete(temp_file)
                        else:
                            temp_file.unlink()
                        self.logger.info(f"Cleaned up temp file: {temp_file.name}")
                except Exception as e:
                    self.logger.error(f"Error cleaning up temp file {temp_file}: {e}")
    
    def _cleanup_cache_data(self, cutoff_date):
        """Clean up cached data"""
        cache_files = [
            self.data_dir / "performance_cache.db",
            self.data_dir / "phone_history.db"
        ]
        
        for cache_file in cache_files:
            if cache_file.exists():
                try:
                    file_time = datetime.fromtimestamp(cache_file.stat().st_mtime)
                    if file_time < cutoff_date:
                        if self.privacy_settings["security"]["secure_deletion"]:
                            self._secure_delete(cache_file)
                        else:
                            cache_file.unlink()
                        self.logger.info(f"Cleaned up cache file: {cache_file.name}")
                except Exception as e:
                    self.logger.error(f"Error cleaning up cache file {cache_file}: {e}")
    
    def _cleanup_audit_logs(self, cutoff_date):
        """Clean up old audit logs"""
        logs_dir = Path("logs")
        if not logs_dir.exists():
            return
        
        for log_file in logs_dir.glob("audit_*.log"):
            try:
                file_time = datetime.fromtimestamp(log_file.stat().st_mtime)
                if file_time < cutoff_date:
                    if self.privacy_settings["security"]["secure_deletion"]:
                        self._secure_delete(log_file)
                    else:
                        log_file.unlink()
                    self.logger.info(f"Cleaned up old audit log: {log_file.name}")
            except Exception as e:
                self.logger.error(f"Error cleaning up audit log {log_file}: {e}")
    
    def _secure_delete(self, file_path):
        """Securely delete a file by overwriting it"""
        try:
            if file_path.is_file():
                # Overwrite file with random data multiple times
                file_size = file_path.stat().st_size
                with open(file_path, 'r+b') as f:
                    for _ in range(3):  # 3 passes
                        f.seek(0)
                        f.write(os.urandom(file_size))
                        f.flush()
                        os.fsync(f.fileno())
                
                # Finally delete the file
                file_path.unlink()
                
        except Exception as e:
            self.logger.error(f"Error securely deleting {file_path}: {e}")
            # Fall back to regular deletion
            try:
                file_path.unlink()
            except:
                pass
    
    def cleanup_user_data(self):
        """Complete cleanup of user data (for consent withdrawal)"""
        try:
            # Remove all investigation history
            cases_dir = self.data_dir / "cases"
            if cases_dir.exists():
                shutil.rmtree(cases_dir)
                cases_dir.mkdir()
            
            # Remove cache data
            cache_files = [
                self.data_dir / "performance_cache.db",
                self.data_dir / "phone_history.db",
                self.data_dir / "whois_history.db"
            ]
            
            for cache_file in cache_files:
                if cache_file.exists():
                    if self.privacy_settings["security"]["secure_deletion"]:
                        self._secure_delete(cache_file)
                    else:
                        cache_file.unlink()
            
            self.logger.info("Completed user data cleanup")
            
        except Exception as e:
            self.logger.error(f"Error during user data cleanup: {e}")
    
    def export_user_data(self):
        """Export user data for portability (GDPR compliance)"""
        try:
            export_data = {
                "export_timestamp": datetime.now().isoformat(),
                "privacy_settings": self.privacy_settings,
                "consent_records": self.user_consent,
                "investigation_history": [],
                "cached_data": {}
            }
            
            # Export investigation history
            cases_dir = self.data_dir / "cases"
            if cases_dir.exists():
                for case_file in cases_dir.glob("session_*.json"):
                    try:
                        with open(case_file, 'r') as f:
                            case_data = json.load(f)
                        export_data["investigation_history"].append(case_data)
                    except Exception as e:
                        self.logger.error(f"Error exporting case {case_file}: {e}")
            
            return export_data
            
        except Exception as e:
            self.logger.error(f"Error exporting user data: {e}")
            return None
    
    def get_privacy_summary(self):
        """Get summary of current privacy settings"""
        return {
            "data_retention_days": self.privacy_settings["data_retention"]["investigation_history_days"],
            "anonymization_enabled": self.privacy_settings["data_anonymization"]["hash_phone_numbers"],
            "encryption_enabled": self.privacy_settings["security"]["encrypt_stored_data"],
            "auto_cleanup_enabled": self.privacy_settings["data_retention"]["auto_cleanup_enabled"],
            "consent_required": self.privacy_settings["security"]["require_consent"],
            "gdpr_compliant": self.privacy_settings["security"]["gdpr_compliance"],
            "active_consents": [k for k, v in self.user_consent.items() if v.get("granted", False)]
        }
    
    def update_privacy_setting(self, category, setting, value):
        """Update a specific privacy setting"""
        if category in self.privacy_settings and setting in self.privacy_settings[category]:
            self.privacy_settings[category][setting] = value
            self._save_privacy_settings()
            self.logger.info(f"Updated privacy setting: {category}.{setting} = {value}")
            return True
        return False