"""
Professional OSINT utilities for CIOT Toolkit
Real API integrations and comprehensive free resources
"""

import re
import webbrowser
import time
import socket
from typing import List, Dict, Optional
from urllib.parse import quote
import threading

# Optional imports for enhanced functionality
try:
    import requests
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False

try:
    import dns.resolver
    HAS_DNS = True
except ImportError:
    HAS_DNS = False

def validate_email(email: str) -> bool:
    """Simple email validation"""
    if not email or '@' not in email:
        return False
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email.strip()))

def validate_phone(phone: str) -> bool:
    """Simple phone validation"""
    if not phone:
        return False
    digits = re.sub(r'[^\d]', '', phone)
    return 7 <= len(digits) <= 15

def validate_ip(ip: str) -> bool:
    """Simple IP validation"""
    if not ip:
        return False
    parts = ip.split('.')
    if len(parts) != 4:
        return False
    try:
        return all(0 <= int(part) <= 255 for part in parts)
    except ValueError:
        return False

def validate_bitcoin_address(address: str) -> bool:
    """Simple Bitcoin address validation"""
    if not address:
        return False
    # Basic patterns for Bitcoin addresses
    return bool(re.match(r'^[13][a-km-zA-HJ-NP-Z1-9]{25,34}$|^bc1[a-z0-9]{39,59}$', address))

