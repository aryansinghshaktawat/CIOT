#!/usr/bin/env python3
"""
Complete Dark Web OSINT Tools Installation and Verification Script
Installs and verifies all required dependencies for full functionality
"""

import subprocess
import sys
import os
import platform
import socket
import requests
from pathlib import Path

def run_command(command, description, ignore_errors=False):
    """Run a command and return success status"""
    print(f"🔧 {description}...")
    try:
        if isinstance(command, str):
            result = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=300)
        else:
            result = subprocess.run(command, capture_output=True, text=True, timeout=300)
        
        if result.returncode == 0:
            print(f"   ✅ Success: {description}")
            if result.stdout.strip():
                print(f"   📝 Output: {result.stdout.strip()[:200]}...")
            return True
        else:
            if ignore_errors:
                print(f"   ⚠️ Warning: {description} - {result.stderr.strip()[:100]}")
                return False
            else:
                print(f"   ❌ Failed: {description}")
                print(f"   📝 Error: {result.stderr.strip()}")
                return False
    except subprocess.TimeoutExpired:
        print(f"   ⏰ Timeout: {description}")
        return False
    except Exception as e:
        print(f"   ❌ Exception: {description} - {str(e)}")
        return False

def check_python_package(package_name):
    """Check if a Python package is installed"""
    try:
        __import__(package_name)
        return True
    except ImportError:
        return False

def install_python_packages():
    """Install required Python packages"""
    print("\n📦 INSTALLING PYTHON PACKAGES")
    print("=" * 40)
    
    packages = [
        "requests[socks]",
        "beautifulsoup4", 
        "lxml",
        "aiohttp",
        "h8mail",
        "finalrecon",
        "python-whois",
        "dnspython",
        "cryptography",
        "pysocks",
        "stem"  # Tor controller library
    ]
    
    success_count = 0
    for package in packages:
        if run_command([sys.executable, "-m", "pip", "install", package], f"Installing {package}"):
            success_count += 1
    
    print(f"\n📊 Python packages: {success_count}/{len(packages)} installed successfully")
    return success_count == len(packages)

def install_tor_service():
    """Install and configure Tor service"""
    print("\n🧅 INSTALLING TOR SERVICE")
    print("=" * 30)
    
    system = platform.system().lower()
    
    if system == "darwin":  # macOS
        print("🍎 macOS detected - using Homebrew")
        
        # Check if Homebrew is installed
        if not run_command("which brew", "Checking Homebrew", ignore_errors=True):
            print("📥 Installing Homebrew...")
            homebrew_install = '/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"'
            if not run_command(homebrew_install, "Installing Homebrew"):
                print("❌ Failed to install Homebrew. Please install manually.")
                return False
        
        # Install Tor
        if run_command("brew install tor", "Installing Tor via Homebrew"):
            run_command("brew services start tor", "Starting Tor service", ignore_errors=True)
            return True
        
    elif system == "linux":
        print("🐧 Linux detected")
        
        # Try different package managers
        package_managers = [
            ("apt", ["sudo", "apt", "update"], ["sudo", "apt", "install", "-y", "tor"]),
            ("yum", None, ["sudo", "yum", "install", "-y", "tor"]),
            ("dnf", None, ["sudo", "dnf", "install", "-y", "tor"]),
            ("pacman", None, ["sudo", "pacman", "-S", "--noconfirm", "tor"])
        ]
        
        for pm, update_cmd, install_cmd in package_managers:
            if run_command(f"which {pm}", f"Checking {pm}", ignore_errors=True):
                print(f"📦 Using {pm} package manager")
                
                if update_cmd:
                    run_command(update_cmd, f"Updating {pm} repositories", ignore_errors=True)
                
                if run_command(install_cmd, f"Installing Tor via {pm}"):
                    # Start Tor service
                    run_command(["sudo", "systemctl", "start", "tor"], "Starting Tor service", ignore_errors=True)
                    run_command(["sudo", "systemctl", "enable", "tor"], "Enabling Tor service", ignore_errors=True)
                    return True
                break
    
    else:
        print("🪟 Windows detected - manual installation required")
        print("   📥 Download Tor Browser: https://www.torproject.org/download/")
        print("   📥 Or use WSL for Linux installation")
        return False
    
    return False

