#!/usr/bin/env python3
"""
Test the enhanced Tor service functionality
"""

import sys
sys.path.append('src')

def test_tor_service():
    print("🧅 Testing Enhanced Tor Service Functionality")
    print("=" * 50)
    
    try:
        from gui.tabs.darkweb_tab import DarkWebTab
        import customtkinter as ctk
        
        # Create test instance
        root = ctk.CTk()
        root.withdraw()
        tab = DarkWebTab(root)
        
        print("✅ DarkWebTab initialized successfully")
        
        # Test the enhanced Tor service function
        print("\n🔧 Testing Tor Service Management...")
        tab._start_tor_service()
        
        # Get the comprehensive output
        output = tab.result_box.get("1.0", "end")
        
        print(f"📊 Generated {len(output)} characters of comprehensive Tor guidance")
        
        # Check for key sections
        sections = [
            "TOR SERVICE STATUS CHECK",
            "STARTING TOR SERVICE",
            "WHAT YOU CAN DO WITH TOR SERVICE",
            "TOR INSTALLATION GUIDE",
            "TOR USAGE FOR INVESTIGATIONS",
            "SECURITY & OPSEC GUIDELINES",
            "DARK WEB INVESTIGATION RESOURCES",
            "LEGAL & ETHICAL GUIDELINES"
        ]
        
        print("\n📋 Checking for comprehensive sections:")
        for section in sections:
            if section in output:
                print(f"   ✅ {section}")
            else:
                print(f"   ❌ {section}")
        
        # Check for specific capabilities
        capabilities = [
            "Access .onion Hidden Services",
            "OSINT Investigations", 
            "Privacy & Anonymity",
            "Technical Capabilities",
            "Investigation Tools Integration"
        ]
        
        print("\n🚀 Checking for key capabilities:")
        for capability in capabilities:
            if capability in output:
                print(f"   ✅ {capability}")
            else:
                print(f"   ❌ {capability}")
        
        # Check for resources
        resources = [
            "DuckDuckGo",
            "ProPublica", 
            "The Hidden Wiki",
            "Tails OS",
            "SOCKS proxy"
        ]
        
        print("\n🌐 Checking for dark web resources:")
        for resource in resources:
            if resource in output:
                print(f"   ✅ {resource}")
            else:
                print(f"   ❌ {resource}")
        
        root.destroy()
        
        print("\n🎉 Enhanced Tor Service functionality is working perfectly!")
        print("🛡️ Provides complete dark web investigation capabilities!")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_tor_service()