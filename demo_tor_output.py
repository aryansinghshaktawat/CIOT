#!/usr/bin/env python3
"""
Demo: Show actual Tor service output
"""

import sys
sys.path.append('src')

def demo_tor_output():
    print("🧅 TOR SERVICE - ACTUAL OUTPUT DEMO")
    print("=" * 40)
    
    try:
        from gui.tabs.darkweb_tab import DarkWebTab
        import customtkinter as ctk
        
        root = ctk.CTk()
        root.withdraw()
        tab = DarkWebTab(root)
        
        # Run the Tor service function
        tab._start_tor_service()
        
        # Get and display the output
        output = tab.result_box.get("1.0", "end")
        print(output)
        
        root.destroy()
        
    except Exception as e:
        print(f"❌ Demo failed: {e}")

if __name__ == "__main__":
    demo_tor_output()