def install_onionscan():
    """Install OnionScan (Go-based tool)"""
    print("\n🧅 INSTALLING ONIONSCAN")
    print("=" * 25)
    
    # Check if Go is installed
    if not run_command("go version", "Checking Go installation", ignore_errors=True):
        print("📥 Go not found. Installing Go...")
        
        system = platform.system().lower()
        if system == "darwin":
            run_command("brew install go", "Installing Go via Homebrew", ignore_errors=True)
        elif system == "linux":
            run_command("sudo apt install golang-go", "Installing Go via apt", ignore_errors=True)
        else:
            print("   ⚠️ Please install Go manually: https://golang.org/dl/")
            return False
    
    # Clone and build OnionScan
    onionscan_dir = Path.home() / "onionscan"
    
    if not onionscan_dir.exists():
        if run_command(f"git clone https://github.com/s-rah/onionscan.git {onionscan_dir}", "Cloning OnionScan"):
            os.chdir(onionscan_dir)
            if run_command("go build", "Building OnionScan"):
                print(f"   ✅ OnionScan installed at {onionscan_dir}")
                return True
    else:
        print(f"   ✅ OnionScan already exists at {onionscan_dir}")
        return True
    
    return False

def install_osint_spy():
    """Install OSINT-SPY"""
    print("\n🕵️ INSTALLING OSINT-SPY")
    print("=" * 25)
    
    osint_spy_dir = Path.home() / "osint-spy"
    
    if not osint_spy_dir.exists():
        if run_command(f"git clone https://github.com/SharadKumar97/OSINT-SPY.git {osint_spy_dir}", "Cloning OSINT-SPY"):
            os.chdir(osint_spy_dir)
            if run_command("pip install -r requirements.txt", "Installing OSINT-SPY requirements", ignore_errors=True):
                print(f"   ✅ OSINT-SPY installed at {osint_spy_dir}")
                return True
    else:
        print(f"   ✅ OSINT-SPY already exists at {osint_spy_dir}")
        return True
    
    return False

def verify_installations():
    """Verify all installations"""
    print("\n🔍 VERIFYING INSTALLATIONS")
    print("=" * 30)
    
    verifications = []
    
    # Check Python packages
    python_packages = [
        ("requests", "HTTP requests library"),
        ("bs4", "BeautifulSoup4 HTML parser"),
        ("lxml", "XML/HTML parser"),
        ("aiohttp", "Async HTTP client"),
        ("whois", "WHOIS lookup library"),
        ("dns", "DNS resolution library"),
        ("socks", "SOCKS proxy support"),
        ("stem", "Tor controller library")
    ]
    
    for package, description in python_packages:
        if check_python_package(package):
            print(f"   ✅ {package} - {description}")
            verifications.append(True)
        else:
            print(f"   ❌ {package} - {description}")
            verifications.append(False)
    
    # Check h8mail
    if run_command("h8mail --version", "h8mail version check", ignore_errors=True):
        print("   ✅ h8mail - Email breach hunting tool")
        verifications.append(True)
    else:
        print("   ❌ h8mail - Email breach hunting tool")
        verifications.append(False)
    
    # Check finalrecon
    if run_command("finalrecon --version", "finalrecon version check", ignore_errors=True):
        print("   ✅ finalrecon - Web reconnaissance tool")
        verifications.append(True)
    else:
        print("   ❌ finalrecon - Web reconnaissance tool")
        verifications.append(False)
    
    # Check Tor service
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(2)
        result = sock.connect_ex(('127.0.0.1', 9050))
        if result == 0:
            print("   ✅ Tor SOCKS proxy (port 9050) - Accessible")
            verifications.append(True)
        else:
            print("   ❌ Tor SOCKS proxy (port 9050) - Not accessible")
            verifications.append(False)
        sock.close()
    except:
        print("   ❌ Tor SOCKS proxy - Connection test failed")
        verifications.append(False)
    
    # Check OnionScan
    onionscan_path = Path.home() / "onionscan" / "onionscan"
    if onionscan_path.exists():
        print(f"   ✅ OnionScan - Available at {onionscan_path}")
        verifications.append(True)
    else:
        print("   ❌ OnionScan - Not found")
        verifications.append(False)
    
    # Check OSINT-SPY
    osint_spy_path = Path.home() / "osint-spy"
    if osint_spy_path.exists():
        print(f"   ✅ OSINT-SPY - Available at {osint_spy_path}")
        verifications.append(True)
    else:
        print("   ❌ OSINT-SPY - Not found")
        verifications.append(False)
    
    success_rate = sum(verifications) / len(verifications) * 100
    print(f"\n📊 Overall Success Rate: {success_rate:.1f}% ({sum(verifications)}/{len(verifications)})")
    
    return success_rate > 80

