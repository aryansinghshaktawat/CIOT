#!/usr/bin/env python3
"""
Configuration Manager for CIOT
Handles application configuration and settings
"""

import json
import os
from pathlib import Path

class ConfigManager:
    """Manages application configuration"""
    
    def __init__(self):
        self.config_file = Path("config/ciot_config.json")
        self.config_file.parent.mkdir(exist_ok=True)
        self.config = self.load_config()
    
    def load_config(self):
        """Load configuration from file"""
        default_config = {
            "theme": "dark",
            "auto_save": True,
            "auto_save_interval": 300,
            "investigation_timeout": 7200,
            "max_concurrent_tasks": 10,
            "export_formats": ["pdf", "html", "json", "csv"],
            "default_export_format": "html",
            "case_retention_days": 365,
            "evidence_encryption": True,
            "audit_logging": True,
            "privacy_settings": {
                "anonymous_mode": True,
                "clear_temp_files": True,
                "secure_deletion": True
            },
            "free_services": {
                "catbox_hosting": True,
                "google_search": True,
                "yandex_search": True,
                "bing_search": True,
                "tineye_search": True,
                "forensically": True,
                "fotoforensics": True
            }
        }
        
        try:
            if self.config_file.exists():
                with open(self.config_file, 'r') as f:
                    config = json.load(f)
                # Merge with defaults for new settings
                for key, value in default_config.items():
                    if key not in config:
                        config[key] = value
                return config
            else:
                self.save_config(default_config)
                return default_config
        except Exception as e:
            print(f"Config load error: {e}")
            return default_config
    
    def save_config(self, config=None):
        """Save configuration to file"""
        if config is None:
            config = self.config
        
        try:
            with open(self.config_file, 'w') as f:
                json.dump(config, f, indent=4)
        except Exception as e:
            print(f"Config save error: {e}")
    
    def get(self, key, default=None):
        """Get configuration value"""
        return self.config.get(key, default)
    
    def set(self, key, value):
        """Set configuration value"""
        self.config[key] = value
        self.save_config()