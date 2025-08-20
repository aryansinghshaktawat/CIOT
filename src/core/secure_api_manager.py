#!/usr/bin/env python3
"""
Secure API Key Manager for CIOT
Handles secure storage and management of API keys with encryption
"""

import json
import os
import base64
import hashlib
from pathlib import Path
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import logging

class SecureAPIManager:
    """Secure API key management with encryption"""
    
    def __init__(self, config_dir="config"):
        self.config_dir = Path(config_dir)
        self.config_dir.mkdir(exist_ok=True)
        self.api_keys_file = self.config_dir / "api_keys.json"
        self.encrypted_keys_file = self.config_dir / "api_keys.enc"
        self.key_file = self.config_dir / ".api_key"
        self.logger = logging.getLogger('CIOT_Security')
        
        # Initialize encryption
        self._encryption_key = self._get_or_create_encryption_key()
        self._cipher = Fernet(self._encryption_key)
        
        # Load API keys
        self.api_keys = self._load_api_keys()
    
    def _get_or_create_encryption_key(self):
        """Get or create encryption key for API keys"""
        try:
            if self.key_file.exists():
                with open(self.key_file, 'rb') as f:
                    return f.read()
            else:
                # Generate new key
                key = Fernet.generate_key()
                with open(self.key_file, 'wb') as f:
                    f.write(key)
                # Set restrictive permissions
                os.chmod(self.key_file, 0o600)
                self.logger.info("Generated new encryption key for API keys")
                return key
        except Exception as e:
            self.logger.error(f"Error managing encryption key: {e}")
            # Fallback to session key
            return Fernet.generate_key()
    
    def _load_api_keys(self):
        """Load API keys from encrypted or plain text file"""
        try:
            # Try encrypted file first
            if self.encrypted_keys_file.exists():
                return self._load_encrypted_keys()
            
            # Fall back to plain text file
            elif self.api_keys_file.exists():
                with open(self.api_keys_file, 'r') as f:
                    keys = json.load(f)
                # Migrate to encrypted storage
                self._save_encrypted_keys(keys)
                self.logger.info("Migrated API keys to encrypted storage")
                return keys
            
            else:
                self.logger.warning("No API keys file found")
                return {}
                
        except Exception as e:
            self.logger.error(f"Error loading API keys: {e}")
            return {}
    
    def _load_encrypted_keys(self):
        """Load API keys from encrypted file"""
        try:
            with open(self.encrypted_keys_file, 'rb') as f:
                encrypted_data = f.read()
            
            decrypted_data = self._cipher.decrypt(encrypted_data)
            return json.loads(decrypted_data.decode())
            
        except Exception as e:
            self.logger.error(f"Error decrypting API keys: {e}")
            return {}
    
    def _save_encrypted_keys(self, keys):
        """Save API keys to encrypted file"""
        try:
            json_data = json.dumps(keys, indent=2)
            encrypted_data = self._cipher.encrypt(json_data.encode())
            
            with open(self.encrypted_keys_file, 'wb') as f:
                f.write(encrypted_data)
            
            # Set restrictive permissions
            os.chmod(self.encrypted_keys_file, 0o600)
            
            # Remove plain text file if it exists
            if self.api_keys_file.exists():
                os.remove(self.api_keys_file)
                self.logger.info("Removed plain text API keys file")
                
        except Exception as e:
            self.logger.error(f"Error encrypting API keys: {e}")
    
    def get_api_key(self, service_name, key_name="api_key"):
        """Get API key for a service"""
        try:
            service_config = self.api_keys.get(service_name, {})
            return service_config.get(key_name)
        except Exception as e:
            self.logger.error(f"Error retrieving API key for {service_name}: {e}")
            return None
    
    def set_api_key(self, service_name, key_name, key_value):
        """Set API key for a service"""
        try:
            if service_name not in self.api_keys:
                self.api_keys[service_name] = {}
            
            self.api_keys[service_name][key_name] = key_value
            self._save_encrypted_keys(self.api_keys)
            self.logger.info(f"Updated API key for {service_name}")
            
        except Exception as e:
            self.logger.error(f"Error setting API key for {service_name}: {e}")
    
    def remove_api_key(self, service_name):
        """Remove API key for a service"""
        try:
            if service_name in self.api_keys:
                del self.api_keys[service_name]
                self._save_encrypted_keys(self.api_keys)
                self.logger.info(f"Removed API key for {service_name}")
                
        except Exception as e:
            self.logger.error(f"Error removing API key for {service_name}: {e}")
    
    def list_services(self):
        """List all configured services"""
        return list(self.api_keys.keys())
    
    def validate_key_format(self, service_name, key_value):
        """Validate API key format for known services"""
        validation_rules = {
            'abstractapi': lambda k: len(k) == 32 and k.isalnum(),
            'neutrino': lambda k: len(k) >= 40,
            'numverify': lambda k: len(k) >= 20,
            'telnyx': lambda k: k.startswith('KEY') and len(k) > 40,
            'intelx': lambda k: len(k) >= 32,
            'dehashed': lambda k: len(k) >= 20
        }
        
        if service_name in validation_rules:
            return validation_rules[service_name](key_value)
        
        # Generic validation - at least 10 characters
        return len(key_value) >= 10
    
    def get_service_config(self, service_name):
        """Get complete service configuration"""
        return self.api_keys.get(service_name, {})
    
    def is_service_configured(self, service_name):
        """Check if service is properly configured"""
        service_config = self.api_keys.get(service_name, {})
        return bool(service_config.get('api_key'))