def test_functionality():
    """Test actual functionality of installed tools"""
    print("\n🧪 TESTING FUNCTIONALITY")
    print("=" * 25)
    
    # Test h8mail
    print("📧 Testing h8mail...")
    if run_command("h8mail -t test@example.com --no-banner", "h8mail test run", ignore_errors=True):
        print("   ✅ h8mail is functional")
    else:
        print("   ⚠️ h8mail test failed (may need API keys)")
    
    # Test finalrecon
    print("🎯 Testing finalrecon...")
    if run_command("finalrecon --domain example.com --quick", "finalrecon test run", ignore_errors=True):
        print("   ✅ finalrecon is functional")
    else:
        print("   ⚠️ finalrecon test failed")
    
    # Test Tor connectivity
    print("🧅 Testing Tor connectivity...")
    try:
        proxies = {'http': 'socks5://127.0.0.1:9050', 'https': 'socks5://127.0.0.1:9050'}
        response = requests.get('http://httpbin.org/ip', proxies=proxies, timeout=10)
        if response.status_code == 200:
            print("   ✅ Tor proxy is working")
            print(f"   📍 Exit IP: {response.json().get('origin', 'Unknown')}")
        else:
            print("   ❌ Tor proxy test failed")
    except Exception as e:
        print(f"   ❌ Tor connectivity test failed: {str(e)}")
    
    # Test .onion access
    print("🌐 Testing .onion access...")
    try:
        proxies = {'http': 'socks5://127.0.0.1:9050', 'https': 'socks5://127.0.0.1:9050'}
        response = requests.get('http://3g2upl4pq6kufc4m.onion', proxies=proxies, timeout=15)
        if response.status_code == 200:
            print("   ✅ .onion access working (DuckDuckGo)")
        else:
            print("   ❌ .onion access failed")
    except Exception as e:
        print(f"   ⚠️ .onion access test failed: {str(e)}")

