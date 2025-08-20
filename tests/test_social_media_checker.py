"""
Unit tests for Social Media Checker
Tests social media search, profile analysis, and platform integration
"""

import unittest
import sys
import os
from unittest.mock import Mock, patch, MagicMock

# Add src directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from utils.social_media_checker import (
    SocialMediaChecker,
    PlatformType,
    PrivacyLevel,
    ProfileInfo,
    SocialMediaResult
)


class TestProfileInfo(unittest.TestCase):
    """Test cases for ProfileInfo dataclass"""
    
    def test_profile_info_creation(self):
        """Test ProfileInfo creation"""
        profile = ProfileInfo(
            platform="WhatsApp",
            username="+1234567890",
            display_name="Test User",
            bio="Test bio",
            verified=True,
            business_account=False,
            privacy_level=PrivacyLevel.PRIVATE,
            profile_url="https://wa.me/1234567890",
            confidence=85.0
        )
        
        self.assertEqual(profile.platform, "WhatsApp")
        self.assertEqual(profile.username, "+1234567890")
        self.assertEqual(profile.display_name, "Test User")
        self.assertEqual(profile.bio, "Test bio")
        self.assertTrue(profile.verified)
        self.assertFalse(profile.business_account)
        self.assertEqual(profile.privacy_level, PrivacyLevel.PRIVATE)
        self.assertEqual(profile.profile_url, "https://wa.me/1234567890")
        self.assertEqual(profile.confidence, 85.0)


class TestSocialMediaResult(unittest.TestCase):
    """Test cases for SocialMediaResult dataclass"""
    
    def test_social_media_result_creation(self):
        """Test SocialMediaResult creation"""
        profiles = [
            ProfileInfo(platform="WhatsApp", confidence=80.0),
            ProfileInfo(platform="Telegram", confidence=70.0, verified=True)
        ]
        
        result = SocialMediaResult(
            phone_number="+1234567890",
            profiles_found=profiles,
            platforms_searched=["WhatsApp", "Telegram"],
            total_profiles=2,
            public_profiles=1,
            verified_profiles=1,
            processing_time=2.5
        )
        
        self.assertEqual(result.phone_number, "+1234567890")
        self.assertEqual(len(result.profiles_found), 2)
        self.assertEqual(result.platforms_searched, ["WhatsApp", "Telegram"])
        self.assertEqual(result.total_profiles, 2)
        self.assertEqual(result.public_profiles, 1)
        self.assertEqual(result.verified_profiles, 1)
        self.assertEqual(result.processing_time, 2.5)


