#!/usr/bin/env python3
"""
Test script to verify phone investigation functionality
"""

import sys
import os
sys.path.append('src')

def test_phone_investigation():
    """Test the complete phone investigation workflow"""
    print("🔍 Testing Phone Investigation Workflow")
    print("=" * 50)
    
    # Test 1: Validation
    print("\n1. Testing Phone Validation...")
    import re
    
    def validate_indian_phone(phone_number):
        clean_number = re.sub(r'[^\d]', '', phone_number)
        
        if len(clean_number) == 10:
            if clean_number[0] in ['6', '7', '8', '9']:
                return True
        elif len(clean_number) == 12 and clean_number.startswith('91'):
            if clean_number[2] in ['6', '7', '8', '9']:
                return True
        elif len(clean_number) == 11 and clean_number.startswith('0'):
            if clean_number[1] in ['6', '7', '8', '9']:
                return True
        elif len(clean_number) == 13 and clean_number.startswith('910'):
            if clean_number[3] in ['6', '7', '8', '9']:
                return True
        
        return False
    
    test_numbers = [
        ('9876543210', True),
        ('+91 9876543210', True),
        ('919876543210', True),
        ('09876543210', True),
        ('5876543210', False),
        ('123456789', False)
    ]
    
    for number, expected in test_numbers:
        result = validate_indian_phone(number)
        status = "✅" if result == expected else "❌"
        print(f"   {status} {number} -> {result} (expected {expected})")
    
    # Test 2: Phone Investigation
    print("\n2. Testing Phone Investigation...")
    try:
        from utils.enhanced_phone_osint import get_comprehensive_phone_info
        
        result = get_comprehensive_phone_info('9876543210', 'IN')
        
        if result:
            print("   ✅ Investigation successful!")
            print(f"   📱 Phone: {result.get('phone_number')}")
            print(f"   🎯 Confidence: {result.get('confidence_score', 0):.1f}%")
            print(f"   📋 Summary: {result.get('investigation_summary', 'N/A')[:100]}...")
            
            # Check technical analysis
            tech = result.get('technical_analysis', {})
            if tech:
                print(f"   📞 Valid: {tech.get('is_valid', False)}")
                print(f"   🏢 Carrier: {tech.get('carrier', 'Unknown')}")
                print(f"   📍 Location: {tech.get('location', 'Unknown')}")
            
            # Check OSINT resources
            resources = result.get('osint_resources', [])
            total_tools = sum(len(cat.get('tools', [])) for cat in resources)
            print(f"   🔗 OSINT Tools: {total_tools} available")
            
        else:
            print("   ❌ Investigation failed")
            
    except Exception as e:
        print(f"   ❌ Investigation error: {e}")
    
    # Test 3: OSINT Links Generation
    print("\n3. Testing OSINT Links Generation...")
    try:
        from utils.osint_utils import generate_search_links
        
        links = generate_search_links('9876543210', 'phone')
        
        if links:
            print(f"   ✅ Generated {len(links)} OSINT links")
            
            # Group by category
            categories = {}
            for link in links:
                category = link.get('category', 'Other')
                if category not in categories:
                    categories[category] = 0
                categories[category] += 1
            
            for category, count in categories.items():
                print(f"   📂 {category}: {count} tools")
                
        else:
            print("   ❌ No links generated")
            
    except Exception as e:
        print(f"   ❌ Link generation error: {e}")
    
    print("\n" + "=" * 50)
    print("🎯 Phone Investigation Test Complete!")
    print("\n💡 To test in the GUI:")
    print("1. Run: python3 main.py")
    print("2. Select 'Phone Number' from dropdown")
    print("3. Enter: 9876543210")
    print("4. Click 'Start Investigation'")
    print("5. Check results in the results box")

if __name__ == "__main__":
    test_phone_investigation()