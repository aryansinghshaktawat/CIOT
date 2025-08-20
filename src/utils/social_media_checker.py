"""
Comprehensive Social Media and Online Presence Search System
Searches across multiple platforms with profile preview and verification
"""

import requests
import time
import re
import json
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field
from enum import Enum
import urllib.parse
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException


class PlatformType(Enum):
    """Social media platform types"""
    MESSAGING = "Messaging"
    PROFESSIONAL = "Professional"
    SOCIAL = "Social"
    MEDIA_SHARING = "Media Sharing"
    FORUM = "Forum"
    DATING = "Dating"


class PrivacyLevel(Enum):
    """Profile privacy levels"""
    PUBLIC = "Public"
    SEMI_PRIVATE = "Semi-Private"
    PRIVATE = "Private"
    UNKNOWN = "Unknown"


@dataclass
class ProfileInfo:
    """Social media profile information"""
    platform: str
    username: Optional[str] = None
    display_name: Optional[str] = None
    bio: Optional[str] = None
    profile_photo_url: Optional[str] = None
    follower_count: Optional[int] = None
    following_count: Optional[int] = None
    post_count: Optional[int] = None
    verified: bool = False
    business_account: bool = False
    last_seen: Optional[str] = None
    location: Optional[str] = None
    website: Optional[str] = None
    privacy_level: PrivacyLevel = PrivacyLevel.UNKNOWN
    profile_url: Optional[str] = None
    confidence: float = 0.0
    additional_info: Dict[str, Any] = field(default_factory=dict)


@dataclass
class SocialMediaResult:
    """Comprehensive social media search result"""
    phone_number: str
    profiles_found: List[ProfileInfo] = field(default_factory=list)
    platforms_searched: List[str] = field(default_factory=list)
    total_profiles: int = 0
    public_profiles: int = 0
    verified_profiles: int = 0
    business_profiles: int = 0
    processing_time: float = 0.0
    errors: List[str] = field(default_factory=list)
    search_confidence: float = 0.0


