#!/usr/bin/env python3
"""
Input validation utilities for CIOT OSINT Toolkit
Provides validation functions for various data types used in investigations
"""

import re
import ipaddress
# No typing import needed for basic bool return type

def validate_email(email: str) -> bool:
    """Validate email address format"""
    if not email or not email.strip():
        return False
    
    email = email.strip().lower()
    
    # Basic email regex pattern
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    
    if not re.match(email_pattern, email):
        return False
    
    # Check for common issues
    if email.count('@') != 1:
        return False
    
    local, domain = email.split('@')
    
    if len(local) > 64 or len(domain) > 253:
        return False
    
    return True

def validate_phone(phone: str) -> bool:
    """Validate phone number format"""
    if not phone or not phone.strip():
        return False
    
    # Remove all non-digit characters
    cleaned = re.sub(r'[^\d]', '', phone.strip())
    
    if not cleaned:
        return False
    
    # Check length (7-15 digits is reasonable for most phone numbers)
    if len(cleaned) < 7 or len(cleaned) > 15:
        return False
    
    return True

def validate_ip(ip: str) -> bool:
    """Validate IP address (IPv4 or IPv6)"""
    if not ip or not ip.strip():
        return False
    
    ip = ip.strip()
    
    try:
        # Try to parse as IP address
        ipaddress.ip_address(ip)
        return True
    except ValueError:
        return False

def validate_domain(domain: str) -> bool:
    """Validate domain name format"""
    if not domain or not domain.strip():
        return False
    
    domain = domain.strip().lower()
    
    # Remove protocol if present
    if domain.startswith(('http://', 'https://')):
        from urllib.parse import urlparse
        parsed = urlparse(domain)
        domain = parsed.netloc or parsed.path
    
    # Basic domain validation
    domain_pattern = r'^[a-zA-Z0-9]([a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?(\.[a-zA-Z0-9]([a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?)*$'
    
    if not re.match(domain_pattern, domain):
        return False
    
    if len(domain) > 253:
        return False
    
    # Check if domain has at least one dot
    if '.' not in domain:
        return False
    
    return True

def validate_bitcoin_address(address: str) -> bool:
    """Validate Bitcoin address format"""
    if not address or not address.strip():
        return False
    
    address = address.strip()
    
    # Bitcoin address patterns
    # Legacy (P2PKH): starts with 1, 26-35 characters
    # Script (P2SH): starts with 3, 26-35 characters  
    # Bech32 (P2WPKH/P2WSH): starts with bc1, 42 or 62 characters
    
    if re.match(r'^[13][a-km-zA-HJ-NP-Z1-9]{25,34}$', address):
        return True
    
    if re.match(r'^bc1[a-z0-9]{39,59}$', address):
        return True
    
    return False

def validate_onion_url(url: str) -> bool:
    """Validate .onion URL format"""
    if not url or not url.strip():
        return False
    
    url = url.strip().lower()
    
    # Remove protocol if present
    if url.startswith('http://'):
        url = url[7:]
    elif url.startswith('https://'):
        url = url[8:]
    
    # Remove path if present
    if '/' in url:
        url = url.split('/')[0]
    
    # V2 onion addresses: 16 characters + .onion
    v2_pattern = r'^[a-z2-7]{16}\.onion$'
    
    # V3 onion addresses: 56 characters + .onion
    v3_pattern = r'^[a-z2-7]{56}\.onion$'
    
    if re.match(v2_pattern, url) or re.match(v3_pattern, url):
        return True
    
    return False

def validate_full_name(name: str) -> bool:
    """Validate full name format"""
    if not name or not name.strip():
        return False
    
    name = name.strip()
    
    # Check for minimum length
    if len(name) < 2:
        return False
    
    # Check for maximum length
    if len(name) > 100:
        return False
    
    # Check for valid characters (letters, spaces, hyphens, apostrophes)
    if not re.match(r"^[a-zA-Z\s\-'\.]+$", name):
        return False
    
    # Check for at least one letter
    if not re.search(r'[a-zA-Z]', name):
        return False
    
    return True

def validate_username(username: str) -> bool:
    """Validate username format for social media searches"""
    if not username or not username.strip():
        return False
    
    username = username.strip()
    
    # Remove @ symbol if present
    if username.startswith('@'):
        username = username[1:]
    
    if not username:
        return False
    
    # Check length (most platforms: 1-30 characters)
    if len(username) < 1 or len(username) > 30:
        return False
    
    # Check for valid characters (alphanumeric, underscore, hyphen, dot)
    if not re.match(r'^[a-zA-Z0-9._-]+$', username):
        return False
    
    return True