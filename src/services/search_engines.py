#!/usr/bin/env python3
"""
Search Engine Services for CIOT
Handles integration with various search engines for OSINT
"""

import requests
import urllib.parse
from typing import List, Dict

class SearchEngineService:
    """Search engine integration service"""
    
    def __init__(self):
        self.user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    
    def generate_google_search_url(self, query):
        """Generate Google search URL"""
        encoded_query = urllib.parse.quote(query)
        return f"https://www.google.com/search?q={encoded_query}"
    
    def generate_bing_search_url(self, query):
        """Generate Bing search URL"""
        encoded_query = urllib.parse.quote(query)
        return f"https://www.bing.com/search?q={encoded_query}"
    
    def generate_yandex_search_url(self, query):
        """Generate Yandex search URL"""
        encoded_query = urllib.parse.quote(query)
        return f"https://yandex.com/search/?text={encoded_query}"
    
    def generate_duckduckgo_search_url(self, query):
        """Generate DuckDuckGo search URL"""
        encoded_query = urllib.parse.quote(query)
        return f"https://duckduckgo.com/?q={encoded_query}"
    
    def get_all_search_urls(self, query):
        """Get search URLs from all engines"""
        return {
            'google': self.generate_google_search_url(query),
            'bing': self.generate_bing_search_url(query),
            'yandex': self.generate_yandex_search_url(query),
            'duckduckgo': self.generate_duckduckgo_search_url(query)
        }