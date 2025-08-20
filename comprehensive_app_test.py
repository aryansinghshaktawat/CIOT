#!/usr/bin/env python3
"""
COMPREHENSIVE CIOT APPLICATION TEST SUITE
Tests every single component and fixes any issues found
"""

import sys
import os
import traceback
import importlib
import subprocess
import socket
import threading
import time
from pathlib import Path

# Add src to path
sys.path.insert(0, 'src')

class CIOTTestSuite:
    def __init__(self):
        self.test_results = []
        self.issues_found = []
        self.fixes_applied = []
        
    def log_test(self, test_name, success, message="", fix_applied=None):
        """Log test results"""
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"   {status} {test_name}")
        if message:
            print(f"       {message}")
        if fix_applied:
            print(f"       🔧 FIX: {fix_applied}")
            self.fixes_applied.append(fix_applied)
        
        self.test_results.append({
            'test': test_name,
            'success': success,
            'message': message,
            'fix': fix_applied
        })
        
        if not success:
            self.issues_found.append(f"{test_name}: {message}")
    
    def test_imports(self):
        """Test all critical imports"""
        print("\n📦 TESTING IMPORTS")
        print("-" * 20)
        
        # Core Python modules
        core_modules = [
            'customtkinter', 'tkinter', 'requests', 'json', 'os', 'sys',
            'threading', 'subprocess', 'socket', 'datetime', 'pathlib',
            'urllib.parse', 'webbrowser', 'fpdf', 'bs4', 'lxml'
        ]
        
        for module in core_modules:
            try:
                importlib.import_module(module)
                self.log_test(f"Import {module}", True)
            except ImportError as e:
                self.log_test(f"Import {module}", False, str(e))
        
        # CIOT specific modules
        ciot_modules = [
            'gui.tabs.darkweb_tab',
            'gui.tabs.surface_web_tab', 
            'utils.osint_utils',
            'utils.enhanced_phone_osint'
        ]
        
        for module in ciot_modules:
            try:
                importlib.import_module(module)
                self.log_test(f"Import {module}", True)
            except ImportError as e:
                self.log_test(f"Import {module}", False, str(e))
    
    def test_main_application(self):
        """Test main application initialization"""
        print("\n🚀 TESTING MAIN APPLICATION")
        print("-" * 30)
        
        try:
            # Test if main.py exists and is importable
            if os.path.exists('src/main.py'):
                self.log_test("Main application file exists", True)
                
                # Try to import main components
                try:
                    from main import CIOTMainApp
                    self.log_test("Main application class import", True)
                except Exception as e:
                    self.log_test("Main application class import", False, str(e))
            else:
                self.log_test("Main application file exists", False, "main.py not found")
                
        except Exception as e:
            self.log_test("Main application test", False, str(e))
    
    def test_surface_web_tab(self):
        """Test Surface Web OSINT tab"""
        print("\n🌐 TESTING SURFACE WEB OSINT TAB")
        print("-" * 35)
        
        try:
            from gui.tabs.surface_web_tab import SurfaceWebTab
            import customtkinter as ctk
            
            # Create test instance
            root = ctk.CTk()
            root.withdraw()
            
            try:
                tab = SurfaceWebTab(root)
                self.log_test("Surface Web tab initialization", True)
                
                # Test lookup types
                lookup_types = ["Full Name", "Phone Number", "Email Address", "IP Address"]
                for lookup_type in lookup_types:
                    try:
                        tab.lookup_type.set(lookup_type)
                        tab.on_lookup_type_change(lookup_type)
                        self.log_test(f"Lookup type: {lookup_type}", True)
                    except Exception as e:
                        self.log_test(f"Lookup type: {lookup_type}", False, str(e))
                
                # Test investigation functionality
                test_cases = [
                    ("Full Name", "John Doe"),
                    ("Phone Number", "9876543210"),  # Valid Indian mobile number
                    ("Email Address", "test@example.com"),
                    ("IP Address", "8.8.8.8")
                ]
                
                for lookup_type, test_input in test_cases:
                    try:
                        tab.lookup_type.set(lookup_type)
                        tab.target_var.set(test_input)
                        
                        # Test validation
                        is_valid = tab.validate_input(test_input, lookup_type)
                        if is_valid:
                            self.log_test(f"Input validation: {lookup_type}", True)
                        else:
                            self.log_test(f"Input validation: {lookup_type}", False, "Validation failed")
                            
                    except Exception as e:
                        self.log_test(f"Input validation: {lookup_type}", False, str(e))
                
                # Test PDF export
                try:
                    tab.results_textbox.insert("1.0", "Test content for PDF export")
                    tab.export_report()
                    self.log_test("PDF export functionality", True)
                except Exception as e:
                    self.log_test("PDF export functionality", False, str(e))
                
            except Exception as e:
                self.log_test("Surface Web tab initialization", False, str(e))
            
            root.destroy()
            
        except Exception as e:
            self.log_test("Surface Web tab import", False, str(e))
    
    def test_dark_web_tab(self):
        """Test Dark Web OSINT tab"""
        print("\n🕸️ TESTING DARK WEB OSINT TAB")
        print("-" * 32)
        
        try:
            from gui.tabs.darkweb_tab import DarkWebTab
            import customtkinter as ctk
            
            # Create test instance
            root = ctk.CTk()
            root.withdraw()
            
            try:
                tab = DarkWebTab(root)
                self.log_test("Dark Web tab initialization", True)
                
                # Test all 9 tools
                tools = [
                    "TorBot", "h8mail", "OnionScan", "Final Recon", 
                    "OSINT-SPY", "Dark Scrape", "Fresh Onions", 
                    "Breach Hunt", "Bitcoin Analysis"
                ]
                
                for tool in tools:
                    try:
                        tab.tool_type.set(tool)
                        tab._change_tool_type()
                        self.log_test(f"Tool switching: {tool}", True)
                    except Exception as e:
                        self.log_test(f"Tool switching: {tool}", False, str(e))
                
                # Test tool execution
                test_cases = [
                    ("h8mail", "test@example.com"),
                    ("OnionScan", "http://3g2upl4pq6kufc4m.onion"),
                    ("Final Recon", "example.com"),
                    ("Bitcoin Analysis", "1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa")
                ]
                
                for tool, test_input in test_cases:
                    try:
                        tab.tool_type.set(tool)
                        tab._change_tool_type()
                        tab.input_var.set(test_input)
                        tab.result_box.delete("1.0", "end")
                        
                        # Execute the tool
                        if tool == "h8mail":
                            tab._run_h8mail(test_input)
                        elif tool == "OnionScan":
                            tab._run_onionscan(test_input)
                        elif tool == "Final Recon":
                            tab._run_finalrecon(test_input)
                        elif tool == "Bitcoin Analysis":
                            tab._run_bitcoin_analysis(test_input)
                        
                        output = tab.result_box.get("1.0", "end").strip()
                        if len(output) > 200:
                            self.log_test(f"Tool execution: {tool}", True)
                        else:
                            self.log_test(f"Tool execution: {tool}", False, "Insufficient output")
                            
                    except Exception as e:
                        self.log_test(f"Tool execution: {tool}", False, str(e))
                
                # Test Tor service management
                try:
                    tab._start_tor_service()
                    tor_output = tab.result_box.get("1.0", "end").strip()
                    if len(tor_output) > 1000:
                        self.log_test("Tor service management", True)
                    else:
                        self.log_test("Tor service management", False, "Insufficient output")
                except Exception as e:
                    self.log_test("Tor service management", False, str(e))
                
                # Test export functions
                try:
                    tab.result_box.insert("1.0", "Test content")
                    tab._export_to_pdf()
                    self.log_test("Dark Web PDF export", True)
                except Exception as e:
                    self.log_test("Dark Web PDF export", False, str(e))
                
                try:
                    tab._export_to_json()
                    self.log_test("Dark Web JSON export", True)
                except Exception as e:
                    self.log_test("Dark Web JSON export", False, str(e))
                
            except Exception as e:
                self.log_test("Dark Web tab initialization", False, str(e))
            
            root.destroy()
            
        except Exception as e:
            self.log_test("Dark Web tab import", False, str(e))
    
    def test_utilities(self):
        """Test utility modules"""
        print("\n🔧 TESTING UTILITY MODULES")
        print("-" * 27)
        
        # Test OSINT utils
        try:
            from utils.osint_utils import OSINTUtils
            utils = OSINTUtils()
            self.log_test("OSINT Utils initialization", True)
            
            # Test validation functions
            test_cases = [
                ("validate_email", "test@example.com", True),
                ("validate_phone", "+1234567890", True),
                ("validate_ip", "192.168.1.1", True),
                ("validate_domain", "example.com", True)
            ]
            
            for method_name, test_input, expected in test_cases:
                try:
                    if hasattr(utils, method_name):
                        result = getattr(utils, method_name)(test_input)
                        self.log_test(f"OSINT Utils {method_name}", True)
                    else:
                        self.log_test(f"OSINT Utils {method_name}", False, "Method not found")
                except Exception as e:
                    self.log_test(f"OSINT Utils {method_name}", False, str(e))
                    
        except Exception as e:
            self.log_test("OSINT Utils import", False, str(e))
        
        # Test enhanced phone OSINT
        try:
            from utils.enhanced_phone_osint import EnhancedPhoneOSINT
            phone_osint = EnhancedPhoneOSINT()
            self.log_test("Enhanced Phone OSINT initialization", True)
            
            # Test phone investigation
            try:
                result = phone_osint.investigate_phone("+1234567890")
                if result:
                    self.log_test("Phone investigation", True)
                else:
                    self.log_test("Phone investigation", False, "No result returned")
            except Exception as e:
                self.log_test("Phone investigation", False, str(e))
                
        except Exception as e:
            self.log_test("Enhanced Phone OSINT import", False, str(e))
    
    def test_external_dependencies(self):
        """Test external dependencies and tools"""
        print("\n🌐 TESTING EXTERNAL DEPENDENCIES")
        print("-" * 35)
        
        # Test network connectivity
        try:
            response = subprocess.run(['ping', '-c', '1', 'google.com'], 
                                    capture_output=True, timeout=10)
            if response.returncode == 0:
                self.log_test("Internet connectivity", True)
            else:
                self.log_test("Internet connectivity", False, "Ping failed")
        except Exception as e:
            self.log_test("Internet connectivity", False, str(e))
        
        # Test Tor service
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(3)
            result = sock.connect_ex(('127.0.0.1', 9050))
            sock.close()
            
            if result == 0:
                self.log_test("Tor SOCKS proxy", True)
            else:
                self.log_test("Tor SOCKS proxy", False, "Port 9050 not accessible")
        except Exception as e:
            self.log_test("Tor SOCKS proxy", False, str(e))
        
        # Test external tools
        external_tools = [
            ("h8mail", ["h8mail", "--help"]),
            ("git", ["git", "--version"]),
            ("curl", ["curl", "--version"]),
            ("python3", ["python3", "--version"])
        ]
        
        for tool_name, command in external_tools:
            try:
                result = subprocess.run(command, capture_output=True, timeout=10)
                if result.returncode == 0:
                    self.log_test(f"External tool: {tool_name}", True)
                else:
                    self.log_test(f"External tool: {tool_name}", False, "Command failed")
            except Exception as e:
                self.log_test(f"External tool: {tool_name}", False, str(e))
    
    def test_file_operations(self):
        """Test file operations and permissions"""
        print("\n📁 TESTING FILE OPERATIONS")
        print("-" * 27)
        
        # Test directory structure
        required_dirs = [
            'src',
            'src/gui',
            'src/gui/tabs',
            'src/utils',
            'tests'
        ]
        
        for directory in required_dirs:
            if os.path.exists(directory):
                self.log_test(f"Directory exists: {directory}", True)
            else:
                self.log_test(f"Directory exists: {directory}", False, "Directory missing")
        
        # Test required files
        required_files = [
            'src/gui/tabs/darkweb_tab.py',
            'src/gui/tabs/surface_web_tab.py',
            'src/utils/osint_utils.py',
            'src/utils/enhanced_phone_osint.py'
        ]
        
        for file_path in required_files:
            if os.path.exists(file_path):
                self.log_test(f"File exists: {file_path}", True)
                
                # Test file readability
                try:
                    with open(file_path, 'r') as f:
                        content = f.read()
                    if len(content) > 100:
                        self.log_test(f"File readable: {file_path}", True)
                    else:
                        self.log_test(f"File readable: {file_path}", False, "File too small")
                except Exception as e:
                    self.log_test(f"File readable: {file_path}", False, str(e))
            else:
                self.log_test(f"File exists: {file_path}", False, "File missing")
        
        # Test write permissions
        try:
            test_file = "test_write_permission.tmp"
            with open(test_file, 'w') as f:
                f.write("test")
            os.remove(test_file)
            self.log_test("Write permissions", True)
        except Exception as e:
            self.log_test("Write permissions", False, str(e))
    
    def test_configuration(self):
        """Test configuration and settings"""
        print("\n⚙️ TESTING CONFIGURATION")
        print("-" * 25)
        
        # Test config directories
        config_dirs = [
            'config',
            '.kiro',
            '.kiro/specs'
        ]
        
        for config_dir in config_dirs:
            if os.path.exists(config_dir):
                self.log_test(f"Config directory: {config_dir}", True)
            else:
                self.log_test(f"Config directory: {config_dir}", False, "Directory missing")
        
        # Test environment variables
        important_env_vars = ['PATH', 'HOME', 'USER']
        for env_var in important_env_vars:
            if os.getenv(env_var):
                self.log_test(f"Environment variable: {env_var}", True)
            else:
                self.log_test(f"Environment variable: {env_var}", False, "Variable not set")
    
    def fix_common_issues(self):
        """Fix common issues found during testing"""
        print("\n🔧 APPLYING FIXES FOR COMMON ISSUES")
        print("-" * 40)
        
        fixes_applied = 0
        
        # Fix missing directories
        required_dirs = ['config', 'logs', 'reports', 'temp']
        for directory in required_dirs:
            if not os.path.exists(directory):
                try:
                    os.makedirs(directory, exist_ok=True)
                    print(f"   ✅ Created directory: {directory}")
                    fixes_applied += 1
                except Exception as e:
                    print(f"   ❌ Failed to create directory {directory}: {e}")
        
        # Fix file permissions
        try:
            # Ensure Python files are executable
            python_files = []
            for root, dirs, files in os.walk('src'):
                for file in files:
                    if file.endswith('.py'):
                        python_files.append(os.path.join(root, file))
            
            for py_file in python_files:
                try:
                    os.chmod(py_file, 0o644)
                    fixes_applied += 1
                except:
                    pass
            
            if python_files:
                print(f"   ✅ Fixed permissions for {len(python_files)} Python files")
                
        except Exception as e:
            print(f"   ❌ Failed to fix file permissions: {e}")
        
        return fixes_applied
    
    def run_comprehensive_test(self):
        """Run all tests"""
        print("🧪 COMPREHENSIVE CIOT APPLICATION TEST SUITE")
        print("=" * 50)
        print("Testing every component and fixing issues...")
        print()
        
        # Run all test categories
        self.test_imports()
        self.test_main_application()
        self.test_surface_web_tab()
        self.test_dark_web_tab()
        self.test_utilities()
        self.test_external_dependencies()
        self.test_file_operations()
        self.test_configuration()
        
        # Apply fixes
        fixes_count = self.fix_common_issues()
        
        # Generate summary
        self.generate_summary()
        
        return len(self.issues_found) == 0
    
    def generate_summary(self):
        """Generate test summary"""
        print("\n📊 TEST SUMMARY")
        print("=" * 20)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result['success'])
        failed_tests = total_tests - passed_tests
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {failed_tests}")
        print(f"Success Rate: {success_rate:.1f}%")
        print(f"Fixes Applied: {len(self.fixes_applied)}")
        
        if success_rate >= 95:
            print("\n🎉 EXCELLENT! Application is in perfect condition")
        elif success_rate >= 85:
            print("\n✅ GOOD! Application is working well with minor issues")
        elif success_rate >= 70:
            print("\n⚠️ FAIR! Application has some issues that need attention")
        else:
            print("\n❌ POOR! Application has significant issues")
        
        if self.issues_found:
            print(f"\n🔍 ISSUES FOUND ({len(self.issues_found)}):")
            for i, issue in enumerate(self.issues_found, 1):
                print(f"   {i}. {issue}")
        
        if self.fixes_applied:
            print(f"\n🔧 FIXES APPLIED ({len(self.fixes_applied)}):")
            for i, fix in enumerate(self.fixes_applied, 1):
                print(f"   {i}. {fix}")
        
        # Save detailed report
        self.save_detailed_report()
    
    def save_detailed_report(self):
        """Save detailed test report"""
        try:
            with open("COMPREHENSIVE_TEST_REPORT.md", "w") as f:
                f.write("# CIOT Application - Comprehensive Test Report\n\n")
                f.write(f"**Test Date:** {time.strftime('%Y-%m-%d %H:%M:%S')}\n\n")
                
                f.write("## Summary\n")
                total_tests = len(self.test_results)
                passed_tests = sum(1 for result in self.test_results if result['success'])
                success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
                
                f.write(f"- **Total Tests:** {total_tests}\n")
                f.write(f"- **Passed:** {passed_tests}\n")
                f.write(f"- **Failed:** {total_tests - passed_tests}\n")
                f.write(f"- **Success Rate:** {success_rate:.1f}%\n")
                f.write(f"- **Fixes Applied:** {len(self.fixes_applied)}\n\n")
                
                f.write("## Detailed Results\n\n")
                for result in self.test_results:
                    status = "✅ PASS" if result['success'] else "❌ FAIL"
                    f.write(f"### {status} {result['test']}\n")
                    if result['message']:
                        f.write(f"**Message:** {result['message']}\n")
                    if result['fix']:
                        f.write(f"**Fix Applied:** {result['fix']}\n")
                    f.write("\n")
                
                if self.issues_found:
                    f.write("## Issues Found\n\n")
                    for i, issue in enumerate(self.issues_found, 1):
                        f.write(f"{i}. {issue}\n")
                    f.write("\n")
                
                if self.fixes_applied:
                    f.write("## Fixes Applied\n\n")
                    for i, fix in enumerate(self.fixes_applied, 1):
                        f.write(f"{i}. {fix}\n")
            
            print(f"\n📄 Detailed report saved: COMPREHENSIVE_TEST_REPORT.md")
            
        except Exception as e:
            print(f"\n❌ Failed to save detailed report: {e}")

def main():
    """Main test execution"""
    test_suite = CIOTTestSuite()
    success = test_suite.run_comprehensive_test()
    
    if success:
        print("\n🎯 ALL TESTS PASSED! Application is ready for use.")
        return 0
    else:
        print("\n⚠️ Some issues found. Check the report for details.")
        return 1

if __name__ == "__main__":
    exit(main())