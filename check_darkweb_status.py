#!/usr/bin/env python3
"""
Dark Web OSINT Tools Status Checker
Comprehensive verification of all required dependencies and tools
"""

import subprocess
import sys
import socket
import importlib
import platform
from pathlib import Path

def check_command(command, description):
    """Check if a command exists and works"""
    try:
        result = subprocess.run(command, capture_output=True, text=True, timeout=10)
        return result.returncode == 0, result.stdout.strip(), result.stderr.strip()
    except (subprocess.TimeoutExpired, FileNotFoundError, Exception):
        return False, "", "Command not found or failed"

def check_python_package(package_name, import_name=None):
    """Check if a Python package is installed and importable"""
    if import_name is None:
        import_name = package_name
    
    try:
        importlib.import_module(import_name)
        return True, "Installed and importable"
    except ImportError:
        return False, "Not installed or import failed"

def check_network_service(host, port, description):
    """Check if a network service is accessible"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(3)
        result = sock.connect_ex((host, port))
        sock.close()
        return result == 0, "Accessible" if result == 0 else "Not accessible"
    except Exception as e:
        return False, f"Connection failed: {str(e)}"

def main():
    print("🔍 DARK WEB OSINT TOOLS - STATUS CHECK")
    print("=" * 45)
    print(f"🖥️ System: {platform.system()} {platform.release()}")
    print(f"🐍 Python: {sys.version.split()[0]}")
    print()
    
    # Track overall status
    total_checks = 0
    passed_checks = 0
    
    # 1. Core Python Packages
    print("📦 CORE PYTHON PACKAGES")
    print("-" * 25)
    
    core_packages = [
        ("requests", "requests", "HTTP requests library"),
        ("beautifulsoup4", "bs4", "HTML/XML parser"),
        ("lxml", "lxml", "XML/HTML parser"),
        ("aiohttp", "aiohttp", "Async HTTP client"),
        ("python-whois", "whois", "WHOIS lookup library"),
        ("dnspython", "dns", "DNS resolution library"),
        ("pysocks", "socks", "SOCKS proxy support"),
        ("stem", "stem", "Tor controller library"),
        ("cryptography", "cryptography", "Cryptographic library")
    ]
    
    for package, import_name, description in core_packages:
        total_checks += 1
        success, message = check_python_package(package, import_name)
        status = "✅" if success else "❌"
        print(f"   {status} {package:<20} - {description}")
        if success:
            passed_checks += 1
    
    # 2. OSINT Tools
    print(f"\n🛠️ OSINT TOOLS")
    print("-" * 15)
    
    # h8mail
    total_checks += 1
    success, stdout, stderr = check_command(["h8mail", "--version"], "h8mail version")
    status = "✅" if success else "❌"
    print(f"   {status} h8mail              - Email breach hunting")
    if success:
        passed_checks += 1
        print(f"       Version: {stdout.split()[0] if stdout else 'Unknown'}")
    else:
        print(f"       Install: pip install h8mail")
    
    # finalrecon
    total_checks += 1
    success, stdout, stderr = check_command(["finalrecon", "--version"], "finalrecon version")
    status = "✅" if success else "❌"
    print(f"   {status} finalrecon          - Web reconnaissance")
    if success:
        passed_checks += 1
    else:
        print(f"       Install: pip install finalrecon")
    
    # OnionScan
    total_checks += 1
    onionscan_path = Path.home() / "onionscan" / "onionscan"
    if onionscan_path.exists():
        print(f"   ✅ OnionScan            - Hidden service security analysis")
        print(f"       Path: {onionscan_path}")
        passed_checks += 1
    else:
        print(f"   ❌ OnionScan            - Hidden service security analysis")
        print(f"       Install: git clone https://github.com/s-rah/onionscan.git ~/onionscan")
        print(f"                cd ~/onionscan && go build")
    
    # OSINT-SPY
    total_checks += 1
    osint_spy_path = Path.home() / "osint-spy"
    if osint_spy_path.exists():
        print(f"   ✅ OSINT-SPY            - Multi-target intelligence")
        print(f"       Path: {osint_spy_path}")
        passed_checks += 1
    else:
        print(f"   ❌ OSINT-SPY            - Multi-target intelligence")
        print(f"       Install: git clone https://github.com/SharadKumar97/OSINT-SPY.git ~/osint-spy")
    
    # 3. Tor Service
    print(f"\n🧅 TOR SERVICE")
    print("-" * 15)
    
    # Tor daemon
    total_checks += 1
    success, stdout, stderr = check_command(["pgrep", "-f", "tor"], "Tor process check")
    status = "✅" if success else "❌"
    print(f"   {status} Tor Daemon          - Background service")
    if success:
        passed_checks += 1
        pids = stdout.strip().split('\n') if stdout.strip() else []
        print(f"       Processes: {len(pids)} running")
    else:
        print(f"       Start: brew services start tor (macOS) or sudo systemctl start tor (Linux)")
    
    # SOCKS proxy
    total_checks += 1
    success, message = check_network_service("127.0.0.1", 9050, "Tor SOCKS proxy")
    status = "✅" if success else "❌"
    print(f"   {status} SOCKS Proxy (9050)  - Application proxy")
    if success:
        passed_checks += 1
    else:
        print(f"       Status: {message}")
    
    # Control port
    total_checks += 1
    success, message = check_network_service("127.0.0.1", 9051, "Tor control port")
    status = "✅" if success else "❌"
    print(f"   {status} Control Port (9051) - Tor management")
    if success:
        passed_checks += 1
    
    # 4. System Tools
    print(f"\n🔧 SYSTEM TOOLS")
    print("-" * 15)
    
    system_tools = [
        (["git", "--version"], "Git", "Version control system"),
        (["curl", "--version"], "Curl", "HTTP client"),
        (["nmap", "--version"], "Nmap", "Network scanner (optional)"),
        (["go", "version"], "Go", "Programming language (for OnionScan)")
    ]
    
    for command, name, description in system_tools:
        total_checks += 1
        success, stdout, stderr = check_command(command, f"{name} check")
        status = "✅" if success else "❌"
        print(f"   {status} {name:<15} - {description}")
        if success:
            passed_checks += 1
            if name == "Git":
                version = stdout.split()[2] if len(stdout.split()) > 2 else "Unknown"
                print(f"       Version: {version}")
            elif name == "Go":
                version = stdout.split()[2] if len(stdout.split()) > 2 else "Unknown"
                print(f"       Version: {version}")
    
    # 5. Connectivity Tests
    print(f"\n🌐 CONNECTIVITY TESTS")
    print("-" * 20)
    
    # Regular internet
    total_checks += 1
    try:
        import requests
        response = requests.get("http://httpbin.org/ip", timeout=10)
        if response.status_code == 200:
            print(f"   ✅ Regular Internet     - Working")
            print(f"       Your IP: {response.json().get('origin', 'Unknown')}")
            passed_checks += 1
        else:
            print(f"   ❌ Regular Internet     - Failed (Status: {response.status_code})")
    except Exception as e:
        print(f"   ❌ Regular Internet     - Failed ({str(e)})")
    
    # Tor connectivity
    total_checks += 1
    try:
        import requests
        proxies = {'http': 'socks5://127.0.0.1:9050', 'https': 'socks5://127.0.0.1:9050'}
        response = requests.get("http://httpbin.org/ip", proxies=proxies, timeout=15)
        if response.status_code == 200:
            print(f"   ✅ Tor Connectivity     - Working")
            print(f"       Exit IP: {response.json().get('origin', 'Unknown')}")
            passed_checks += 1
        else:
            print(f"   ❌ Tor Connectivity     - Failed (Status: {response.status_code})")
    except Exception as e:
        print(f"   ❌ Tor Connectivity     - Failed ({str(e)})")
    
    # .onion access
    total_checks += 1
    try:
        import requests
        proxies = {'http': 'socks5://127.0.0.1:9050', 'https': 'socks5://127.0.0.1:9050'}
        response = requests.get("http://3g2upl4pq6kufc4m.onion", proxies=proxies, timeout=20)
        if response.status_code == 200:
            print(f"   ✅ .onion Access        - Working (DuckDuckGo)")
            passed_checks += 1
        else:
            print(f"   ❌ .onion Access        - Failed (Status: {response.status_code})")
    except Exception as e:
        print(f"   ❌ .onion Access        - Failed ({str(e)})")
    
    # 6. Summary and Recommendations
    print(f"\n📊 SUMMARY")
    print("=" * 15)
    
    success_rate = (passed_checks / total_checks) * 100
    print(f"Overall Status: {passed_checks}/{total_checks} checks passed ({success_rate:.1f}%)")
    
    if success_rate >= 90:
        print("🎉 EXCELLENT! All systems ready for dark web OSINT")
        print("   Your CIOT application should work without installation messages")
    elif success_rate >= 70:
        print("✅ GOOD! Most systems ready, minor issues detected")
        print("   Most tools should work, some may show installation messages")
    elif success_rate >= 50:
        print("⚠️ PARTIAL! Several components need attention")
        print("   Many tools will show installation messages")
    else:
        print("❌ CRITICAL! Major components missing")
        print("   Most tools will show installation messages")
    
    print(f"\n🔧 RECOMMENDATIONS")
    print("-" * 18)
    
    if passed_checks < total_checks:
        print("To fix missing components:")
        print("1. Run: python3 install_darkweb_tools.py")
        print("2. Install missing packages manually")
        print("3. Start Tor service if not running")
        print("4. Restart your CIOT application")
    
    print(f"\n📚 For detailed installation instructions:")
    print("   • Run the installation script: python3 install_darkweb_tools.py")
    print("   • Check the usage guide: DARKWEB_TOOLS_USAGE_GUIDE.md")
    print("   • Review Tor service guide: TOR_SERVICE_COMPREHENSIVE_GUIDE.md")

if __name__ == "__main__":
    main()