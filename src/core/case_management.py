#!/usr/bin/env python3
"""
Case Management System for CIOT
Handles investigation case creation and management
"""

import customtkinter as ctk
from tkinter import messagebox
import datetime
import os

class CaseCreationDialog(ctk.CTkToplevel):
    """Professional case creation dialog"""
    
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        
        self.title("🆕 Create New Investigation Case")
        self.geometry("600x500")
        self.resizable(False, False)
        
        self.setup_ui()
    
    def setup_ui(self):
        """Setup case creation UI"""
        # Header
        header_label = ctk.CTkLabel(
            self,
            text="🆕 Create New Investigation Case",
            font=ctk.CTkFont(size=20, weight="bold")
        )
        header_label.pack(pady=20)
        
        # Form frame
        form_frame = ctk.CTkFrame(self)
        form_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Case name
        ctk.CTkLabel(form_frame, text="📋 Case Name:", 
                    font=ctk.CTkFont(size=14, weight="bold")).pack(anchor="w", padx=20, pady=(20, 5))
        self.case_name_entry = ctk.CTkEntry(form_frame, width=500, height=35)
        self.case_name_entry.pack(padx=20, pady=(0, 15))
        
        # Case type
        ctk.CTkLabel(form_frame, text="🔍 Investigation Type:", 
                    font=ctk.CTkFont(size=14, weight="bold")).pack(anchor="w", padx=20, pady=(0, 5))
        self.case_type_var = ctk.StringVar(value="General OSINT")
        case_type_menu = ctk.CTkOptionMenu(
            form_frame,
            values=["General OSINT", "Image Analysis", "Profile Investigation", 
                   "Digital Forensics", "Threat Intelligence"],
            variable=self.case_type_var,
            width=500,
            height=35
        )
        case_type_menu.pack(padx=20, pady=(0, 15))
        
        # Description
        ctk.CTkLabel(form_frame, text="📝 Case Description:", 
                    font=ctk.CTkFont(size=14, weight="bold")).pack(anchor="w", padx=20, pady=(0, 5))
        self.description_text = ctk.CTkTextbox(form_frame, width=500, height=100)
        self.description_text.pack(padx=20, pady=(0, 15))
        
        # Priority
        ctk.CTkLabel(form_frame, text="⚡ Priority Level:", 
                    font=ctk.CTkFont(size=14, weight="bold")).pack(anchor="w", padx=20, pady=(0, 5))
        self.priority_var = ctk.StringVar(value="Medium")
        priority_menu = ctk.CTkOptionMenu(
            form_frame,
            values=["Low", "Medium", "High", "Critical"],
            variable=self.priority_var,
            width=500,
            height=35
        )
        priority_menu.pack(padx=20, pady=(0, 20))
        
        # Buttons
        button_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        button_frame.pack(fill="x", padx=20, pady=20)
        
        create_btn = ctk.CTkButton(
            button_frame,
            text="✅ Create Case",
            command=self.create_case,
            width=150,
            height=40,
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color="#00aa44",
            hover_color="#008833"
        )
        create_btn.pack(side="left", padx=(0, 10))
        
        cancel_btn = ctk.CTkButton(
            button_frame,
            text="❌ Cancel",
            command=self.destroy,
            width=150,
            height=40,
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color="#666666",
            hover_color="#555555"
        )
        cancel_btn.pack(side="left")
    
    def create_case(self):
        """Create new investigation case"""
        case_name = self.case_name_entry.get().strip()
        if not case_name:
            messagebox.showerror("Error", "Please enter a case name")
            return
        
        case_id = f"CASE-{int(datetime.datetime.now().timestamp())}"
        case_data = {
            "case_id": case_id,
            "name": case_name,
            "type": self.case_type_var.get(),
            "description": self.description_text.get("1.0", "end-1c"),
            "priority": self.priority_var.get(),
            "created": datetime.datetime.now().isoformat(),
            "investigator": os.getenv("USER", "Unknown"),
            "status": "Active"
        }
        
        # Update parent with new case
        if hasattr(self.parent, 'case_database'):
            self.parent.case_database[case_id] = case_data
            self.parent.current_investigation = case_data
        
        # Log case creation
        if hasattr(self.parent, 'audit_logger'):
            self.parent.audit_logger.log_action("case_created", case_data)
        
        # Update UI
        if hasattr(self.parent, 'update_status'):
            self.parent.update_status(f"✅ New case created: {case_name}")
        
        self.destroy()