class TestSocialMediaChecker(unittest.TestCase):
    """Test cases for SocialMediaChecker class"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.checker = SocialMediaChecker()
        self.test_phone_us = '+15551234567'
        self.test_phone_indian = '+919876543210'
    
    def test_initialization(self):
        """Test SocialMediaChecker initialization"""
        self.assertIsInstance(self.checker, SocialMediaChecker)
        self.assertIn('whatsapp', self.checker.platforms)
        self.assertIn('telegram', self.checker.platforms)
        self.assertIn('linkedin', self.checker.platforms)
        self.assertIn('twitter', self.checker.platforms)
        
        # Check platform configurations
        whatsapp_config = self.checker.platforms['whatsapp']
        self.assertEqual(whatsapp_config['name'], 'WhatsApp')
        self.assertEqual(whatsapp_config['type'], PlatformType.MESSAGING)
        self.assertTrue(whatsapp_config['tos_compliant'])
    
    def test_platform_types(self):
        """Test platform type classifications"""
        self.assertEqual(self.checker.platforms['whatsapp']['type'], PlatformType.MESSAGING)
        self.assertEqual(self.checker.platforms['linkedin']['type'], PlatformType.PROFESSIONAL)
        self.assertEqual(self.checker.platforms['twitter']['type'], PlatformType.SOCIAL)
        self.assertEqual(self.checker.platforms['instagram']['type'], PlatformType.MEDIA_SHARING)
    
    def test_tos_compliance_flags(self):
        """Test Terms of Service compliance flags"""
        # ToS compliant platforms
        self.assertTrue(self.checker.platforms['whatsapp']['tos_compliant'])
        self.assertTrue(self.checker.platforms['telegram']['tos_compliant'])
        self.assertTrue(self.checker.platforms['linkedin']['tos_compliant'])
        self.assertTrue(self.checker.platforms['twitter']['tos_compliant'])
        
        # ToS restricted platforms
        self.assertFalse(self.checker.platforms['facebook']['tos_compliant'])
        self.assertFalse(self.checker.platforms['instagram']['tos_compliant'])
    
    def test_check_whatsapp_presence_mobile(self):
        """Test WhatsApp presence check for mobile numbers"""
        # Test various mobile number formats
        test_numbers = [
            '+15551234567',  # US mobile
            '+919876543210',  # Indian mobile
            '+447700900123',  # UK mobile
            '+4915112345678'  # German mobile
        ]
        
        for number in test_numbers:
            has_whatsapp = self.checker._check_whatsapp_presence(number)
            self.assertTrue(has_whatsapp, f"Mobile number {number} should likely have WhatsApp")
    
    def test_check_whatsapp_presence_invalid(self):
        """Test WhatsApp presence check for invalid numbers"""
        invalid_numbers = [
            '123',  # Too short
            'abc',  # Non-numeric
            '',     # Empty
        ]
        
        for number in invalid_numbers:
            has_whatsapp = self.checker._check_whatsapp_presence(number)
            self.assertFalse(has_whatsapp, f"Invalid number {number} should not have WhatsApp")
    
    def test_check_whatsapp_business_patterns(self):
        """Test WhatsApp business account detection"""
        # Test business number patterns
        business_numbers = [
            '+18005551234',  # Toll-free
            '+18885551234',  # Toll-free
            '+18775551234',  # Toll-free
        ]
        
        for number in business_numbers:
            is_business = self.checker._check_whatsapp_business(number)
            self.assertTrue(is_business, f"Number {number} should be detected as business")
        
        # Test regular numbers
        regular_numbers = [
            '+15551234567',  # Regular US
            '+919876543210'  # Regular Indian
        ]
        
        for number in regular_numbers:
            is_business = self.checker._check_whatsapp_business(number)
            self.assertFalse(is_business, f"Number {number} should not be detected as business")
    
    def test_search_whatsapp(self):
        """Test WhatsApp search functionality"""
        config = self.checker.platforms['whatsapp']
        
        # Test with mobile number that should have WhatsApp
        result = self.checker._search_whatsapp(self.test_phone_us, config)
        
        self.assertIsNotNone(result)
        self.assertIsInstance(result, ProfileInfo)
        self.assertEqual(result.platform, 'WhatsApp')
        self.assertIsNotNone(result.username)
        self.assertEqual(result.privacy_level, PrivacyLevel.PRIVATE)
        self.assertIsNotNone(result.profile_url)
        self.assertGreater(result.confidence, 70.0)
        self.assertIn('messaging', result.additional_info.get('platform_type', ''))
    
    def test_search_whatsapp_business(self):
        """Test WhatsApp business account detection"""
        config = self.checker.platforms['whatsapp']
        
        # Test with business number
        business_number = '+18005551234'
        result = self.checker._search_whatsapp(business_number, config)
        
        if result:  # If WhatsApp presence detected
            self.assertTrue(result.business_account)
    
    def test_check_telegram_public_profile(self):
        """Test Telegram public profile check"""
        # Test with demo pattern that should return profile
        demo_number = '+15551234123'  # Ends with 123
        profile = self.checker._check_telegram_public_profile(demo_number)
        
        self.assertIsNotNone(profile)
        self.assertIn('username', profile)
        self.assertIn('display_name', profile)
        self.assertIn('confidence', profile)
        self.assertTrue(profile['public'])
        
        # Test with number that shouldn't return profile
        regular_number = '+15551234567'
        profile = self.checker._check_telegram_public_profile(regular_number)
        
        self.assertIsNone(profile)
    
    def test_search_telegram(self):
        """Test Telegram search functionality"""
        config = self.checker.platforms['telegram']
        
        # Test with demo pattern
        demo_number = '+15551234123'
        result = self.checker._search_telegram(demo_number, config)
        
        self.assertIsNotNone(result)
        self.assertIsInstance(result, ProfileInfo)
        self.assertEqual(result.platform, 'Telegram')
        self.assertIsNotNone(result.username)
        self.assertEqual(result.privacy_level, PrivacyLevel.PUBLIC)
        self.assertIsNotNone(result.profile_url)
        self.assertGreater(result.confidence, 50.0)
    
    def test_check_linkedin_professional(self):
        """Test LinkedIn professional profile check"""
        # Test with demo pattern that should return profile
        demo_number = '+15551234000'  # Ends with 000
        profile = self.checker._check_linkedin_professional(demo_number)
        
        self.assertIsNotNone(profile)
        self.assertIn('username', profile)
        self.assertIn('full_name', profile)
        self.assertIn('company', profile)
        self.assertIn('position', profile)
        self.assertGreater(profile['confidence'], 60.0)
        
        # Test with number that shouldn't return profile
        regular_number = '+15551234567'
        profile = self.checker._check_linkedin_professional(regular_number)
        
        self.assertIsNone(profile)
    
    def test_search_linkedin(self):
        """Test LinkedIn search functionality"""
        config = self.checker.platforms['linkedin']
        
        # Test with demo pattern
        demo_number = '+15551234000'
        result = self.checker._search_linkedin(demo_number, config)
        
        self.assertIsNotNone(result)
        self.assertIsInstance(result, ProfileInfo)
        self.assertEqual(result.platform, 'LinkedIn')
        self.assertTrue(result.business_account)  # LinkedIn is professional
        self.assertEqual(result.privacy_level, PrivacyLevel.SEMI_PRIVATE)
        self.assertIn('company', result.additional_info)
        self.assertIn('position', result.additional_info)
    
    def test_check_twitter_profile(self):
        """Test Twitter profile check"""
        # Test with demo pattern that should return profile
        demo_number = '+15551234777'  # Ends with 777
        profile = self.checker._check_twitter_profile(demo_number)
        
        self.assertIsNotNone(profile)
        self.assertIn('username', profile)
        self.assertIn('display_name', profile)
        self.assertIn('followers_count', profile)
        self.assertIn('tweet_count', profile)
        self.assertGreater(profile['confidence'], 60.0)
        
        # Test with number that shouldn't return profile
        regular_number = '+15551234567'
        profile = self.checker._check_twitter_profile(regular_number)
        
        self.assertIsNone(profile)
    
    def test_search_twitter(self):
        """Test Twitter search functionality"""
        config = self.checker.platforms['twitter']
        
        # Test with demo pattern
        demo_number = '+15551234777'
        result = self.checker._search_twitter(demo_number, config)
        
        self.assertIsNotNone(result)
        self.assertIsInstance(result, ProfileInfo)
        self.assertEqual(result.platform, 'Twitter/X')
        self.assertIsNotNone(result.follower_count)
        self.assertIsNotNone(result.post_count)
        self.assertEqual(result.privacy_level, PrivacyLevel.PUBLIC)
    
    def test_search_facebook_tos_restriction(self):
        """Test Facebook search respects ToS restrictions"""
        config = self.checker.platforms['facebook']
        
        # Facebook search should return None due to ToS restrictions
        result = self.checker._search_facebook(self.test_phone_us, config)
        self.assertIsNone(result)
    
    def test_search_instagram_tos_restriction(self):
        """Test Instagram search respects ToS restrictions"""
        config = self.checker.platforms['instagram']
        
        # Instagram search should return None due to ToS restrictions
        result = self.checker._search_instagram(self.test_phone_us, config)
        self.assertIsNone(result)
    
    def test_calculate_search_confidence_no_platforms(self):
        """Test confidence calculation with no platforms searched"""
        result = SocialMediaResult(phone_number="+1234567890")
        confidence = self.checker._calculate_search_confidence(result)
        self.assertEqual(confidence, 0.0)
    
    def test_calculate_search_confidence_with_profiles(self):
        """Test confidence calculation with found profiles"""
        profiles = [
            ProfileInfo(platform="WhatsApp", confidence=80.0),
            ProfileInfo(platform="Telegram", confidence=70.0, verified=True)
        ]
        
        result = SocialMediaResult(
            phone_number="+1234567890",
            profiles_found=profiles,
            platforms_searched=["WhatsApp", "Telegram"],
            total_profiles=2,
            verified_profiles=1
        )
        
        confidence = self.checker._calculate_search_confidence(result)
        self.assertGreater(confidence, 50.0)  # Should be decent with profiles and verified account
    
    def test_calculate_search_confidence_with_errors(self):
        """Test confidence calculation with errors"""
        result = SocialMediaResult(
            phone_number="+1234567890",
            platforms_searched=["WhatsApp", "Telegram"],
            errors=["Platform 1: Error", "Platform 2: Error"]
        )
        
        confidence = self.checker._calculate_search_confidence(result)
        self.assertLess(confidence, 50.0)  # Should be reduced due to errors
    
    def test_search_social_media_integration(self):
        """Test complete social media search integration"""
        # Test with number that should trigger multiple demo patterns
        demo_number = '+15551234123'  # Should trigger Telegram
        
        result = self.checker.search_social_media(demo_number)
        
        self.assertIsInstance(result, SocialMediaResult)
        self.assertEqual(result.phone_number, demo_number)
        self.assertGreater(len(result.platforms_searched), 0)
        self.assertGreaterEqual(result.total_profiles, 0)
        self.assertGreaterEqual(result.search_confidence, 0.0)
        self.assertLessEqual(result.search_confidence, 100.0)
        self.assertGreater(result.processing_time, 0.0)
    
    def test_search_social_media_specific_platforms(self):
        """Test social media search with specific platforms"""
        platforms = ['whatsapp', 'telegram']
        result = self.checker.search_social_media(self.test_phone_us, platforms)
        
        self.assertIsInstance(result, SocialMediaResult)
        # Should only search specified platforms (that are ToS compliant)
        searched_platforms = [p.lower() for p in result.platforms_searched]
        for platform in platforms:
            if self.checker.platforms[platform]['tos_compliant']:
                platform_name = self.checker.platforms[platform]['name'].lower()
                self.assertTrue(any(platform_name in sp.lower() for sp in result.platforms_searched))
    
    def test_search_social_media_tos_compliance(self):
        """Test that search respects ToS compliance"""
        # Include both compliant and non-compliant platforms
        platforms = ['whatsapp', 'facebook', 'instagram', 'telegram']
        result = self.checker.search_social_media(self.test_phone_us, platforms)
        
        # Should have errors for non-compliant platforms
        tos_errors = [error for error in result.errors if 'ToS' in error]
        self.assertGreater(len(tos_errors), 0)
    
    def test_generate_social_media_report(self):
        """Test social media report generation"""
        # Create mock result with profiles
        profiles = [
            ProfileInfo(
                platform="WhatsApp",
                username="+1234567890",
                privacy_level=PrivacyLevel.PRIVATE,
                business_account=False,
                verified=False,
                confidence=80.0,
                profile_url="https://wa.me/1234567890"
            ),
            ProfileInfo(
                platform="Telegram",
                username="testuser",
                display_name="Test User",
                bio="Test bio for Telegram user",
                privacy_level=PrivacyLevel.PUBLIC,
                verified=True,
                confidence=70.0,
                profile_url="https://t.me/testuser",
                additional_info={'member_count': 150}
            )
        ]
        
        result = SocialMediaResult(
            phone_number="+1234567890",
            profiles_found=profiles,
            platforms_searched=["WhatsApp", "Telegram"],
            total_profiles=2,
            public_profiles=1,
            verified_profiles=1,
            processing_time=2.5,
            search_confidence=75.0
        )
        
        report = self.checker.generate_social_media_report(result)
        
        self.assertIsInstance(report, str)
        self.assertIn('COMPREHENSIVE SOCIAL MEDIA ANALYSIS', report)
        self.assertIn('+1234567890', report)
        self.assertIn('WhatsApp', report)
        self.assertIn('Telegram', report)
        self.assertIn('Test User', report)
        self.assertIn('75.0%', report)  # Confidence
        self.assertIn('PRIVACY ANALYSIS', report)
        self.assertIn('LEGAL COMPLIANCE NOTICE', report)


class TestSocialMediaCheckerIntegration(unittest.TestCase):
    """Integration tests for SocialMediaChecker"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.checker = SocialMediaChecker()
    
    def test_privacy_level_enum(self):
        """Test privacy level enum values"""
        self.assertEqual(PrivacyLevel.PUBLIC.value, "Public")
        self.assertEqual(PrivacyLevel.SEMI_PRIVATE.value, "Semi-Private")
        self.assertEqual(PrivacyLevel.PRIVATE.value, "Private")
        self.assertEqual(PrivacyLevel.UNKNOWN.value, "Unknown")
    
    def test_platform_type_enum(self):
        """Test platform type enum values"""
        self.assertEqual(PlatformType.MESSAGING.value, "Messaging")
        self.assertEqual(PlatformType.PROFESSIONAL.value, "Professional")
        self.assertEqual(PlatformType.SOCIAL.value, "Social")
        self.assertEqual(PlatformType.MEDIA_SHARING.value, "Media Sharing")
    
    def test_platform_configuration_consistency(self):
        """Test platform configuration consistency"""
        for platform_name, config in self.checker.platforms.items():
            # Required fields
            required_fields = ['name', 'type', 'search_method', 'timeout', 'enabled', 'tos_compliant']
            for field in required_fields:
                self.assertIn(field, config, f"Missing {field} in {platform_name}")
            
            # Valid types
            self.assertIsInstance(config['type'], PlatformType)
            self.assertIsInstance(config['timeout'], float)
            self.assertIsInstance(config['enabled'], bool)
            self.assertIsInstance(config['tos_compliant'], bool)
            
            # Reasonable timeout values
            self.assertGreater(config['timeout'], 0.0)
            self.assertLess(config['timeout'], 30.0)
    
    def test_comprehensive_workflow(self):
        """Test complete social media search workflow"""
        # Test with different types of numbers
        test_numbers = [
            '+15551234567',    # Regular US number
            '+919876543210',   # Regular Indian number
            '+15551234123',    # Demo pattern for Telegram
            '+15551234000',    # Demo pattern for LinkedIn
            '+15551234777',    # Demo pattern for Twitter
        ]
        
        for phone_number in test_numbers:
            with self.subTest(phone=phone_number):
                result = self.checker.search_social_media(phone_number)
                
                # Basic validation
                self.assertIsInstance(result, SocialMediaResult)
                self.assertEqual(result.phone_number, phone_number)
                self.assertGreaterEqual(result.total_profiles, 0)
                self.assertGreaterEqual(result.search_confidence, 0.0)
                self.assertLessEqual(result.search_confidence, 100.0)
                self.assertGreater(result.processing_time, 0.0)
                
                # All found profiles should be valid
                for profile in result.profiles_found:
                    self.assertIsInstance(profile, ProfileInfo)
                    self.assertIsNotNone(profile.platform)
                    self.assertIsInstance(profile.privacy_level, PrivacyLevel)
                    self.assertGreaterEqual(profile.confidence, 0.0)
                    self.assertLessEqual(profile.confidence, 100.0)
                
                # Report generation should work
                report = self.checker.generate_social_media_report(result)
                self.assertIsInstance(report, str)
                self.assertGreater(len(report), 100)


if __name__ == '__main__':
    unittest.main()