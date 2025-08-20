#!/usr/bin/env python3
"""
Demo: Show actual output from dark web OSINT tools
"""

import sys
sys.path.append('src')

def demo_tool_output():
    print("🕸️ DARK WEB OSINT TOOLS - SAMPLE OUTPUT DEMO")
    print("=" * 50)
    
    try:
        from gui.tabs.darkweb_tab import DarkWebTab
        import customtkinter as ctk
        
        root = ctk.CTk()
        root.withdraw()
        tab = DarkWebTab(root)
        
        # Demo h8mail output
        print("\n📧 H8MAIL TOOL - Email Breach Analysis")
        print("-" * 40)
        tab.tool_type.set("h8mail")
        tab._change_tool_type()
        tab.result_box.delete("1.0", "end")
        tab._run_h8mail("leakedaccount@testmail.com")
        output = tab.result_box.get("1.0", "end")
        print(output)
        
        print("\n" + "=" * 50)
        print("₿ BITCOIN ANALYSIS TOOL - Cryptocurrency Investigation")
        print("-" * 50)
        tab.tool_type.set("Bitcoin Analysis")
        tab._change_tool_type()
        tab.result_box.delete("1.0", "end")
        tab._run_bitcoin_analysis("1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa")
        output = tab.result_box.get("1.0", "end")
        print(output)
        
        root.destroy()
        
    except Exception as e:
        print(f"❌ Demo failed: {e}")

if __name__ == "__main__":
    demo_tool_output()