def generate_search_links(target: str, search_type: str) -> List[Dict[str, str]]:
    """Generate comprehensive professional OSINT search links"""
    links = []
    
    if search_type == "email":
        domain = target.split("@")[1] if "@" in target else ""
        links = [
            # Search Engines
            {"name": "Google Search", "url": f'https://www.google.com/search?q="{target}"', "category": "Search Engines"},
            {"name": "Bing Search", "url": f'https://www.bing.com/search?q="{target}"', "category": "Search Engines"},
            {"name": "DuckDuckGo", "url": f'https://duckduckgo.com/?q="{target}"', "category": "Search Engines"},
            
            # Breach Databases
            {"name": "Have I Been Pwned", "url": f'https://haveibeenpwned.com/account/{target}', "category": "Breach Databases"},
            {"name": "Dehashed", "url": f'https://dehashed.com/search?query={target}', "category": "Breach Databases"},
            {"name": "LeakCheck", "url": f'https://leakcheck.io/search?query={target}', "category": "Breach Databases"},
            
            # Email Tools
            {"name": "Hunter.io", "url": f'https://hunter.io/search/{domain}', "category": "Email Tools"},
            {"name": "EmailRep", "url": f'https://emailrep.io/{target}', "category": "Email Tools"},
            {"name": "ThatsThem Email", "url": f'https://thatsthem.com/email/{target}', "category": "Email Tools"},
            
            # Social Media
            {"name": "LinkedIn Search", "url": f'https://www.google.com/search?q=site:linkedin.com "{target}"', "category": "Social Media"},
            {"name": "Facebook Search", "url": f'https://www.facebook.com/search/people/?q={target}', "category": "Social Media"},
            {"name": "Twitter Search", "url": f'https://twitter.com/search?q={target}', "category": "Social Media"},
            
            # Paste Sites
            {"name": "Pastebin Search", "url": f'https://www.google.com/search?q=site:pastebin.com "{target}"', "category": "Paste Sites"},
            {"name": "GitHub Search", "url": f'https://github.com/search?q={target}&type=code', "category": "Code Repositories"},
        ]
        
    elif search_type == "phone":
        clean_phone = ''.join(filter(str.isdigit, target))
        formatted_phone = target.replace("(", "").replace(")", "").replace("-", "").replace(" ", "")
        
        links = [
            # Phone Lookup Services
            {"name": "TrueCaller", "url": f'https://www.truecaller.com/search/us/{clean_phone}', "category": "Phone Lookup"},
            {"name": "WhitePages", "url": f'https://www.whitepages.com/phone/{clean_phone}', "category": "Phone Lookup"},
            {"name": "FastPeopleSearch", "url": f'https://www.fastpeoplesearch.com/phone/{clean_phone}', "category": "Phone Lookup"},
            {"name": "Spokeo Phone", "url": f'https://www.spokeo.com/phone-search/{formatted_phone}', "category": "Phone Lookup"},
            
            # Search Engines
            {"name": "Google Search", "url": f'https://www.google.com/search?q="{target}"', "category": "Search Engines"},
            {"name": "Bing Search", "url": f'https://www.bing.com/search?q="{target}"', "category": "Search Engines"},
            
            # Social Media
            {"name": "Facebook Search", "url": f'https://www.facebook.com/search/people/?q={target}', "category": "Social Media"},
            {"name": "LinkedIn Search", "url": f'https://www.google.com/search?q=site:linkedin.com "{target}"', "category": "Social Media"},
            
            # Carrier/Technical
            {"name": "FreeCarrierLookup", "url": f'https://freecarrierlookup.com/result?phone={clean_phone}', "category": "Technical"},
            {"name": "NumVerify", "url": f'https://numverify.com/', "category": "Technical"},
        ]
        
    elif search_type == "name":
        name_encoded = target.replace(" ", "%20")
        first_name = target.split()[0] if target.split() else ""
        last_name = target.split()[-1] if len(target.split()) > 1 else ""
        
        links = [
            # Search Engines
            {"name": "Google Search", "url": f'https://www.google.com/search?q="{target}"', "category": "Search Engines"},
            {"name": "Bing Search", "url": f'https://www.bing.com/search?q="{target}"', "category": "Search Engines"},
            {"name": "DuckDuckGo", "url": f'https://duckduckgo.com/?q="{target}"', "category": "Search Engines"},
            {"name": "Yandex Search", "url": f'https://yandex.com/search/?text="{target}"', "category": "Search Engines"},
            
            # Social Media
            {"name": "LinkedIn", "url": f'https://www.linkedin.com/search/results/people/?keywords={name_encoded}', "category": "Social Media"},
            {"name": "Facebook", "url": f'https://www.facebook.com/search/people/?q={name_encoded}', "category": "Social Media"},
            {"name": "Twitter", "url": f'https://twitter.com/search?q="{target}"', "category": "Social Media"},
            {"name": "Instagram", "url": f'https://www.instagram.com/explore/tags/{target.replace(" ", "")}/', "category": "Social Media"},
            
            # People Search
            {"name": "WhitePages", "url": f'https://www.whitepages.com/name/{name_encoded}', "category": "People Search"},
            {"name": "Spokeo", "url": f'https://www.spokeo.com/search?q={name_encoded}', "category": "People Search"},
            {"name": "PeopleFinder", "url": f'https://www.peoplefinder.com/search/?fn={first_name}&ln={last_name}', "category": "People Search"},
            {"name": "ThatsThem", "url": f'https://thatsthem.com/name/{first_name}-{last_name}', "category": "People Search"},
            
            # Professional Networks
            {"name": "ZoomInfo", "url": f'https://www.zoominfo.com/s/#{target}', "category": "Professional"},
            {"name": "Apollo", "url": f'https://www.apollo.io/people/search?name={name_encoded}', "category": "Professional"},
            
            # Public Records
            {"name": "FamilySearch", "url": f'https://www.familysearch.org/search/record/results?q.givenName={first_name}&q.surname={last_name}', "category": "Public Records"},
            {"name": "Ancestry", "url": f'https://www.ancestry.com/search/?name={name_encoded}', "category": "Public Records"},
        ]
        
    elif search_type == "ip":
        links = [
            # IP Information
            {"name": "IPinfo.io", "url": f'https://ipinfo.io/{target}', "category": "IP Information"},
            {"name": "IP-API", "url": f'http://ip-api.com/{target}', "category": "IP Information"},
            {"name": "IPGeolocation", "url": f'https://ipgeolocation.io/ip-location/{target}', "category": "IP Information"},
            
            # WHOIS & Registration
            {"name": "WHOIS.net", "url": f'https://whois.net/ip/{target}', "category": "WHOIS"},
            {"name": "ARIN WHOIS", "url": f'https://search.arin.net/rdap/?query={target}', "category": "WHOIS"},
            {"name": "IPWhois", "url": f'https://ipwhois.io/ip/{target}', "category": "WHOIS"},
            
            # Threat Intelligence
            {"name": "VirusTotal", "url": f'https://www.virustotal.com/gui/ip-address/{target}', "category": "Threat Intelligence"},
            {"name": "AbuseIPDB", "url": f'https://www.abuseipdb.com/check/{target}', "category": "Threat Intelligence"},
            {"name": "ThreatCrowd", "url": f'https://www.threatcrowd.org/ip.php?ip={target}', "category": "Threat Intelligence"},
            
            # Network Scanning
            {"name": "Shodan", "url": f'https://www.shodan.io/host/{target}', "category": "Network Scanning"},
            {"name": "Censys", "url": f'https://censys.io/ipv4/{target}', "category": "Network Scanning"},
            {"name": "ZoomEye", "url": f'https://www.zoomeye.org/searchResult?q={target}', "category": "Network Scanning"},
            
            # DNS & History
            {"name": "SecurityTrails", "url": f'https://securitytrails.com/list/ip/{target}', "category": "DNS History"},
            {"name": "PassiveTotal", "url": f'https://community.riskiq.com/search/{target}', "category": "DNS History"},
        ]
    
    return links