class ProfessionalSettingsDialog(ctk.CTkToplevel):
    """Professional settings configuration dialog"""
    
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        
        self.title("⚙️ CIOT Settings")
        self.geometry("700x600")
        self.resizable(False, False)
        
        self.setup_ui()
    
    def setup_ui(self):
        """Setup settings UI"""
        # Header
        header_label = ctk.CTkLabel(
            self,
            text="⚙️ CIOT Settings",
            font=ctk.CTkFont(size=20, weight="bold")
        )
        header_label.pack(pady=20)
        
        # Tabview for settings categories
        settings_tabview = ctk.CTkTabview(self, width=650, height=450)
        settings_tabview.pack(padx=20, pady=10)
        
        # General settings tab
        settings_tabview.add("🔧 General")
        general_frame = settings_tabview.tab("🔧 General")
        
        # Auto-save settings
        auto_save_frame = ctk.CTkFrame(general_frame)
        auto_save_frame.pack(fill="x", padx=10, pady=10)
        
        config = getattr(self.parent, 'config_manager', None)
        default_auto_save = config.get("auto_save", True) if config else True
        
        self.auto_save_var = ctk.BooleanVar(value=default_auto_save)
        auto_save_check = ctk.CTkCheckBox(
            auto_save_frame,
            text="Enable automatic session saving",
            variable=self.auto_save_var,
            font=ctk.CTkFont(size=12, weight="bold")
        )
        auto_save_check.pack(anchor="w", padx=15, pady=15)
        
        # Privacy settings tab
        settings_tabview.add("🔒 Privacy")
        privacy_frame = settings_tabview.tab("🔒 Privacy")
        
        privacy_info = ctk.CTkLabel(
            privacy_frame,
            text="🔒 Privacy & Security Settings\n\nAll CIOT operations use only free and open-source services.\nNo data is transmitted to paid or proprietary services.",
            font=ctk.CTkFont(size=12),
            justify="center"
        )
        privacy_info.pack(pady=20)
        
        default_anonymous = True
        if config and "privacy_settings" in config.config:
            default_anonymous = config.config["privacy_settings"].get("anonymous_mode", True)
        
        self.anonymous_var = ctk.BooleanVar(value=default_anonymous)
        anonymous_check = ctk.CTkCheckBox(
            privacy_frame,
            text="Enable anonymous mode (recommended)",
            variable=self.anonymous_var,
            font=ctk.CTkFont(size=12, weight="bold")
        )
        anonymous_check.pack(pady=10)
        
        # About tab
        settings_tabview.add("ℹ️ About")
        about_frame = settings_tabview.tab("ℹ️ About")
        
        about_text = ctk.CTkLabel(
            about_frame,
            text="""🛡️ Cyber Investigation OSINT Toolkit
Version 3.0

🌟 Features:
• 100% Free and Open Source
• Professional Investigation Tools
• Advanced Digital Forensics
• Comprehensive OSINT Capabilities
• Evidence Chain Management
• Professional Reporting

🔧 Built with:
• Python & CustomTkinter
• Free Online Services
• Open Source Libraries

⚖️ Legal & Ethical Use Only
Designed for legitimate investigation purposes""",
            font=ctk.CTkFont(size=11),
            justify="left"
        )
        about_text.pack(pady=20, padx=20)
        
        # Buttons
        button_frame = ctk.CTkFrame(self, fg_color="transparent")
        button_frame.pack(fill="x", padx=20, pady=20)
        
        save_btn = ctk.CTkButton(
            button_frame,
            text="💾 Save Settings",
            command=self.save_settings,
            width=150,
            height=40,
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color="#00aa44",
            hover_color="#008833"
        )
        save_btn.pack(side="left", padx=(0, 10))
        
        close_btn = ctk.CTkButton(
            button_frame,
            text="❌ Close",
            command=self.destroy,
            width=150,
            height=40,
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color="#666666",
            hover_color="#555555"
        )
        close_btn.pack(side="left")
    
    def save_settings(self):
        """Save settings configuration"""
        config_manager = getattr(self.parent, 'config_manager', None)
        if config_manager:
            config_manager.set("auto_save", self.auto_save_var.get())
            
            privacy_settings = config_manager.get("privacy_settings", {})
            privacy_settings["anonymous_mode"] = self.anonymous_var.get()
            config_manager.set("privacy_settings", privacy_settings)
        
        # Log settings update
        audit_logger = getattr(self.parent, 'audit_logger', None)
        if audit_logger:
            audit_logger.log_action("settings_updated")
        
        # Update status
        if hasattr(self.parent, 'update_status'):
            self.parent.update_status("✅ Settings saved successfully")
        
        self.destroy()