#!/usr/bin/env python3
"""
CIOT (Cyber Investigation & OSINT Toolkit) - Main Application
Professional OSINT toolkit for cybersecurity investigations
"""

import customtkinter as ctk
import sys
import os
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent))

# Import tabs
from gui.tabs.surface_web_tab import SurfaceWebTab
from gui.tabs.darkweb_tab import DarkWebTab

class CIOTMainApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        # Configure window
        self.title("CIOT - Cyber Investigation & OSINT Toolkit")
        self.geometry("1400x900")
        self.minsize(1200, 800)
        
        # Configure grid
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        
        # Set theme
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        
        # Initialize UI
        self.setup_ui()
        
    def setup_ui(self):
        """Setup the main user interface"""
        # Create main container
        main_container = ctk.CTkFrame(self)
        main_container.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        main_container.grid_rowconfigure(1, weight=1)
        main_container.grid_columnconfigure(0, weight=1)
        
        # Header
        header_frame = ctk.CTkFrame(main_container)
        header_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=(10, 5))
        header_frame.grid_columnconfigure(1, weight=1)
        
        # Logo/Title
        title_label = ctk.CTkLabel(
            header_frame,
            text="🕵️ CIOT - Cyber Investigation & OSINT Toolkit",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        title_label.grid(row=0, column=0, padx=20, pady=15, sticky="w")
        
        # Version info
        version_label = ctk.CTkLabel(
            header_frame,
            text="v1.0 - Professional OSINT Suite",
            font=ctk.CTkFont(size=12)
        )
        version_label.grid(row=0, column=1, padx=20, pady=15, sticky="e")
        
        # Create tabview
        self.tabview = ctk.CTkTabview(main_container)
        self.tabview.grid(row=1, column=0, sticky="nsew", padx=10, pady=(5, 10))
        
        # Add tabs
        self.setup_tabs()
        
    def setup_tabs(self):
        """Setup all investigation tabs"""
        # Surface Web OSINT Tab
        surface_tab = self.tabview.add("🌐 Surface Web OSINT")
        self.surface_web_tab = SurfaceWebTab(surface_tab)
        self.surface_web_tab.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Dark Web OSINT Tab
        dark_tab = self.tabview.add("🕸️ Dark Web OSINT")
        self.dark_web_tab = DarkWebTab(dark_tab)
        self.dark_web_tab.pack(fill="both", expand=True, padx=10, pady=10)
        
        # AI Assistant Tab (placeholder for future implementation)
        ai_tab = self.tabview.add("🤖 AI Assistant")
        ai_placeholder = ctk.CTkLabel(
            ai_tab,
            text="🤖 AI Assistant Tab\n\nComing Soon!\nIntelligent OSINT guidance and analysis",
            font=ctk.CTkFont(size=16)
        )
        ai_placeholder.pack(expand=True)
        
        # Additional Tools Tab (placeholder for future implementation)
        tools_tab = self.tabview.add("🛠️ Additional Tools")
        tools_placeholder = ctk.CTkLabel(
            tools_tab,
            text="🛠️ Additional Tools Tab\n\nComing Soon!\nNetwork tools, social media analysis, and more",
            font=ctk.CTkFont(size=16)
        )
        tools_placeholder.pack(expand=True)
        
        # Set default tab
        self.tabview.set("🌐 Surface Web OSINT")
    
    def on_closing(self):
        """Handle application closing"""
        self.destroy()

def main():
    """Main application entry point"""
    try:
        # Create and run application
        app = CIOTMainApp()
        app.protocol("WM_DELETE_WINDOW", app.on_closing)
        app.mainloop()
        
    except Exception as e:
        print(f"❌ Application error: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())