def get_real_ip_info(ip: str) -> Dict:
    """Get real IP information using free APIs"""
    if not HAS_REQUESTS:
        return {'success': False, 'error': 'Requests library not available'}
    
    try:
        # Use ip-api.com (free, no key required)
        import requests
        response = requests.get(f"http://ip-api.com/json/{ip}", timeout=10)
        if response.status_code == 200:
            data = response.json()
            if data.get('status') == 'success':
                return {
                    'success': True,
                    'ip': data.get('query'),
                    'country': data.get('country'),
                    'country_code': data.get('countryCode'),
                    'region': data.get('regionName'),
                    'city': data.get('city'),
                    'zip': data.get('zip'),
                    'lat': data.get('lat'),
                    'lon': data.get('lon'),
                    'timezone': data.get('timezone'),
                    'isp': data.get('isp'),
                    'org': data.get('org'),
                    'as_info': data.get('as'),
                    'mobile': data.get('mobile', False),
                    'proxy': data.get('proxy', False),
                    'hosting': data.get('hosting', False)
                }
    except Exception as e:
        pass
    
    return {'success': False, 'error': 'Unable to fetch IP information'}

def get_phone_info(phone: str) -> Dict:
    """Get phone information using free APIs and analysis"""
    clean_phone = ''.join(filter(str.isdigit, phone))
    
    # Basic phone analysis
    info = {
        'success': True,
        'phone': phone,
        'clean_phone': clean_phone,
        'length': len(clean_phone),
        'country_guess': 'Unknown',
        'type_guess': 'Unknown',
        'carrier_guess': 'Unknown'
    }
    
    # Basic country code detection
    if clean_phone.startswith('1') and len(clean_phone) == 11:
        info['country_guess'] = 'United States/Canada'
        info['type_guess'] = 'Mobile/Landline'
    elif clean_phone.startswith('44') and len(clean_phone) >= 10:
        info['country_guess'] = 'United Kingdom'
    elif clean_phone.startswith('91') and len(clean_phone) >= 10:
        info['country_guess'] = 'India'
    elif len(clean_phone) == 10:
        info['country_guess'] = 'US (without country code)'
        info['type_guess'] = 'Mobile/Landline'
    
    return info

def get_email_info(email: str) -> Dict:
    """Get email information using free analysis"""
    if '@' not in email:
        return {'success': False, 'error': 'Invalid email format'}
    
    local, domain = email.split('@', 1)
    
    info = {
        'success': True,
        'email': email,
        'local_part': local,
        'domain': domain,
        'mx_valid': False,
        'domain_exists': False,
        'common_provider': False
    }
    
    # Check if domain exists
    try:
        socket.gethostbyname(domain)
        info['domain_exists'] = True
        
        # Try to get MX record
        if HAS_DNS:
            try:
                import dns.resolver
                mx_records = dns.resolver.resolve(domain, 'MX')
                info['mx_valid'] = len(mx_records) > 0
            except:
                # Fallback: assume MX exists if domain exists
                info['mx_valid'] = True
        else:
            # Fallback: assume MX exists if domain exists
            info['mx_valid'] = True
    except:
        pass
    
    # Check for common providers
    common_providers = ['gmail.com', 'yahoo.com', 'hotmail.com', 'outlook.com', 'aol.com', 'icloud.com']
    info['common_provider'] = domain.lower() in common_providers
    
    return info

