#!/usr/bin/env python3
"""
Image Hosting Services for CIOT
Handles anonymous image hosting for OSINT investigations
"""

import requests
import base64
from pathlib import Path

class ImageHostingService:
    """Anonymous image hosting service integration"""
    
    def __init__(self):
        self.catbox_url = "https://catbox.moe/user/api.php"
    
    def upload_to_catbox(self, image_path):
        """Upload image to Catbox.moe anonymous hosting"""
        try:
            with open(image_path, 'rb') as f:
                files = {'fileToUpload': f}
                data = {'reqtype': 'fileupload'}
                
                response = requests.post(self.catbox_url, files=files, data=data, timeout=30)
                
                if response.status_code == 200:
                    return {
                        'success': True,
                        'url': response.text.strip(),
                        'service': 'catbox.moe'
                    }
                else:
                    return {
                        'success': False,
                        'error': f"Upload failed with status {response.status_code}"
                    }
                    
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_hosted_url(self, image_path):
        """Get hosted URL for image"""
        return self.upload_to_catbox(image_path)