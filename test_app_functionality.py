#!/usr/bin/env python3
"""
Simple test script to verify core CIOT Toolkit functionality
"""

import sys
import os
sys.path.append('src')

def test_core_functionality():
    """Test core functionality of the CIOT Toolkit"""
    print("🔍 CIOT Toolkit - Core Functionality Test")
    print("=" * 50)
    
    # Test 1: Phone Investigation
    print("\n1. Testing Phone Investigation...")
    try:
        from utils.osint_utils import IndianPhoneNumberFormatter
        formatter = IndianPhoneNumberFormatter()
        result = formatter.format_phone_number('9876543210')
        
        if result.get('success'):
            best = result.get('best_format', {})
            print(f"   ✅ Phone formatting successful")
            print(f"   📱 Input: 9876543210")
            print(f"   🌍 International: {best.get('international', 'N/A')}")
            print(f"   🇮🇳 Country: {best.get('country_name', 'N/A')}")
            print(f"   📞 Type: {best.get('number_type', 'N/A')}")
        else:
            print(f"   ❌ Phone formatting failed: {result.get('error', 'Unknown error')}")
    except Exception as e:
        print(f"   ❌ Phone investigation error: {e}")
    
    # Test 2: Validators
    print("\n2. Testing Input Validators...")
    try:
        from utils.validators import validate_phone, validate_email, validate_ip, validate_domain
        
        tests = [
            ('Phone', validate_phone, '+919876543210'),
            ('Email', validate_email, 'test@example.com'),
            ('IP', validate_ip, '192.168.1.1'),
            ('Domain', validate_domain, 'example.com')
        ]
        
        for name, validator, test_input in tests:
            result = validator(test_input)
            status = "✅" if result else "❌"
            print(f"   {status} {name} validation: {test_input} -> {result}")
            
    except Exception as e:
        print(f"   ❌ Validator error: {e}")
    
    # Test 3: WHOIS Checker
    print("\n3. Testing WHOIS Checker...")
    try:
        from utils.whois_checker import WHOISChecker
        import tempfile
        
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
            checker = WHOISChecker(tmp.name)
            print(f"   ✅ WHOIS checker initialized successfully")
            
        # Cleanup
        os.unlink(tmp.name)
        
    except Exception as e:
        print(f"   ❌ WHOIS checker error: {e}")
    
    # Test 4: Configuration Manager
    print("\n4. Testing Configuration Manager...")
    try:
        from core.config_manager import ConfigManager
        config = ConfigManager()
        print(f"   ✅ Configuration manager initialized")
        print(f"   📁 Config directory: {config.config_dir}")
        
    except Exception as e:
        print(f"   ❌ Configuration manager error: {e}")
    
    # Test 5: Application Import
    print("\n5. Testing Main Application...")
    try:
        from core.application import CIOTMainApp
        print(f"   ✅ Main application class imported successfully")
        print(f"   🚀 Application ready to launch")
        
    except Exception as e:
        print(f"   ❌ Application import error: {e}")
    
    print("\n" + "=" * 50)
    print("🎯 Core functionality test completed!")
    print("📝 Note: Some advanced features may require API keys")
    print("🔧 For full functionality, configure API keys in config/api_keys.json")

if __name__ == "__main__":
    test_core_functionality()