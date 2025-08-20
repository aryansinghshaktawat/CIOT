#!/usr/bin/env python3
"""
Forensic Tools Services for CIOT
Handles integration with forensic analysis tools
"""

import requests
import urllib.parse
from typing import Dict, Optional

class ForensicToolsService:
    """Forensic tools integration service"""
    
    def __init__(self):
        self.user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    
    def get_forensically_url(self, image_url):
        """Generate Forensically.com analysis URL"""
        encoded_url = urllib.parse.quote(image_url)
        return f"https://29a.ch/photo-forensics/#level=1&algo=ela&url={encoded_url}"
    
    def get_fotoforensics_url(self, image_url):
        """Generate FotoForensics analysis URL"""
        encoded_url = urllib.parse.quote(image_url)
        return f"http://fotoforensics.com/analysis.php?fmt=ela&size=600&url={encoded_url}"
    
    def get_tineye_url(self, image_url):
        """Generate TinEye reverse search URL"""
        encoded_url = urllib.parse.quote(image_url)
        return f"https://tineye.com/search?url={encoded_url}"
    
    def get_google_images_url(self, image_url):
        """Generate Google Images reverse search URL"""
        encoded_url = urllib.parse.quote(image_url)
        return f"https://images.google.com/searchbyimage?image_url={encoded_url}"
    
    def get_yandex_images_url(self, image_url):
        """Generate Yandex Images reverse search URL"""
        encoded_url = urllib.parse.quote(image_url)
        return f"https://yandex.com/images/search?rpt=imageview&url={encoded_url}"
    
    def get_all_forensic_urls(self, image_url):
        """Get all forensic analysis URLs"""
        return {
            'forensically': self.get_forensically_url(image_url),
            'fotoforensics': self.get_fotoforensics_url(image_url),
            'tineye': self.get_tineye_url(image_url),
            'google_images': self.get_google_images_url(image_url),
            'yandex_images': self.get_yandex_images_url(image_url)
        }