def create_usage_guide():
    """Create a usage guide for the installed tools"""
    guide_content = """# 🕸️ Dark Web OSINT Tools - Usage Guide

## 🚀 Quick Start Commands

### h8mail - Email Breach Hunting
```bash
# Basic email check
h8mail -t target@email.com

# Advanced with chase mode
h8mail -t target@email.com --chase

# Use local breach files
h8mail -t target@email.com -lb /path/to/breaches/
```

### finalrecon - Web Reconnaissance
```bash
# Full scan
finalrecon --domain target.com --full

# Quick scan
finalrecon --domain target.com --quick

# Specific modules
finalrecon --domain target.com --headers --ssl --whois
```

### OnionScan - Hidden Service Analysis
```bash
# Basic scan
~/onionscan/onionscan target.onion

# Verbose output
~/onionscan/onionscan --verbose target.onion

# JSON output
~/onionscan/onionscan --jsonReport target.onion
```

### OSINT-SPY - Multi-target Intelligence
```bash
# Email investigation
cd ~/osint-spy && python osint-spy.py -e target@email.com

# Domain investigation  
cd ~/osint-spy && python osint-spy.py -d target.com

# IP investigation
cd ~/osint-spy && python osint-spy.py -ip 192.168.1.1
```

## 🧅 Tor Usage

### Start Tor Service
```bash
# macOS
brew services start tor

# Linux
sudo systemctl start tor
```

### Test Tor Connection
```bash
# Check SOCKS proxy
curl --socks5 127.0.0.1:9050 http://httpbin.org/ip

# Test .onion access
curl --socks5 127.0.0.1:9050 http://3g2upl4pq6kufc4m.onion
```

### Python with Tor
```python
import requests

proxies = {
    'http': 'socks5://127.0.0.1:9050',
    'https': 'socks5://127.0.0.1:9050'
}

response = requests.get('http://example.onion', proxies=proxies)
```

## 🔑 API Keys (Optional but Recommended)

### HaveIBeenPwned (for h8mail)
1. Get API key: https://haveibeenpwned.com/API/Key
2. Set environment variable: `export HIBP_API_KEY=your_key_here`

### VirusTotal (for enhanced analysis)
1. Get API key: https://www.virustotal.com/gui/join-us
2. Set environment variable: `export VT_API_KEY=your_key_here`

## ⚖️ Legal Reminder
- Only use for authorized investigations
- Respect terms of service
- Follow local laws and regulations
- Report illegal content to authorities

## 🛡️ Security Best Practices
- Use VPN + Tor for additional anonymity
- Regularly rotate Tor circuits
- Never download suspicious files
- Clear browser data frequently
- Use Tails OS for maximum security
"""
    
    with open("DARKWEB_TOOLS_USAGE_GUIDE.md", "w") as f:
        f.write(guide_content)
    
    print("📚 Usage guide created: DARKWEB_TOOLS_USAGE_GUIDE.md")

def main():
    """Main installation and verification process"""
    print("🕸️ DARK WEB OSINT TOOLS - COMPLETE INSTALLATION")
    print("=" * 55)
    print("This script will install and verify all required tools for")
    print("full dark web OSINT functionality in your CIOT application.")
    print()
    
    # Check system requirements
    print(f"🖥️ System: {platform.system()} {platform.release()}")
    print(f"🐍 Python: {sys.version}")
    print()
    
    # Installation steps
    steps = [
        ("Installing Python packages", install_python_packages),
        ("Installing Tor service", install_tor_service),
        ("Installing OnionScan", install_onionscan),
        ("Installing OSINT-SPY", install_osint_spy)
    ]
    
    results = []
    for step_name, step_func in steps:
        print(f"\n🔄 {step_name}...")
        try:
            result = step_func()
            results.append(result)
            if result:
                print(f"✅ {step_name} completed successfully")
            else:
                print(f"⚠️ {step_name} completed with warnings")
        except Exception as e:
            print(f"❌ {step_name} failed: {str(e)}")
            results.append(False)
    
    # Verification
    print("\n" + "=" * 55)
    verification_success = verify_installations()
    
    # Functionality testing
    test_functionality()
    
    # Create usage guide
    create_usage_guide()
    
    # Final summary
    print("\n🎉 INSTALLATION SUMMARY")
    print("=" * 25)
    success_count = sum(results)
    total_steps = len(results)
    
    print(f"📊 Installation Steps: {success_count}/{total_steps} successful")
    print(f"🔍 Verification: {'✅ Passed' if verification_success else '⚠️ Issues detected'}")
    
    if success_count >= 3 and verification_success:
        print("\n🚀 READY FOR DARK WEB OSINT!")
        print("Your CIOT application now has full dark web investigation capabilities.")
        print("All tools should work without 'Install for full functionality' messages.")
    else:
        print("\n⚠️ PARTIAL INSTALLATION")
        print("Some tools may still show installation messages.")
        print("Check the verification results above and install missing components.")
    
    print("\n📚 Next Steps:")
    print("1. Restart your CIOT application")
    print("2. Test the Dark Web OSINT tab")
    print("3. Check DARKWEB_TOOLS_USAGE_GUIDE.md for usage instructions")
    print("4. Configure API keys for enhanced functionality")

if __name__ == "__main__":
    main()