#!/usr/bin/env python3
"""
Cyber Investigation OSINT Toolkit - Main Application
Professional OSINT Investigation Platform

Author: CIOT Development Team
Version: 3.0
License: Open Source
"""

import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox
import webbrowser
import sys
import os
import json
import datetime
from pathlib import Path

# Add src directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from src.gui.tabs.surface_web_tab import SurfaceWebTab
from src.gui.tabs.image_analysis_tab import ImageAnalysisTab
from src.gui.tabs.darkweb_tab import DarkWebTab
from src.gui.tabs.ai_assistant_tab import AIAssistantTab
from src.gui.tabs.additional_tools_tab import AdditionalToolsTab
from src.gui.tabs.aadhaar_tab import AadhaarTab
from src.gui.tabs.dashboard_tab import DashboardTab
from src.gui.tabs.google_dorking_tab import GoogleDorkingTab
from src.core.case_management import CaseCreationDialog, ProfessionalSettingsDialog
from src.core.config_manager import ConfigManager
from src.core.audit_logger import AuditLogger
from src.utils.report_generator import ReportGenerator

class CIOTMainApp(ctk.CTk):
    """
    Main Application Class for Cyber Investigation OSINT Toolkit
    Enterprise-grade OSINT toolkit with case management, advanced analytics,
    and comprehensive reporting capabilities.
    """
    
    def __init__(self):
        super().__init__()
        
        # Configure main window
        self.title("🛡️ Cyber Investigation OSINT Toolkit")
        self.geometry("1900x1300")
        self.minsize(1700, 1100)
        
        # Set professional appearance
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        
        # Initialize core components
        self.config_manager = ConfigManager()
        self.audit_logger = AuditLogger()
        self.report_generator = ReportGenerator()
        
        # Initialize investigation variables
        self.loaded_tab_count = 0
        self.current_investigation = None
        self.investigation_log = []
        self.case_database = {}
        self.evidence_chain = []
        self.session_start_time = datetime.datetime.now()
        self.investigation_id = f"INV-{int(datetime.datetime.now().timestamp())}"
        
        # Setup application
        self.initialize_directories()
        self.setup_ui()
        self.start_investigation_session()
    
    def initialize_directories(self):
        """Initialize required directories"""
        directories = ['data/cases', 'data/evidence', 'data/reports', 'data/exports', 'logs']
        for directory in directories:
            Path(directory).mkdir(parents=True, exist_ok=True)
    
    def setup_ui(self):
        """Setup the main user interface"""
        # Header
        self.setup_header()
        
        # Global info button
        self.setup_global_info_button()
        
        # Main tabview
        self.setup_tabview()
        
        # Status bar
        self.setup_status_bar()
    
    def setup_header(self):
        """Setup application header"""
        header_frame = ctk.CTkFrame(self, height=80, corner_radius=15, fg_color=("#1a1a2e", "#16213e"))
        header_frame.pack(fill="x", padx=15, pady=(15, 10))
        header_frame.pack_propagate(False)

        # Title
        title_label = ctk.CTkLabel(
            header_frame,
            text="🛡️ Cyber Investigation OSINT Toolkit",
            font=ctk.CTkFont(size=26, weight="bold"),
            text_color=("#00d4ff", "#ffffff")
        )
        title_label.pack(pady=20)
    
    def setup_global_info_button(self):
        """Setup global info button below header"""
        info_frame = ctk.CTkFrame(self, height=40, corner_radius=10, fg_color="transparent")
        info_frame.pack(fill="x", padx=15, pady=(0, 5))
        info_frame.pack_propagate(False)
        

        # Info button positioned on the right (after dork button)
        self.global_info_btn = ctk.CTkButton(
            info_frame,
            text="ℹ️ Tab Info",
            width=100,
            height=30,
            font=ctk.CTkFont(size=12, weight="bold"),
            command=self.show_current_tab_info,
            fg_color=("#2b2b2b", "#3b3b3b"),
            hover_color=("#3b3b3b", "#4b4b4b"),
            corner_radius=8
        )
        self.global_info_btn.pack(side="right", padx=10, pady=5)

    # (Google dorking feature removed per user request)
    
    def setup_tabview(self):
        """Setup main tabview with all investigation tabs"""
        self.tabview = ctk.CTkTabview(
            self,
            width=1880,
            height=1000,
            corner_radius=15,
            border_width=2,
            segmented_button_fg_color=("#2a2a2a", "#2a2a2a"),
            segmented_button_selected_color=("#00d4ff", "#0099cc"),
            segmented_button_selected_hover_color=("#00b8e6", "#00b8e6"),
            fg_color="#1a1a1a"
        )
        self.tabview.pack(fill="both", expand=True, padx=15, pady=10)
        
        # Create all tabs
        self.create_tabs()
    
    def create_tabs(self):
        """Create all investigation tabs"""
        tabs = [
            ("📊 Dashboard", DashboardTab, 'dashboard_tab'),
            ("🔍 Surface Web OSINT", SurfaceWebTab, 'surface_web_tab'),
            ("🖼️ Image Analysis", ImageAnalysisTab, 'image_tab'),
            ("🕵️ Dark Web OSINT", DarkWebTab, 'darkweb_tab'),
            ("🤖 AI Assistant", AIAssistantTab, 'ai_tab'),
            ("🛠️ Additional Tools", AdditionalToolsTab, 'tools_tab'),
            ("🆔 Aadhaar Validator", AadhaarTab, 'aadhaar_tab')
        ]
        for label, cls, attr in tabs:
            self.tabview.add(label)
            frame = self.tabview.tab(label)
            instance = cls(frame)
            setattr(self, attr, instance)
            instance.pack(fill="both", expand=True)
    
    def setup_status_bar(self):
        """Setup status bar"""
        self.status_frame = ctk.CTkFrame(self, height=30, corner_radius=10)
        self.status_frame.pack(fill="x", padx=15, pady=(0, 15))
        self.status_frame.pack_propagate(False)
        
        self.status_label = ctk.CTkLabel(
            self.status_frame,
            text="✅ Ready | Cyber Investigation OSINT Toolkit",
            font=ctk.CTkFont(size=11)
        )
        self.status_label.pack(side="left", padx=15, pady=5)
    
    def start_investigation_session(self):
        """Start investigation session"""
        self.audit_logger.log_session_start(self.investigation_id)
        print(f"[INFO] Investigation session started - ID: {self.investigation_id}")
    
    def update_status(self, message):
        """Update status bar message"""
        self.status_label.configure(text=message)
    
    def show_current_tab_info(self):
        """Show information about the currently active tab"""
        current_tab = self.tabview.get()
        
        # Get the appropriate tab object and call its info method
        tab_info_methods = {
            "📊 Dashboard": self.show_dashboard_info,
            "🔍 Surface Web OSINT": self.show_surface_web_info,
            "🖼️ Image Analysis": self.show_image_analysis_info,
            "🕵️ Dark Web OSINT": self.show_darkweb_info,
            "🤖 AI Assistant": self.show_ai_assistant_info,
            "🛠️ Additional Tools": self.show_additional_tools_info,
            "🆔 Aadhaar Validator": self.show_aadhaar_info
        }
        
        info_method = tab_info_methods.get(current_tab)
        if info_method:
            info_method()
        else:
            self.show_general_info()
    
    def show_general_info(self):
        """Show general application information"""
        info_window = ctk.CTkToplevel(self)
        info_window.title("CIOT - General Information")
        info_window.geometry("700x500")
        info_window.transient(self)
        info_window.grab_set()
        
        content = ctk.CTkTextbox(info_window, wrap="word")
        content.pack(fill="both", expand=True, padx=20, pady=20)
        
        info_text = """🛡️ CYBER INVESTIGATION OSINT TOOLKIT (CIOT)
═══════════════════════════════════════════════════════════════════════════════

🎯 PROFESSIONAL OSINT INVESTIGATION PLATFORM

CIOT is a comprehensive, professional-grade platform designed for digital investigators, 
cybersecurity professionals, researchers, and law enforcement agencies. Built entirely 
with free and open-source technologies, CIOT provides enterprise-level capabilities 
without proprietary dependencies.

📋 AVAILABLE INVESTIGATION MODULES:

📊 DASHBOARD
   • Investigation overview and case management
   • Session tracking and audit logs
   • Professional reporting dashboard

🔍 SURFACE WEB OSINT
   • Email address investigation and validation
   • Phone number analysis and carrier identification
   • IP address geolocation and threat intelligence
   • Full name and username investigations

🖼️ IMAGE ANALYSIS & FORENSICS
   • Multi-platform reverse image search
   • EXIF metadata extraction and analysis
   • Cryptographic hash generation
   • Professional forensic tool integration

🕵️ DARK WEB INVESTIGATION
   • .onion URL analysis and scanning
   • Dark web marketplace investigation
   • Cryptocurrency transaction analysis
   • Anonymous network analysis

🤖 AI-POWERED ASSISTANT
   • Intelligent investigation guidance
   • OSINT methodology recommendations
   • Automated research suggestions

🛠️ ADDITIONAL OSINT TOOLS
   • Extended toolkit for comprehensive investigations
   • Specialized utilities and resources

🆔 AADHAAR VALIDATOR
   • Identity verification tools
   • Document validation systems

🛡️ SECURITY & COMPLIANCE:
• 100% Open Source with complete transparency
• Privacy-first design with local data storage
• Evidence integrity with SHA-256 verification
• Professional audit logging for legal compliance

⚖️ LEGAL & ETHICAL USE ONLY
This toolkit is designed for legitimate investigation purposes only. 
Users must comply with all applicable laws and regulations."""

        content.insert("1.0", info_text)
        content.configure(state="disabled")
    
    def show_dashboard_info(self):
        """Show Dashboard tab information"""
        if hasattr(self, 'dashboard_tab') and hasattr(self.dashboard_tab, 'show_info_popup'):
            self.dashboard_tab.show_info_popup()
        else:
            self.show_general_info()
    
    def show_surface_web_info(self):
        """Show Surface Web OSINT tab information"""
        if hasattr(self, 'surface_web_tab') and hasattr(self.surface_web_tab, 'show_info_popup'):
            self.surface_web_tab.show_info_popup()
        else:
            self.show_general_info()
    
    def show_image_analysis_info(self):
        """Show Image Analysis tab information"""
        if hasattr(self, 'image_tab') and hasattr(self.image_tab, 'show_info_popup'):
            self.image_tab.show_info_popup()
        else:
            self.show_general_info()
    
    def show_darkweb_info(self):
        """Show Dark Web OSINT tab information"""
        if hasattr(self, 'darkweb_tab') and hasattr(self.darkweb_tab, 'show_info_popup'):
            self.darkweb_tab.show_info_popup()
        else:
            self.show_general_info()
    
    def show_ai_assistant_info(self):
        """Show AI Assistant tab information"""
        if hasattr(self, 'ai_tab') and hasattr(self.ai_tab, 'show_info_popup'):
            self.ai_tab.show_info_popup()
        else:
            self.show_general_info()
    
    def show_additional_tools_info(self):
        """Show Additional Tools tab information"""
        if hasattr(self, 'tools_tab') and hasattr(self.tools_tab, 'show_info_popup'):
            self.tools_tab.show_info_popup()
        else:
            self.show_general_info()
    
    def show_aadhaar_info(self):
        """Show Aadhaar Validator tab information"""
        if hasattr(self, 'aadhaar_tab') and hasattr(self.aadhaar_tab, 'show_info_popup'):
            self.aadhaar_tab.show_info_popup()
        else:
            self.show_general_info()

def main():
    """Main application entry point"""
    print("🚀 Starting Cyber Investigation OSINT Toolkit...")
    print("📋 Checking dependencies...")
    
    try:
        import customtkinter
        print("✅ CustomTkinter available")
        import requests
        print("✅ Requests available")
        from PIL import Image
        print("✅ PIL/Pillow available")
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        print("Please install requirements: pip install -r requirements.txt")
        return
    
    print("🎯 Launching application...")
    
    try:
        app = CIOTMainApp()
        print("✅ All tabs loaded successfully")
        app.mainloop()
    except Exception as e:
        print(f"❌ Application error: {e}")
    finally:
        print("👋 Cyber Investigation OSINT Toolkit closed")

# Main function is called from ciot.py entry point