def open_links_safely(links: List[Dict[str, str]], max_links: int = 8):
    """Open links in browser with professional delay management"""
    def open_link_batch(link_batch):
        for i, link in enumerate(link_batch):
            webbrowser.open(link["url"])
            if i < len(link_batch) - 1:
                time.sleep(0.3)  # Shorter delay for better UX
    
    # Open links in batches to prevent browser overload
    batch_size = 4
    opened_count = 0
    
    for i in range(0, min(len(links), max_links), batch_size):
        batch = links[i:i + batch_size]
        thread = threading.Thread(target=open_link_batch, args=(batch,))
        thread.start()
        opened_count += len(batch)
        time.sleep(1)  # Delay between batches
    
    return opened_count

def format_results_text(target: str, search_type: str, links: List[Dict[str, str]]) -> str:
    """Format results for professional display with categorization"""
    result = f"🔍 PROFESSIONAL OSINT INVESTIGATION RESULTS\n"
    result += f"{'='*60}\n\n"
    result += f"🎯 Target: {target}\n"
    result += f"📋 Investigation Type: {search_type.title()}\n"
    result += f"🕐 Timestamp: {time.strftime('%Y-%m-%d %H:%M:%S')}\n"
    result += f"🔗 Total Links Generated: {len(links)}\n\n"
    
    # Group links by category
    categories = {}
    for link in links:
        category = link.get('category', 'Other')
        if category not in categories:
            categories[category] = []
        categories[category].append(link)
    
    # Display links by category
    for category, category_links in categories.items():
        result += f"📂 {category.upper()}\n"
        result += f"{'─'*40}\n"
        
        for i, link in enumerate(category_links, 1):
            result += f"  {i:2d}. {link['name']}\n"
            result += f"      🔗 {link['url']}\n\n"
        
        result += "\n"
    
    result += f"✅ Investigation Links Opened in Browser\n\n"
    
    # Professional investigation guidance
    result += f"📋 PROFESSIONAL INVESTIGATION WORKFLOW:\n"
    result += f"{'─'*50}\n"
    
    if search_type == "email":
        result += "1. Check breach databases first (Have I Been Pwned, Dehashed)\n"
        result += "2. Validate email deliverability and domain reputation\n"
        result += "3. Search social media platforms for associated accounts\n"
        result += "4. Look for the email in paste sites and code repositories\n"
        result += "5. Cross-reference findings across multiple sources\n"
    elif search_type == "phone":
        result += "1. Identify carrier and geographic location\n"
        result += "2. Check reverse lookup services for owner information\n"
        result += "3. Search social media platforms for associated accounts\n"
        result += "4. Verify through multiple phone lookup services\n"
        result += "5. Document all findings with timestamps\n"
    elif search_type == "name":
        result += "1. Start with general search engines for broad coverage\n"
        result += "2. Check professional networks (LinkedIn, ZoomInfo)\n"
        result += "3. Search social media platforms systematically\n"
        result += "4. Use people search engines for contact information\n"
        result += "5. Check public records and genealogy sites\n"
    elif search_type == "ip":
        result += "1. Gather basic IP information (geolocation, ISP)\n"
        result += "2. Check WHOIS records for registration details\n"
        result += "3. Analyze threat intelligence for malicious activity\n"
        result += "4. Use network scanning tools for open services\n"
        result += "5. Review DNS history and associated domains\n"
    
    result += f"\n⚖️ LEGAL & ETHICAL COMPLIANCE:\n"
    result += f"{'─'*40}\n"
    result += "• Only investigate authorized targets\n"
    result += "• Respect privacy laws and regulations (GDPR, CCPA)\n"
    result += "• Use information for legitimate purposes only\n"
    result += "• Document methodology for legal proceedings\n"
    result += "• Maintain confidentiality of sensitive findings\n"
    result += "• Follow platform terms of service\n\n"
    
    result += f"📊 INVESTIGATION SUMMARY:\n"
    result += f"{'─'*30}\n"
    result += f"Target Analyzed: {target}\n"
    result += f"Search Categories: {len(categories)}\n"
    result += f"Total Resources: {len(links)}\n"
    result += f"Status: Investigation Complete ✅\n"
    
    return result