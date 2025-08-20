#!/usr/bin/env python3
"""
Test the main CIOT application launch
"""

import sys
import os
import threading
import time

# Add src to path
sys.path.insert(0, 'src')

def test_app_launch():
    """Test application launch without GUI display"""
    print("🚀 Testing CIOT Main Application Launch")
    print("=" * 40)
    
    try:
        # Import main application
        from main import CIOTMainApp
        print("✅ Main application imported successfully")
        
        # Test initialization (without showing GUI)
        import customtkinter as ctk
        
        # Set headless mode for testing
        os.environ['DISPLAY'] = ':99'  # Virtual display for testing
        
        try:
            app = CIOTMainApp()
            print("✅ Application initialized successfully")
            
            # Test tab creation
            if hasattr(app, 'tabview'):
                print("✅ Tab view created successfully")
                
                # Check if tabs exist
                tabs = app.tabview._tab_dict.keys() if hasattr(app.tabview, '_tab_dict') else []
                print(f"✅ Tabs created: {len(tabs)} tabs")
                for tab_name in tabs:
                    print(f"   • {tab_name}")
            
            # Test surface web tab
            if hasattr(app, 'surface_web_tab'):
                print("✅ Surface Web OSINT tab initialized")
            
            # Test dark web tab
            if hasattr(app, 'dark_web_tab'):
                print("✅ Dark Web OSINT tab initialized")
            
            # Clean shutdown
            app.destroy()
            print("✅ Application shutdown successfully")
            
            return True
            
        except Exception as e:
            print(f"❌ Application initialization failed: {e}")
            return False
            
    except Exception as e:
        print(f"❌ Import failed: {e}")
        return False

def test_tab_functionality():
    """Test individual tab functionality"""
    print("\n🔧 Testing Tab Functionality")
    print("-" * 30)
    
    try:
        # Test Surface Web Tab
        from gui.tabs.surface_web_tab import SurfaceWebTab
        import customtkinter as ctk
        
        root = ctk.CTk()
        root.withdraw()  # Hide window
        
        surface_tab = SurfaceWebTab(root)
        print("✅ Surface Web tab created successfully")
        
        # Test basic functionality
        surface_tab.lookup_type.set("Phone Number")
        surface_tab.target_var.set("9876543210")
        print("✅ Surface Web tab basic operations work")
        
        root.destroy()
        
        # Test Dark Web Tab
        from gui.tabs.darkweb_tab import DarkWebTab
        
        root = ctk.CTk()
        root.withdraw()  # Hide window
        
        dark_tab = DarkWebTab(root)
        print("✅ Dark Web tab created successfully")
        
        # Test basic functionality
        dark_tab.tool_type.set("h8mail")
        dark_tab._change_tool_type()
        print("✅ Dark Web tab basic operations work")
        
        root.destroy()
        
        return True
        
    except Exception as e:
        print(f"❌ Tab functionality test failed: {e}")
        return False

def main():
    """Main test execution"""
    print("🧪 CIOT APPLICATION LAUNCH TEST")
    print("=" * 35)
    
    # Test 1: Application launch
    launch_success = test_app_launch()
    
    # Test 2: Tab functionality
    tab_success = test_tab_functionality()
    
    # Summary
    print(f"\n📊 TEST RESULTS")
    print("=" * 20)
    print(f"Application Launch: {'✅ PASS' if launch_success else '❌ FAIL'}")
    print(f"Tab Functionality: {'✅ PASS' if tab_success else '❌ FAIL'}")
    
    overall_success = launch_success and tab_success
    
    if overall_success:
        print("\n🎉 ALL TESTS PASSED!")
        print("🚀 CIOT Application is ready to launch!")
        print("\n📋 To run the application:")
        print("   python3 src/main.py")
        return 0
    else:
        print("\n❌ SOME TESTS FAILED!")
        print("🔧 Check the errors above and fix before launching")
        return 1

if __name__ == "__main__":
    exit(main())