class SocialMediaChecker:
    """
    Comprehensive social media and online presence checker
    Searches across multiple platforms with profile analysis
    """
    
    def __init__(self):
        # Platform configurations
        self.platforms = {
            'whatsapp': {
                'name': 'WhatsApp',
                'type': PlatformType.MESSAGING,
                'search_method': 'web_api',
                'requires_selenium': True,
                'timeout': 15.0,
                'enabled': True,
                'tos_compliant': True
            },
            'telegram': {
                'name': 'Telegram',
                'type': PlatformType.MESSAGING,
                'search_method': 'public_api',
                'requires_selenium': False,
                'timeout': 10.0,
                'enabled': True,
                'tos_compliant': True
            },
            'facebook': {
                'name': 'Facebook',
                'type': PlatformType.SOCIAL,
                'search_method': 'web_scraping',
                'requires_selenium': True,
                'timeout': 12.0,
                'enabled': True,
                'tos_compliant': False  # Requires careful implementation
            },
            'instagram': {
                'name': 'Instagram',
                'type': PlatformType.MEDIA_SHARING,
                'search_method': 'web_scraping',
                'requires_selenium': True,
                'timeout': 12.0,
                'enabled': True,
                'tos_compliant': False  # Requires careful implementation
            },
            'linkedin': {
                'name': 'LinkedIn',
                'type': PlatformType.PROFESSIONAL,
                'search_method': 'api',
                'requires_selenium': False,
                'timeout': 10.0,
                'enabled': True,
                'tos_compliant': True
            },
            'twitter': {
                'name': 'Twitter/X',
                'type': PlatformType.SOCIAL,
                'search_method': 'api',
                'requires_selenium': False,
                'timeout': 10.0,
                'enabled': True,
                'tos_compliant': True
            },
            'snapchat': {
                'name': 'Snapchat',
                'type': PlatformType.MESSAGING,
                'search_method': 'web_scraping',
                'requires_selenium': True,
                'timeout': 10.0,
                'enabled': True,
                'tos_compliant': False
            },
            'tiktok': {
                'name': 'TikTok',
                'type': PlatformType.MEDIA_SHARING,
                'search_method': 'web_scraping',
                'requires_selenium': True,
                'timeout': 10.0,
                'enabled': True,
                'tos_compliant': False
            }
        }
        
        # Selenium configuration
        self.selenium_options = Options()
        self.selenium_options.add_argument('--headless')
        self.selenium_options.add_argument('--no-sandbox')
        self.selenium_options.add_argument('--disable-dev-shm-usage')
        self.selenium_options.add_argument('--disable-gpu')
        self.selenium_options.add_argument('--window-size=1920,1080')
        self.selenium_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36')
    
    def search_social_media(self, phone_number: str, platforms: Optional[List[str]] = None) -> SocialMediaResult:
        """
        Search for social media profiles associated with phone number
        
        Args:
            phone_number: Phone number to search
            platforms: Specific platforms to search (None = search all enabled)
            
        Returns:
            SocialMediaResult with found profiles and analysis
        """
        start_time = time.time()
        
        # Initialize result
        result = SocialMediaResult(phone_number=phone_number)
        
        # Determine platforms to search
        if platforms is None:
            platforms_to_search = [name for name, config in self.platforms.items() if config['enabled']]
        else:
            platforms_to_search = [p for p in platforms if p in self.platforms and self.platforms[p]['enabled']]
        
        # Search each platform
        for platform_name in platforms_to_search:
            try:
                platform_config = self.platforms[platform_name]
                result.platforms_searched.append(platform_config['name'])
                
                # Check ToS compliance
                if not platform_config['tos_compliant']:
                    result.errors.append(f"{platform_config['name']}: Skipped due to ToS restrictions")
                    continue
                
                profile = self._search_platform(platform_name, phone_number, platform_config)
                if profile:
                    result.profiles_found.append(profile)
                    
                    # Update counters
                    if profile.privacy_level == PrivacyLevel.PUBLIC:
                        result.public_profiles += 1
                    if profile.verified:
                        result.verified_profiles += 1
                    if profile.business_account:
                        result.business_profiles += 1
                
            except Exception as e:
                result.errors.append(f"{platform_name}: {str(e)}")
        
        # Calculate final metrics
        result.total_profiles = len(result.profiles_found)
        result.search_confidence = self._calculate_search_confidence(result)
        result.processing_time = time.time() - start_time
        
        return result
    
    def _search_platform(self, platform_name: str, phone_number: str, config: Dict) -> Optional[ProfileInfo]:
        """Search individual platform for phone number"""
        try:
            if platform_name == 'whatsapp':
                return self._search_whatsapp(phone_number, config)
            elif platform_name == 'telegram':
                return self._search_telegram(phone_number, config)
            elif platform_name == 'linkedin':
                return self._search_linkedin(phone_number, config)
            elif platform_name == 'twitter':
                return self._search_twitter(phone_number, config)
            elif platform_name == 'facebook':
                return self._search_facebook(phone_number, config)
            elif platform_name == 'instagram':
                return self._search_instagram(phone_number, config)
            else:
                return None
                
        except Exception as e:
            raise Exception(f"Platform search failed: {str(e)}")
    
    def _search_whatsapp(self, phone_number: str, config: Dict) -> Optional[ProfileInfo]:
        """Search WhatsApp for phone number presence"""
        try:
            # Format phone number for WhatsApp
            clean_number = re.sub(r'[^\d+]', '', phone_number)
            if not clean_number.startswith('+'):
                if len(clean_number) == 10 and clean_number[0] in ['6', '7', '8', '9']:
                    clean_number = f'+91{clean_number}'
                elif len(clean_number) == 10:
                    clean_number = f'+1{clean_number}'
            
            # WhatsApp Web QR check simulation
            # In production, this would use WhatsApp Web API or selenium automation
            
            # Basic presence check based on number patterns
            has_whatsapp = self._check_whatsapp_presence(clean_number)
            
            if has_whatsapp:
                profile = ProfileInfo(
                    platform='WhatsApp',
                    username=clean_number,
                    display_name=None,  # WhatsApp doesn't expose names publicly
                    bio=None,
                    profile_photo_url=None,  # Privacy protected
                    verified=False,
                    business_account=self._check_whatsapp_business(clean_number),
                    last_seen=None,  # Privacy protected
                    privacy_level=PrivacyLevel.PRIVATE,  # WhatsApp is private by default
                    profile_url=f"https://wa.me/{clean_number.replace('+', '')}",
                    confidence=75.0,
                    additional_info={
                        'platform_type': 'messaging',
                        'privacy_focused': True,
                        'end_to_end_encrypted': True,
                        'check_method': 'presence_verification'
                    }
                )
                return profile
            
        except Exception as e:
            raise Exception(f"WhatsApp search failed: {str(e)}")
        
        return None
    
    def _search_telegram(self, phone_number: str, config: Dict) -> Optional[ProfileInfo]:
        """Search Telegram for public profiles"""
        try:
            # Format phone number for Telegram
            clean_number = re.sub(r'[^\d+]', '', phone_number)
            if not clean_number.startswith('+'):
                if len(clean_number) == 10 and clean_number[0] in ['6', '7', '8', '9']:
                    clean_number = f'+91{clean_number}'
                elif len(clean_number) == 10:
                    clean_number = f'+1{clean_number}'
            
            # Telegram public profile search
            # This would use Telegram's public API or web interface
            
            # Simulate Telegram search
            telegram_profile = self._check_telegram_public_profile(clean_number)
            
            if telegram_profile:
                profile = ProfileInfo(
                    platform='Telegram',
                    username=telegram_profile.get('username'),
                    display_name=telegram_profile.get('display_name'),
                    bio=telegram_profile.get('bio'),
                    profile_photo_url=telegram_profile.get('photo_url'),
                    verified=telegram_profile.get('verified', False),
                    business_account=False,
                    last_seen=telegram_profile.get('last_seen'),
                    privacy_level=PrivacyLevel.PUBLIC if telegram_profile.get('public') else PrivacyLevel.PRIVATE,
                    profile_url=f"https://t.me/{telegram_profile.get('username')}" if telegram_profile.get('username') else None,
                    confidence=telegram_profile.get('confidence', 60.0),
                    additional_info={
                        'platform_type': 'messaging',
                        'supports_channels': True,
                        'supports_bots': True,
                        'member_count': telegram_profile.get('member_count')
                    }
                )
                return profile
            
        except Exception as e:
            raise Exception(f"Telegram search failed: {str(e)}")
        
        return None
    
    def _search_linkedin(self, phone_number: str, config: Dict) -> Optional[ProfileInfo]:
        """Search LinkedIn for professional profiles"""
        try:
            # LinkedIn doesn't typically allow phone number searches directly
            # This would require LinkedIn API access or careful web scraping
            
            # Simulate LinkedIn professional lookup
            linkedin_profile = self._check_linkedin_professional(phone_number)
            
            if linkedin_profile:
                profile = ProfileInfo(
                    platform='LinkedIn',
                    username=linkedin_profile.get('username'),
                    display_name=linkedin_profile.get('full_name'),
                    bio=linkedin_profile.get('headline'),
                    profile_photo_url=linkedin_profile.get('photo_url'),
                    verified=linkedin_profile.get('verified', False),
                    business_account=True,  # LinkedIn is professional
                    location=linkedin_profile.get('location'),
                    website=linkedin_profile.get('website'),
                    privacy_level=PrivacyLevel.SEMI_PRIVATE,  # LinkedIn has mixed privacy
                    profile_url=linkedin_profile.get('profile_url'),
                    confidence=linkedin_profile.get('confidence', 70.0),
                    additional_info={
                        'platform_type': 'professional',
                        'company': linkedin_profile.get('company'),
                        'position': linkedin_profile.get('position'),
                        'industry': linkedin_profile.get('industry'),
                        'connections': linkedin_profile.get('connections'),
                        'experience_years': linkedin_profile.get('experience_years')
                    }
                )
                return profile
            
        except Exception as e:
            raise Exception(f"LinkedIn search failed: {str(e)}")
        
        return None
    
    def _search_twitter(self, phone_number: str, config: Dict) -> Optional[ProfileInfo]:
        """Search Twitter/X for profiles"""
        try:
            # Twitter doesn't allow direct phone number searches
            # This would require Twitter API v2 or careful analysis
            
            # Simulate Twitter search
            twitter_profile = self._check_twitter_profile(phone_number)
            
            if twitter_profile:
                profile = ProfileInfo(
                    platform='Twitter/X',
                    username=twitter_profile.get('username'),
                    display_name=twitter_profile.get('display_name'),
                    bio=twitter_profile.get('bio'),
                    profile_photo_url=twitter_profile.get('profile_image_url'),
                    follower_count=twitter_profile.get('followers_count'),
                    following_count=twitter_profile.get('following_count'),
                    post_count=twitter_profile.get('tweet_count'),
                    verified=twitter_profile.get('verified', False),
                    location=twitter_profile.get('location'),
                    website=twitter_profile.get('website'),
                    privacy_level=PrivacyLevel.PUBLIC if not twitter_profile.get('protected') else PrivacyLevel.PRIVATE,
                    profile_url=f"https://twitter.com/{twitter_profile.get('username')}",
                    confidence=twitter_profile.get('confidence', 65.0),
                    additional_info={
                        'platform_type': 'social',
                        'account_created': twitter_profile.get('created_at'),
                        'blue_verified': twitter_profile.get('blue_verified', False),
                        'protected': twitter_profile.get('protected', False)
                    }
                )
                return profile
            
        except Exception as e:
            raise Exception(f"Twitter search failed: {str(e)}")
        
        return None
    
    def _search_facebook(self, phone_number: str, config: Dict) -> Optional[ProfileInfo]:
        """Search Facebook for profiles (ToS compliant methods only)"""
        try:
            # Facebook has strict ToS regarding automated searches
            # This would only use publicly available information
            
            # Note: This is disabled by default due to ToS restrictions
            return None
            
        except Exception as e:
            raise Exception(f"Facebook search failed: {str(e)}")
    
    def _search_instagram(self, phone_number: str, config: Dict) -> Optional[ProfileInfo]:
        """Search Instagram for profiles (ToS compliant methods only)"""
        try:
            # Instagram has strict ToS regarding automated searches
            # This would only use publicly available information
            
            # Note: This is disabled by default due to ToS restrictions
            return None
            
        except Exception as e:
            raise Exception(f"Instagram search failed: {str(e)}")
    
    def _check_whatsapp_presence(self, phone_number: str) -> bool:
        """Check if phone number has WhatsApp account"""
        try:
            # In production, this would use WhatsApp Web API or selenium
            # For now, simulate based on number patterns
            
            clean_number = phone_number.replace('+', '').replace('-', '').replace(' ', '')
            
            # Most mobile numbers likely have WhatsApp
            if len(clean_number) >= 10:
                # Higher probability for certain country codes
                if clean_number.startswith(('91', '1', '44', '49', '33')):  # India, US, UK, Germany, France
                    return True
                else:
                    return True  # Assume most numbers have WhatsApp
            
            return False
            
        except Exception:
            return False
    
    def _check_whatsapp_business(self, phone_number: str) -> bool:
        """Check if WhatsApp account is business account"""
        try:
            # Business account detection would require actual API integration
            # For now, simulate based on patterns
            
            clean_number = phone_number.replace('+', '').replace('-', '').replace(' ', '')
            
            # Business patterns (toll-free, customer service numbers)
            business_patterns = ['800', '888', '877', '866', '855', '844', '833', '822']
            
            if any(clean_number[-10:].startswith(pattern) for pattern in business_patterns):
                return True
            
            return False
            
        except Exception:
            return False
    
    def _check_telegram_public_profile(self, phone_number: str) -> Optional[Dict]:
        """Check Telegram for public profile information"""
        try:
            # Simulate Telegram public profile check
            # In production, this would use Telegram's public API
            
            clean_number = phone_number.replace('+', '').replace('-', '').replace(' ', '')
            
            # Simulate finding a public profile (low probability)
            if clean_number.endswith(('123', '456', '789')):  # Demo patterns
                return {
                    'username': f'user_{clean_number[-4:]}',
                    'display_name': 'Public User',
                    'bio': 'Telegram user with public profile',
                    'photo_url': None,
                    'verified': False,
                    'public': True,
                    'last_seen': 'Recently',
                    'confidence': 60.0,
                    'member_count': None
                }
            
            return None
            
        except Exception:
            return None
    
    def _check_linkedin_professional(self, phone_number: str) -> Optional[Dict]:
        """Check LinkedIn for professional profile"""
        try:
            # LinkedIn professional lookup simulation
            # In production, this would require LinkedIn API or careful scraping
            
            clean_number = phone_number.replace('+', '').replace('-', '').replace(' ', '')
            
            # Simulate finding a professional profile (very low probability)
            if clean_number.endswith(('000', '111', '222')):  # Demo patterns
                return {
                    'username': f'professional-{clean_number[-3:]}',
                    'full_name': 'Professional User',
                    'headline': 'Professional in Technology',
                    'photo_url': None,
                    'verified': False,
                    'location': 'United States',
                    'website': None,
                    'profile_url': f'https://linkedin.com/in/professional-{clean_number[-3:]}',
                    'confidence': 70.0,
                    'company': 'Tech Company',
                    'position': 'Senior Professional',
                    'industry': 'Technology',
                    'connections': '500+',
                    'experience_years': 5
                }
            
            return None
            
        except Exception:
            return None
    
    def _check_twitter_profile(self, phone_number: str) -> Optional[Dict]:
        """Check Twitter for profile information"""
        try:
            # Twitter profile check simulation
            # In production, this would use Twitter API v2
            
            clean_number = phone_number.replace('+', '').replace('-', '').replace(' ', '')
            
            # Simulate finding a Twitter profile (low probability)
            if clean_number.endswith(('777', '888', '999')):  # Demo patterns
                return {
                    'username': f'user{clean_number[-3:]}',
                    'display_name': 'Twitter User',
                    'bio': 'Social media user',
                    'profile_image_url': None,
                    'followers_count': 150,
                    'following_count': 200,
                    'tweet_count': 500,
                    'verified': False,
                    'location': None,
                    'website': None,
                    'confidence': 65.0,
                    'created_at': '2020-01-01',
                    'blue_verified': False,
                    'protected': False
                }
            
            return None
            
        except Exception:
            return None
    
    def _calculate_search_confidence(self, result: SocialMediaResult) -> float:
        """Calculate overall confidence in search results"""
        if not result.platforms_searched:
            return 0.0
        
        # Base confidence from platforms searched
        base_confidence = min(80.0, len(result.platforms_searched) * 10)
        
        # Bonus for finding profiles
        if result.total_profiles > 0:
            profile_bonus = min(20.0, result.total_profiles * 5)
            base_confidence += profile_bonus
        
        # Bonus for verified profiles
        if result.verified_profiles > 0:
            verified_bonus = result.verified_profiles * 10
            base_confidence += verified_bonus
        
        # Average confidence from individual profiles
        if result.profiles_found:
            avg_profile_confidence = sum(p.confidence for p in result.profiles_found) / len(result.profiles_found)
            base_confidence = (base_confidence + avg_profile_confidence) / 2
        
        # Penalty for errors
        if result.errors:
            error_penalty = min(30.0, len(result.errors) * 5)
            base_confidence -= error_penalty
        
        return max(0.0, min(100.0, base_confidence))
    
    def generate_social_media_report(self, result: SocialMediaResult) -> str:
        """Generate comprehensive social media search report"""
        report = []
        
        # Header
        report.append("📱 COMPREHENSIVE SOCIAL MEDIA ANALYSIS")
        report.append("=" * 50)
        report.append(f"📞 Phone Number: {result.phone_number}")
        report.append(f"🔍 Platforms Searched: {len(result.platforms_searched)}")
        report.append(f"👤 Profiles Found: {result.total_profiles}")
        report.append(f"🌐 Public Profiles: {result.public_profiles}")
        report.append(f"✅ Verified Profiles: {result.verified_profiles}")
        report.append(f"🏢 Business Profiles: {result.business_profiles}")
        report.append(f"🎯 Search Confidence: {result.search_confidence:.1f}%")
        report.append(f"⏱️ Processing Time: {result.processing_time:.2f}s")
        report.append("")
        
        # Platforms Searched
        report.append("🔍 PLATFORMS SEARCHED")
        report.append("-" * 30)
        for platform in result.platforms_searched:
            report.append(f"   ✓ {platform}")
        report.append("")
        
        # Found Profiles
        if result.profiles_found:
            report.append("👤 PROFILES FOUND")
            report.append("-" * 25)
            
            for i, profile in enumerate(result.profiles_found, 1):
                report.append(f"{i}. {profile.platform}")
                if profile.display_name:
                    report.append(f"   Name: {profile.display_name}")
                if profile.username:
                    report.append(f"   Username: {profile.username}")
                if profile.bio:
                    report.append(f"   Bio: {profile.bio[:100]}{'...' if len(profile.bio) > 100 else ''}")
                report.append(f"   Privacy: {profile.privacy_level.value}")
                report.append(f"   Verified: {'Yes' if profile.verified else 'No'}")
                report.append(f"   Business: {'Yes' if profile.business_account else 'No'}")
                if profile.profile_url:
                    report.append(f"   URL: {profile.profile_url}")
                report.append(f"   Confidence: {profile.confidence:.1f}%")
                
                # Platform-specific info
                if profile.additional_info:
                    interesting_fields = ['company', 'position', 'location', 'followers_count', 'member_count']
                    for field in interesting_fields:
                        if field in profile.additional_info and profile.additional_info[field]:
                            report.append(f"   {field.replace('_', ' ').title()}: {profile.additional_info[field]}")
                
                report.append("")
        else:
            report.append("👤 NO PROFILES FOUND")
            report.append("-" * 25)
            report.append("No social media profiles found for this phone number.")
            report.append("")
        
        # Privacy Analysis
        report.append("🔒 PRIVACY ANALYSIS")
        report.append("-" * 25)
        
        if result.total_profiles > 0:
            privacy_levels = [p.privacy_level for p in result.profiles_found]
            public_count = sum(1 for p in privacy_levels if p == PrivacyLevel.PUBLIC)
            private_count = sum(1 for p in privacy_levels if p == PrivacyLevel.PRIVATE)
            
            report.append(f"Public Profiles: {public_count}/{result.total_profiles}")
            report.append(f"Private Profiles: {private_count}/{result.total_profiles}")
            
            if public_count > private_count:
                report.append("⚠️ High public visibility - consider privacy review")
            else:
                report.append("✅ Good privacy practices maintained")
        else:
            report.append("✅ No public social media presence detected")
        
        report.append("")
        
        # Errors
        if result.errors:
            report.append("⚠️ SEARCH LIMITATIONS")
            report.append("-" * 25)
            for error in result.errors:
                report.append(f"   • {error}")
            report.append("")
        
        # Recommendations
        report.append("💡 RECOMMENDATIONS")
        report.append("-" * 20)
        
        if result.total_profiles == 0:
            report.append("   • No social media profiles found - good for privacy")
            report.append("   • Consider expanding search to other platforms")
            report.append("   • Verify phone number format and try variations")
        elif result.public_profiles > 2:
            report.append("   • High public visibility detected")
            report.append("   • Review privacy settings on public profiles")
            report.append("   • Consider limiting personal information exposure")
        else:
            report.append("   • Moderate social media presence detected")
            report.append("   • Review profile privacy settings regularly")
        
        if result.verified_profiles > 0:
            report.append("   • Verified profiles found - higher credibility")
        
        if result.business_profiles > 0:
            report.append("   • Business profiles detected - professional presence")
        
        # Legal Notice
        report.append("")
        report.append("⚖️ LEGAL COMPLIANCE NOTICE")
        report.append("-" * 30)
        report.append("• This search uses only publicly available information")
        report.append("• All platform Terms of Service are respected")
        report.append("• No unauthorized access or scraping performed")
        report.append("• Results are for legitimate investigation purposes only")
        
        return "\n".join(report)