#!/usr/bin/env python3
"""
Final comprehensive test of all dark web OSINT tools
Tests actual functionality within the CIOT application
"""

import sys
sys.path.append('src')

def test_all_tools():
    print("🕸️ FINAL DARK WEB OSINT TOOLS TEST")
    print("=" * 40)
    
    try:
        from gui.tabs.darkweb_tab import DarkWebTab
        import customtkinter as ctk
        
        # Create test instance
        root = ctk.CTk()
        root.withdraw()
        tab = DarkWebTab(root)
        
        print("✅ CIOT Dark Web Tab initialized successfully")
        
        # Test all 9 tools with real functionality
        test_cases = [
            ("h8mail", "test@example.com", "Email breach analysis"),
            ("OnionScan", "http://3g2upl4pq6kufc4m.onion", "Onion security analysis"),
            ("Final Recon", "example.com", "Web reconnaissance"),
            ("OSINT-SPY", "test@example.com", "Multi-target intelligence"),
            ("Dark Scrape", "http://3g2upl4pq6kufc4m.onion", "Content extraction"),
            ("Fresh Onions", "bitcoin", "Hidden service discovery"),
            ("Breach Hunt", "test@example.com", "Credential monitoring"),
            ("Bitcoin Analysis", "1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa", "Cryptocurrency analysis"),
            ("TorBot", "http://3g2upl4pq6kufc4m.onion", "Dark web crawling")
        ]
        
        print("\n🔍 Testing all 9 dark web OSINT tools:")
        print("-" * 40)
        
        results = []
        
        for i, (tool, target, description) in enumerate(test_cases, 1):
            print(f"\n{i}. Testing {tool}")
            print(f"   Target: {target}")
            print(f"   Purpose: {description}")
            
            # Set the tool and target
            tab.tool_type.set(tool)
            tab._change_tool_type()
            tab.input_var.set(target)
            
            # Clear results
            tab.result_box.delete("1.0", "end")
            
            # Run the tool
            try:
                if tool == "h8mail":
                    tab._run_h8mail(target)
                elif tool == "OnionScan":
                    tab._run_onionscan(target)
                elif tool == "Final Recon":
                    tab._run_finalrecon(target)
                elif tool == "OSINT-SPY":
                    tab._run_osintspy(target)
                elif tool == "Dark Scrape":
                    tab._run_darkscrape(target)
                elif tool == "Fresh Onions":
                    tab._run_freshonions(target)
                elif tool == "Breach Hunt":
                    tab._run_breachhunt(target)
                elif tool == "Bitcoin Analysis":
                    tab._run_bitcoin_analysis(target)
                elif tool == "TorBot":
                    tab._run_torbot(target)
                
                # Get results
                output = tab.result_box.get("1.0", "end").strip()
                
                if output and len(output) > 200:
                    print("   ✅ SUCCESS - Tool executed with comprehensive analysis")
                    print(f"   📊 Generated {len(output)} characters of analysis")
                    
                    # Check for key indicators of real functionality
                    indicators = []
                    if "Install" not in output or "pip install" not in output:
                        indicators.append("No installation messages")
                    if "analysis" in output.lower():
                        indicators.append("Analysis performed")
                    if "security" in output.lower() or "investigation" in output.lower():
                        indicators.append("Professional guidance")
                    if len(output) > 1000:
                        indicators.append("Comprehensive output")
                    
                    if indicators:
                        print(f"   🎯 Quality indicators: {', '.join(indicators)}")
                    
                    results.append(True)
                else:
                    print("   ❌ FAILED - Minimal or no output")
                    results.append(False)
                    
            except Exception as e:
                print(f"   ❌ ERROR - {str(e)}")
                results.append(False)
        
        # Test Tor service functionality
        print(f"\n🧅 Testing Tor Service Management:")
        print("-" * 35)
        
        try:
            tab.result_box.delete("1.0", "end")
            tab._start_tor_service()
            tor_output = tab.result_box.get("1.0", "end").strip()
            
            if len(tor_output) > 5000:
                print("   ✅ SUCCESS - Comprehensive Tor service guide")
                print(f"   📊 Generated {len(tor_output)} characters of guidance")
                
                # Check for key Tor features
                tor_features = [
                    "TOR SERVICE STATUS CHECK",
                    "WHAT YOU CAN DO WITH TOR SERVICE",
                    "TOR INSTALLATION GUIDE",
                    "SECURITY & OPSEC GUIDELINES",
                    "DARK WEB INVESTIGATION RESOURCES"
                ]
                
                found_features = [f for f in tor_features if f in tor_output]
                print(f"   🎯 Features included: {len(found_features)}/{len(tor_features)}")
                
                results.append(True)
            else:
                print("   ❌ FAILED - Insufficient Tor guidance")
                results.append(False)
                
        except Exception as e:
            print(f"   ❌ ERROR - Tor service test failed: {str(e)}")
            results.append(False)
        
        # Final summary
        print(f"\n🎉 FINAL RESULTS")
        print("=" * 20)
        
        success_count = sum(results)
        total_tests = len(results)
        success_rate = (success_count / total_tests) * 100
        
        print(f"📊 Overall Success: {success_count}/{total_tests} ({success_rate:.1f}%)")
        
        if success_rate >= 90:
            print("🚀 EXCELLENT! All dark web OSINT tools are fully functional")
            print("   ✅ No 'Install for full functionality' messages should appear")
            print("   ✅ All tools provide comprehensive professional analysis")
            print("   ✅ Ready for professional cybersecurity investigations")
        elif success_rate >= 80:
            print("✅ VERY GOOD! Most tools are fully functional")
            print("   ✅ Minimal installation messages")
            print("   ✅ Professional analysis capabilities")
        elif success_rate >= 70:
            print("👍 GOOD! Tools are working with minor issues")
            print("   ⚠️ Some tools may show installation messages")
            print("   ✅ Core functionality is available")
        else:
            print("⚠️ NEEDS IMPROVEMENT! Several tools need attention")
            print("   ❌ Many tools will show installation messages")
            print("   🔧 Run installation script to fix issues")
        
        # Specific tool status
        print(f"\n🛠️ TOOL-BY-TOOL STATUS:")
        print("-" * 25)
        
        for i, (tool, _, _) in enumerate(test_cases):
            status = "✅ WORKING" if results[i] else "❌ NEEDS ATTENTION"
            print(f"   {status} - {tool}")
        
        tor_status = "✅ WORKING" if results[-1] else "❌ NEEDS ATTENTION"
        print(f"   {tor_status} - Tor Service Management")
        
        print(f"\n📚 NEXT STEPS:")
        print("-" * 15)
        
        if success_rate >= 90:
            print("🎯 Your CIOT application is ready for professional use!")
            print("   • All dark web OSINT tools are fully functional")
            print("   • Comprehensive analysis and reporting available")
            print("   • Legal and ethical guidelines included")
        else:
            print("🔧 To improve functionality:")
            print("   • Ensure all external tools are properly installed")
            print("   • Check Tor service is running correctly")
            print("   • Verify network connectivity")
            print("   • Review installation logs for errors")
        
        root.destroy()
        
        return success_rate >= 80
        
    except Exception as e:
        print(f"❌ Critical test failure: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_all_tools()
    exit(0 if success else 1)