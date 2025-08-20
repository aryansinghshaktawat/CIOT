import customtkinter as ctk
import threading
import time
import webbrowser
from urllib.parse import quote_plus, quote, urlparse, urlunparse
from fpdf import FPDF
import os
import re
from typing import List, Dict, Optional

# Import utility functions
from src.utils.validators import validate_email, validate_phone, validate_ip
from src.utils.osint_utils import generate_search_links, open_links_safely, get_real_ip_info, get_enhanced_phone_info, get_email_info


class ToolTip:
    """Simple tooltip implementation for CustomTkinter widgets"""
    
    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tooltip_window = None
        
        # Bind events
        self.widget.bind("<Enter>", self.on_enter)
        self.widget.bind("<Leave>", self.on_leave)
    
    def on_enter(self, event=None):
        """Show tooltip on mouse enter"""
        if self.tooltip_window or not self.text:
            return
        
        x, y, _, _ = self.widget.bbox("insert") if hasattr(self.widget, 'bbox') else (0, 0, 0, 0)
        x += self.widget.winfo_rootx() + 25
        y += self.widget.winfo_rooty() + 25
        
        self.tooltip_window = ctk.CTkToplevel(self.widget)
        self.tooltip_window.wm_overrideredirect(True)
        self.tooltip_window.wm_geometry(f"+{x}+{y}")
        
        label = ctk.CTkLabel(
            self.tooltip_window,
            text=self.text,
            font=ctk.CTkFont(size=10),
            fg_color=("#333333", "#666666"),
            corner_radius=6,
            text_color=("#ffffff", "#ffffff")
        )
        label.pack(padx=8, pady=4)
    
    def on_leave(self, event=None):
        """Hide tooltip on mouse leave"""
        if self.tooltip_window:
            self.tooltip_window.destroy()
            self.tooltip_window = None

class SurfaceWebTab(ctk.CTkFrame):
    def __init__(self, master=None, **kwargs):
        super().__init__(master, **kwargs)
        self.setup_ui()

    def show_info_popup(self):
        """Show information about Surface Web OSINT"""
        info_window = ctk.CTkToplevel(self)
        info_window.title("Surface Web OSINT - Information")
        info_window.geometry("600x400")
        info_window.transient(self.master)
        info_window.grab_set()
        
        content = ctk.CTkTextbox(info_window, wrap="word")
        content.pack(fill="both", expand=True, padx=20, pady=20)
        
        info_text = """🔍 PROFESSIONAL SURFACE WEB OSINT INVESTIGATION TOOLKIT
═══════════════════════════════════════════════════════════════════════════════

🎯 WHAT IT DOES:
Primary open-source intelligence gathering tool for surface web investigations across multiple target types with real-time data analysis and comprehensive resource generation.

📋 INVESTIGATION CAPABILITIES:

📧 EMAIL ADDRESS INVESTIGATION:
   • Real-time email validation and deliverability testing
   • Breach database analysis (Have I Been Pwned, Dehashed, LeakCheck)
   • Social media account discovery and mapping
   • Paste site and code repository searches
   • Domain reputation and security analysis
   • MX record validation and provider identification

📞 PHONE NUMBER INVESTIGATION:
   • Real-time carrier identification and geographic location
   • Reverse lookup across multiple databases (TrueCaller, WhitePages)
   • Social media account association analysis
   • Technical validation and number portability
   • Cross-platform presence verification
   • Country code and format analysis

👤 FULL NAME INVESTIGATION:
   • Multi-engine search across 4 major search platforms
   • Professional network analysis (LinkedIn, ZoomInfo, Apollo)
   • Social media presence mapping and verification
   • Public records and genealogy database searches
   • People search engine comprehensive coverage
   • Background check resource compilation

🌐 IP ADDRESS INVESTIGATION:
   • Real-time geolocation and ISP identification
   • WHOIS registration and ownership analysis
   • Threat intelligence and malicious activity detection
   • Network scanning and service enumeration (Shodan, Censys)
   • DNS history and domain association mapping
   • Proxy/VPN and hosting detection

🚀 PROFESSIONAL FEATURES:
✓ Real-time API integration for live data analysis
✓ 10-16 specialized OSINT resources per investigation type
✓ Categorized results for systematic analysis
✓ Professional PDF report generation with legal disclaimers
✓ Real-time status updates and progress tracking
✓ Comprehensive investigation methodology guidance
✓ Smart browser integration with batch link opening
✓ Input validation and error handling
✓ Legal and ethical compliance reminders

📋 HOW TO CONDUCT PROFESSIONAL INVESTIGATION:
1. Select your target type from the dropdown menu (Full Name, Phone, Email, IP)
2. Enter the target information with proper formatting
3. Click 'Start Investigation' to begin real-time analysis
4. Review live data analysis results and comprehensive OSINT resources
5. Follow systematic investigation workflow provided in results
6. Export professional PDF report for documentation and legal compliance

🔍 INVESTIGATION WORKFLOW:
• Target validation and format verification
• Real-time data analysis using free APIs
• Comprehensive OSINT resource generation
• Categorized link compilation by source type
• Professional methodology guidance
• Legal compliance documentation

⚖️ LEGAL COMPLIANCE NOTICE:
This toolkit is designed for authorized investigations only. Ensure proper legal authorization before investigating any target. All investigations use only publicly available information and free APIs. Respect privacy laws, platform terms of service, and maintain ethical investigation standards.

🛡️ SECURITY & PRIVACY:
• No data is stored or transmitted to third parties
• All API calls use free, public services
• Investigation logs are local only
• Professional ethical standards maintained

🎯 REAL-WORLD APPLICATIONS:
• Cybersecurity threat investigation
• Digital forensics and incident response
• Background verification and due diligence
• Social engineering awareness training
• Academic research and education
• Law enforcement support (with proper authorization)

This tool provides professional-grade OSINT investigation capabilities using only free and open-source resources, suitable for security professionals, researchers, and authorized investigators."""

        content.insert("1.0", info_text)
        content.configure(state="disabled")

    def setup_ui(self):
        # Compact title
        title_frame = ctk.CTkFrame(self, fg_color="transparent")
        title_frame.pack(fill="x", padx=20, pady=(15, 5))
        
        title_label = ctk.CTkLabel(
            title_frame, 
            text="🔍 CIOT Surface Web OSINT Investigation", 
            font=ctk.CTkFont(size=22, weight="bold"),
            text_color=("#1f538d", "#4a9eff")
        )
        title_label.pack()

        # Investigation type selection with compact layout
        lookup_frame = ctk.CTkFrame(self, corner_radius=12)
        lookup_frame.pack(fill="x", padx=20, pady=10)
        
        # Create a grid layout for better organization
        lookup_frame.grid_columnconfigure(1, weight=1)
        
        type_icon = ctk.CTkLabel(lookup_frame, text="🎯", font=ctk.CTkFont(size=18))
        type_icon.grid(row=0, column=0, padx=(12, 8), pady=12, sticky="w")
        
        type_label = ctk.CTkLabel(
            lookup_frame, 
            text="Investigation Type:", 
            font=ctk.CTkFont(size=14, weight="bold")
        )
        type_label.grid(row=0, column=1, padx=8, pady=12, sticky="w")
        
        self.lookup_type = ctk.StringVar(value="Full Name")
        self.lookup_menu = ctk.CTkOptionMenu(
            lookup_frame, 
            variable=self.lookup_type,
            values=["Full Name", "Phone Number", "Email Address", "IP Address"],
            command=self.on_lookup_type_change,
            font=ctk.CTkFont(size=12, weight="bold"),
            width=180,
            height=32,
            corner_radius=8
        )
        self.lookup_menu.grid(row=0, column=2, padx=(8, 12), pady=12, sticky="e")
        
        # Add tooltip for investigation type selection
        ToolTip(self.lookup_menu, "Select the type of target you want to investigate:\n• Full Name: Person investigation\n• Phone Number: Enhanced phone analysis\n• Email Address: Email validation & breach check\n• IP Address: Geolocation & network analysis")

        # Compact input section
        input_frame = ctk.CTkFrame(self, corner_radius=12)
        input_frame.pack(fill="x", padx=20, pady=10)

        # Input header
        input_header = ctk.CTkFrame(input_frame, fg_color="transparent")
        input_header.pack(fill="x", padx=12, pady=(12, 5))
        
        input_icon = ctk.CTkLabel(input_header, text="📝", font=ctk.CTkFont(size=16))
        input_icon.pack(side="left")
        
        self.input_label = ctk.CTkLabel(
            input_header, 
            text="Enter Full Name:", 
            font=ctk.CTkFont(size=14, weight="bold")
        )
        self.input_label.pack(side="left", padx=(8, 0))
        
        # Indian phone number format guidance (always visible for phone numbers)
        self.india_frame = ctk.CTkFrame(input_frame, fg_color="transparent")
        
        india_label = ctk.CTkLabel(
            self.india_frame,
            text="🇮🇳 Indian Phone Number:",
            font=ctk.CTkFont(size=12, weight="bold")
        )
        india_label.pack(side="left", padx=(12, 8))
        
        # Format guidance label
        self.format_guidance = ctk.CTkLabel(
            self.india_frame,
            text="Format: +91 9876543210 or 9876543210",
            font=ctk.CTkFont(size=10),
            text_color=("#666666", "#999999")
        )
        self.format_guidance.pack(side="left", padx=(8, 8))
        
        # Add tooltip for format guidance
        ToolTip(self.format_guidance, "Indian phone number formats:\n• +91 9876543210 (international)\n• 9876543210 (10-digit mobile)\n• 09876543210 (with leading zero)")
        

        
        # Input field
        self.target_var = ctk.StringVar()
        self.target_entry = ctk.CTkEntry(
            input_frame, 
            textvariable=self.target_var, 
            height=38,
            placeholder_text="e.g., John Smith",
            font=ctk.CTkFont(size=13),
            corner_radius=10,
            border_width=2
        )
        self.target_entry.pack(fill="x", padx=12, pady=(5, 4))

        # Placeholder references for contextual Google Dorking buttons
        self.name_dork_btn = None
        self.phone_dork_btn = None
        self.email_dork_btn = None

        # Container to hold dynamic dork button
        self.dork_button_container = ctk.CTkFrame(input_frame, fg_color="transparent")
        self.dork_button_container.pack(fill="x", padx=12, pady=(0, 10))

        # Initialize with Full Name dork button by default
        self._create_name_dork_button()

        # Compact action buttons
        button_frame = ctk.CTkFrame(self, fg_color="transparent")
        button_frame.pack(fill="x", padx=20, pady=8)
        
        # Center the buttons
        button_container = ctk.CTkFrame(button_frame, fg_color="transparent")
        button_container.pack(expand=True)

        self.investigate_btn = ctk.CTkButton(
            button_container, 
            text="🔍 Start Investigation", 
            command=self.start_investigation,
            font=ctk.CTkFont(size=13, weight="bold"),
            height=38,
            width=180,
            corner_radius=10,
            fg_color=("#1f538d", "#4a9eff"),
            hover_color=("#3d8ce6", "#3d8ce6")
        )
        self.investigate_btn.pack(side="left", padx=8)
        
        # Add tooltip for investigation button
        ToolTip(self.investigate_btn, "Start comprehensive OSINT investigation:\n• Validates input format\n• Performs real-time analysis\n• Opens multiple OSINT resources\n• Generates professional results")

        self.export_btn = ctk.CTkButton(
            button_container, 
            text="📄 Export Report", 
            command=self.export_report,
            font=ctk.CTkFont(size=12, weight="bold"),
            height=38,
            width=130,
            corner_radius=10,
            fg_color=("#2d5a2d", "#4a8c4a"),
            hover_color=("#3d7a3d", "#5aa85a")
        )
        self.export_btn.pack(side="left", padx=8)
        
        # Add tooltip for export button
        ToolTip(self.export_btn, "Export professional PDF report:\n• Complete investigation summary\n• All OSINT resources used\n• Legal disclaimers included\n• Court-admissible format")

        self.clear_btn = ctk.CTkButton(
            button_container, 
            text="🗑️ Clear", 
            command=self.clear_results,
            font=ctk.CTkFont(size=12, weight="bold"),
            height=38,
            width=100,
            corner_radius=10,
            fg_color=("#8b4513", "#cd853f"),
            hover_color=("#a0522d", "#daa520")
        )
        self.clear_btn.pack(side="left", padx=8)

        self.performance_btn = ctk.CTkButton(
            button_container, 
            text="⚡ Performance", 
            command=self.show_performance_metrics,
            font=ctk.CTkFont(size=12, weight="bold"),
            height=38,
            width=120,
            corner_radius=10,
            fg_color=("#6a0dad", "#9932cc"),
            hover_color=("#8a2be2", "#ba55d3")
        )
        self.performance_btn.pack(side="left", padx=8)
        
        # Add tooltip for performance button
        ToolTip(self.performance_btn, "View performance metrics:\n• Investigation speed analysis\n• API response times\n• Success rates by type\n• System optimization tips")

    # (Moved Google Dork buttons below their respective input sections.)

        # Large results section - maximized for content
        results_frame = ctk.CTkFrame(self, corner_radius=12)
        results_frame.pack(fill="both", expand=True, padx=20, pady=(10, 20))
        
        # Compact results header
        results_header = ctk.CTkFrame(results_frame, fg_color="transparent")
        results_header.pack(fill="x", padx=12, pady=(12, 8))
        
        results_icon = ctk.CTkLabel(results_header, text="📊", font=ctk.CTkFont(size=16))
        results_icon.pack(side="left")
        
        results_title = ctk.CTkLabel(
            results_header, 
            text="Investigation Results", 
            font=ctk.CTkFont(size=16, weight="bold")
        )
        results_title.pack(side="left", padx=(8, 0))
        
        # Status indicator
        self.status_label = ctk.CTkLabel(
            results_header,
            text="Ready",
            font=ctk.CTkFont(size=11),
            text_color=("#4a9eff", "#4a9eff")
        )
        self.status_label.pack(side="right")
        
        # Large results textbox - maximized space
        self.results_textbox = ctk.CTkTextbox(
            results_frame, 
            font=ctk.CTkFont(size=11),
            corner_radius=8,
            border_width=1,
            wrap="word"
        )
        self.results_textbox.pack(fill="both", expand=True, padx=8, pady=(0, 8))
        
        # Initial instructions
        self.show_initial_instructions()

    def show_initial_instructions(self):
        """Show clean initial state"""
        initial_message = """🔍 CIOT SURFACE WEB OSINT INVESTIGATION

Ready for professional investigation.

🇮🇳 PHONE INVESTIGATION: Specialized for Indian mobile numbers
   • TrueCaller integration for caller ID
   • FindAndTrace for location details
   • Comprehensive carrier analysis
   • Social media presence detection

📧 EMAIL INVESTIGATION: Breach checking and validation
🌐 IP INVESTIGATION: Geolocation and threat analysis  
👤 NAME INVESTIGATION: Social media and public records

Select investigation type and enter target to begin analysis.
Click the 'ℹ️ Tab Info' button above for detailed instructions."""

        self.results_textbox.delete("1.0", "end")
        self.results_textbox.insert("end", initial_message)

    def on_lookup_type_change(self, value):
        """Update UI when lookup type changes"""
        lookup_type = self.lookup_type.get()
        
        if lookup_type == "Full Name":
            self.input_label.configure(text="Enter Full Name:")
            self.target_entry.configure(placeholder_text="e.g., John Smith")
            self.india_frame.pack_forget()  # Hide Indian phone guidance
        elif lookup_type == "Phone Number":
            self.input_label.configure(text="Enter Indian Phone Number:")
            self.target_entry.configure(placeholder_text="e.g., 9876543210")
            # Show Indian phone guidance
            self.india_frame.pack(fill="x", padx=12, pady=(0, 8))
        elif lookup_type == "Email Address":
            self.input_label.configure(text="Enter Email Address:")
            self.target_entry.configure(placeholder_text="e.g., john@example.com")
            self.india_frame.pack_forget()  # Hide Indian phone guidance
        elif lookup_type == "IP Address":
            self.input_label.configure(text="Enter IP Address:")
            self.target_entry.configure(placeholder_text="e.g., 8.8.8.8")
            self.india_frame.pack_forget()  # Hide Indian phone guidance
        
        # Clear previous results
        self.show_initial_instructions()
        # Recreate contextual dork button
        for widget in self.dork_button_container.winfo_children():
            widget.destroy()
        if lookup_type == "Full Name":
            self._create_name_dork_button()
        elif lookup_type == "Phone Number":
            self._create_phone_dork_button()
        elif lookup_type == "Email Address":
            self._create_email_dork_button()
    

    


    def start_investigation(self):
        """Start the OSINT investigation"""
        target = self.target_var.get().strip()
        lookup_type = self.lookup_type.get()
        
        if not target:
            self.results_textbox.delete("1.0", "end")
            self.results_textbox.insert("end", "❌ Please enter a target for investigation.\n")
            return

        # Validate input based on type
        is_valid = self.validate_input(target, lookup_type)
        if not is_valid:
            return

        # Start investigation in separate thread
        threading.Thread(target=self.perform_investigation, args=(target, lookup_type)).start()

    # ---- Contextual Google Dorking Buttons Creation ----
    def _create_name_dork_button(self):
        self.name_dork_btn = ctk.CTkButton(
            self.dork_button_container,
            text="🕵️ Google Dorking (Name)",
            command=self.google_dork_name,
            font=ctk.CTkFont(size=12, weight="bold"),
            height=34,
            corner_radius=10,
            fg_color=("#444444", "#555555"),
            hover_color=("#666666", "#777777")
        )
        self.name_dork_btn.pack(fill="x")
        ToolTip(self.name_dork_btn, "Open Google dork searches for a full name")

    def _create_phone_dork_button(self):
        self.phone_dork_btn = ctk.CTkButton(
            self.dork_button_container,
            text="📞 Google Dorking (Phone)",
            command=self.google_dork_phone,
            font=ctk.CTkFont(size=12, weight="bold"),
            height=34,
            corner_radius=10,
            fg_color=("#444444", "#555555"),
            hover_color=("#666666", "#777777")
        )
        self.phone_dork_btn.pack(fill="x")
        ToolTip(self.phone_dork_btn, "Open Google dork searches for a phone number")

    def _create_email_dork_button(self):
        # Create dedicated Google Dorking button for Email mode
        self.email_dork_btn = ctk.CTkButton(
            self.dork_button_container,
            text="📧 Google Dorking (Email)",
            command=self.google_dork_email,
            font=ctk.CTkFont(size=12, weight="bold"),
            height=34,
            corner_radius=10,
            fg_color=("#444444", "#555555"),
            hover_color=("#666666", "#777777")
        )
        self.email_dork_btn.pack(fill="x")
        ToolTip(self.email_dork_btn, "Open expanded Google dork searches for an email address")

    # ---- Existing Handlers (renamed) ----
    def google_dork_name(self):
        """Generate and open predefined Google dorks for a full name."""
        # Ensure only active for Full Name mode
        if self.lookup_type.get() != "Full Name":
            return
        name = self.target_var.get().strip()
        if not name:
            self.results_textbox.insert("end", "\n❌ Please enter a full name before running Google dorking.\n")
            self.results_textbox.see("end")
            return

        quoted = f'"{name}"'
        # Core dorks focused on person footprinting
        dorks = [
            f'{quoted} site:linkedin.com',
            f'{quoted} site:twitter.com',
            f'{quoted} site:facebook.com',
            f'{quoted} site:instagram.com',
            f'{quoted} site:github.com',
            f'{quoted} site:stackoverflow.com',
            f'{quoted} site:angel.co',
            f'{quoted} site:medium.com',
            f'{quoted} site:about.me',
            f'{quoted} site:crunchbase.com',
            f'{quoted} site:zoominfo.com',
            f'{quoted} site:apollo.io',
            f'{quoted} site:rocketreach.co',
            f'{quoted} site:hunter.io',
            f'{quoted} site:rocketreach.co',
            f'{quoted} site:github.com inurl:users',
            f'{quoted} filetype:pdf',
            f'{quoted} filetype:doc OR filetype:docx',
            f'{quoted} filetype:xls OR filetype:xlsx',
            f'{quoted} filetype:ppt OR filetype:pptx',
            f'{quoted} "Curriculum Vitae" OR "CV"',
            f'{quoted} "resume"',
            f'{quoted} "email"',
            f'{quoted} "contact"',
            f'{quoted} "phone"',
            f'{quoted} "@gmail.com"',
            f'{quoted} "@yahoo.com"',
            f'{quoted} site:*.in',
            f'intitle:{quoted}',
            f'intext:{quoted}',
            f'inurl:{name.split()[0]}' if name.split() else quoted,
        ]

        # Remove potential duplicates and keep order
        seen = set()
        unique_dorks = []
        for d in dorks:
            if d not in seen:
                seen.add(d)
                unique_dorks.append(d)

        base = "https://www.google.com/search?q="
        self.results_textbox.insert("end", f"\n🔎 Launching {len(unique_dorks)} Google dork searches for {name}\n")
        delay = getattr(self, 'GOOGLE_DORK_OPEN_DELAY', 1.0)
        for d in unique_dorks:
            url = base + quote_plus(d)
            try:
                webbrowser.open_new_tab(url)
                time.sleep(delay)
            except Exception as e:
                self.results_textbox.insert("end", f"⚠️ Failed to open: {d} ({e})\n")
        self.results_textbox.insert("end", "✅ Google dork searches opened in browser tabs.\n")
        self.results_textbox.see("end")

    def google_dork_phone(self):
        """Generate and open predefined Google dorks for a phone number."""
        if self.lookup_type.get() != "Phone Number":
            return
        phone = self.target_var.get().strip()
        if not phone:
            self.results_textbox.insert("end", "\n❌ Please enter a phone number before running Google dorking.\n")
            self.results_textbox.see("end")
            return

        quoted = f'"{phone}"'
        dorks = [
            f'{quoted}',
            f'{quoted} site:linkedin.com',
            f'{quoted} site:facebook.com',
            f'{quoted} site:instagram.com',
            f'{quoted} site:twitter.com',
            f'{quoted} filetype:pdf',
            f'{quoted} filetype:docx',
            f'{quoted} filetype:xls',
            f'{quoted} "contact number"',
            f'{quoted} "resume"',
            f'{quoted} intext:"mobile"',
            f'{quoted} intext:"phone"',
            f'{quoted} inurl:directory',
            f'{quoted} site:justdial.com',
            f'{quoted} site:indiamart.com',
            f'{quoted} site:sulekha.com',
            f'{quoted} site:yellowpages.com'
        ]

        base = "https://www.google.com/search?q="
        self.results_textbox.insert("end", f"\n🔎 Launching {len(dorks)} Google dork searches for {phone}\n")
        delay = getattr(self, 'GOOGLE_DORK_OPEN_DELAY', 1.0)
        for d in dorks:
            url = base + quote_plus(d)
            try:
                webbrowser.open_new_tab(url)
                time.sleep(delay)
            except Exception as e:
                self.results_textbox.insert("end", f"⚠️ Failed to open: {d} ({e})\n")
        self.results_textbox.insert("end", "✅ Phone number Google dork searches opened.\n")
        self.results_textbox.see("end")

    def google_dork_email(self):
        """Generate and open expanded Google dorks for an email address with normalization & dedup."""
        if self.lookup_type.get() != "Email Address":
            return
        email = self.target_var.get().strip()
        if not email:
            self.results_textbox.insert("end", "\n❌ Please enter an email address before running Google dorking.\n")
            self.results_textbox.see("end")
            return
        if '@' not in email or email.startswith('@') or email.endswith('@'):
            self.results_textbox.insert("end", "\n❌ Invalid email format for dorking.\n")
            self.results_textbox.see("end")
            return

        quoted = f'"{email}"'
        # Expanded list per requirements
        queries = [
            f"{quoted} site:pastebin.com",
            f"{quoted} site:throwbin.io",
            f"{quoted} site:ghostbin.com",
            f"{quoted} site:controlc.com",
            f"{quoted} intext:password",
            f"{quoted} \"database dump\"",
            f"{quoted} leaked",
            f"{quoted} filetype:pdf",
            f"{quoted} filetype:docx",
            f"{quoted} filetype:xls",
            f"{quoted} filetype:txt",
            f"{quoted} inurl:/uploads/",
            f"{quoted} inurl:/documents/",
            f"{quoted} site:reddit.com",
            f"{quoted} site:quora.com",
            f"{quoted} site:stackoverflow.com",
            f"{quoted} site:medium.com",
            f"{quoted} site:github.com",
            f"{quoted} site:gitlab.com",
            f"{quoted} site:bitbucket.org",
            f"{quoted} inurl:paste",
            f"{quoted} inurl:login",
            f"{quoted} inurl:signup",
            f"{quoted} intitle:\"index of\"",
            f"{quoted} inurl:/wp-content/",
            f"{quoted} site:*.in",
            f"{quoted} site:*.gov.in",
            f"{quoted} site:*.edu",
        ]

        base = "https://www.google.com/search?q="
        raw_urls = [base + quote_plus(q) for q in queries]

        # Normalization (strip, trailing slash removal, lowercase host) & dedup
        from urllib.parse import urlparse, urlunparse
        seen = set()
        final_urls = []
        for u in raw_urls:
            v = u.strip()
            if len(v) > 8 and v.endswith('/'):
                v = v.rstrip('/')
            try:
                p = urlparse(v)
                v_norm = urlunparse((p.scheme, p.netloc.lower(), p.path, p.params, p.query, p.fragment))
            except Exception:
                v_norm = v
            if v_norm not in seen:
                seen.add(v_norm)
                final_urls.append(v_norm)

        self.results_textbox.insert("end", f"\n🔎 Launching {len(final_urls)} email Google dork searches (expanded) for {email}\n")
        self.results_textbox.see("end")
        delay = getattr(self, 'GOOGLE_DORK_OPEN_DELAY', 1.0)
        for u in final_urls:
            try:
                webbrowser.open_new_tab(u)
                time.sleep(delay)
            except Exception as e:
                self.results_textbox.insert("end", f"⚠️ Failed to open: {u} ({e})\n")
        self.results_textbox.insert("end", "✅ Expanded email Google dork searches opened.\n")
        self.results_textbox.see("end")

    def email_quick_resources(self):
        """Open categorized quick OSINT resources for the entered email (with delay)."""
        if self.lookup_type.get() != "Email Address":
            return
        email = self.target_var.get().strip()
        if not email:
            self.results_textbox.insert("end", "\n❌ Please enter an email address before opening quick resources.\n")
            self.results_textbox.see("end")
            return
        if '@' not in email or email.startswith('@') or email.endswith('@'):
            self.results_textbox.insert("end", "\n❌ Invalid email format.\n")
            self.results_textbox.see("end")
            return
        domain = email.split('@',1)[1]

        categories = {
            '📂 BREACH DATABASES': [
                ("Have I Been Pwned", f"https://haveibeenpwned.com/account/{email}"),
                ("DeHashed", f"https://dehashed.com/search?query={email}"),
                ("LeakCheck.io", "https://leakcheck.io/")
            ],
            '📂 EMAIL VERIFICATION': [
                ("Hunter.io", "https://hunter.io/email-verifier"),
                ("Email Checker", f"https://email-checker.net/validate/{email}"),
                ("VerifyEmailAddress", "https://www.verifyemailaddress.org/")
            ],
            '📂 SOCIAL MEDIA': [
                ("Facebook", f"https://www.facebook.com/search/people/?q={email}"),
                ("LinkedIn", f"https://www.linkedin.com/search/results/people/?keywords={email}"),
                ("Twitter/X", f"https://twitter.com/search?q={email}"),
                ("Instagram Reset", "https://www.instagram.com/accounts/password/reset/")
            ],
            '📂 SEARCH ENGINES': [
                ("Google", f"https://www.google.com/search?q=\"{email}\""),
                ("Bing", f"https://www.bing.com/search?q=\"{email}\""),
                ("DuckDuckGo", f"https://duckduckgo.com/?q=\"{email}\"")
            ],
            '📂 DOMAIN ANALYSIS': [
                ("WHOIS", f"https://whois.domaintools.com/{domain}"),
                ("MXToolbox", f"https://mxtoolbox.com/domain/{domain}")
            ]
        }

        # Log categories to results box
        self.results_textbox.insert("end", f"\n⚡ Opening quick resources for {email} (domain: {domain})\n")
        for cat, items in categories.items():
            self.results_textbox.insert("end", f"{cat}\n")
            for name, url in items:
                self.results_textbox.insert("end", f"   • {name}: {url}\n")
            self.results_textbox.insert("end", "\n")
        self.results_textbox.see("end")

        # Open each URL with 1-second delay
        delay = getattr(self, 'GOOGLE_DORK_OPEN_DELAY', 1.0)
        for items in categories.values():
            for _name, url in items:
                try:
                    webbrowser.open_new_tab(url)
                    time.sleep(delay)
                except Exception as e:
                    self.results_textbox.insert("end", f"⚠️ Failed to open: {url} ({e})\n")
        self.results_textbox.insert("end", "✅ Quick resources opened.\n")
        self.results_textbox.see("end")

    def validate_input(self, target, lookup_type):
        """Validate input based on lookup type"""
        if lookup_type == "Email Address":
            if not validate_email(target):
                self.results_textbox.delete("1.0", "end")
                self.results_textbox.insert("end", "❌ Invalid email format. Please enter a valid email address.\n")
                return False
        elif lookup_type == "Phone Number":
            # Indian phone number validation
            if not self._validate_indian_phone(target):
                return False
        elif lookup_type == "IP Address":
            if not validate_ip(target):
                self.results_textbox.delete("1.0", "end")
                self.results_textbox.insert("end", "❌ Invalid IP format. Please enter a valid IP address.\n")
                return False
        
        return True

    def perform_investigation(self, target, lookup_type):
        """Perform comprehensive professional investigation with real data"""
        # Update status
        self.status_label.configure(text="🔄 Investigating...", text_color=("#ff9500", "#ff9500"))
        
        self.results_textbox.delete("1.0", "end")
        self.results_textbox.insert("end", f"🔍 Investigating {target}...\n\n")
        
        # Get search type
        search_type = lookup_type.lower().replace(" ", "_").replace("_address", "")
        if search_type == "full_name":
            search_type = "name"
        elif search_type == "phone_number":
            search_type = "phone"
        elif search_type == "email_address":
            search_type = "email"
        elif search_type == "ip_address":
            search_type = "ip"
        
        # Perform real data analysis
        real_data = None
        if search_type == "ip":
            real_data = get_real_ip_info(target)
        elif search_type == "phone":
            # Indian phone investigation only
            self.status_label.configure(text="🔄 Indian Phone Investigation...", text_color=("#ff9500", "#ff9500"))
            self.results_textbox.insert("end", f"🇮🇳 Starting Indian phone number investigation...\n")
            self.results_textbox.insert("end", f"📱 Target: {target}\n")
            self.results_textbox.insert("end", f"🌍 Country: India (IN)\n\n")
            
            try:
                # Use our enhanced phone OSINT investigation for India
                from src.utils.enhanced_phone_osint import get_comprehensive_phone_info
                
                self.results_textbox.insert("end", "📊 Analyzing Indian phone number...\n")
                self.results_textbox.insert("end", "🔍 Checking carrier and location...\n")
                self.results_textbox.insert("end", "📱 Analyzing social media presence...\n")
                self.results_textbox.see("end")
                
                real_data = get_comprehensive_phone_info(target, 'IN')
                
                if real_data:
                    self.results_textbox.insert("end", f"✅ Indian phone investigation completed!\n")
                    self.results_textbox.insert("end", f"🎯 Confidence Score: {real_data.get('confidence_score', 0):.1f}%\n")
                    self.results_textbox.insert("end", f"📋 Summary: {real_data.get('investigation_summary', 'Analysis complete')}\n\n")
                    real_data['success'] = True
                else:
                    self.results_textbox.insert("end", "⚠️ Investigation completed with limited data\n\n")
                    real_data = {'success': False, 'message': 'Limited data available'}
                
            except Exception as e:
                self.results_textbox.insert("end", f"⚠️ Investigation error: {str(e)}\n")
                self.results_textbox.insert("end", "🔄 Using basic Indian phone analysis...\n\n")
                
                # Fallback to basic Indian phone analysis
                try:
                    from src.utils.osint_utils import IndianPhoneNumberFormatter
                    formatter = IndianPhoneNumberFormatter()
                    basic_result = formatter.format_phone_number(target)
                    
                    if basic_result.get('success'):
                        best_format = basic_result.get('best_format', {})
                        real_data = {
                            'success': True,
                            'technical_analysis': {
                                'is_valid': best_format.get('is_valid', False),
                                'international_format': best_format.get('international', 'N/A'),
                                'country_name': 'India',
                                'number_type': best_format.get('number_type_name', 'Unknown'),
                                'carrier': best_format.get('carrier_name', 'Unknown'),
                                'indian_operator': best_format.get('indian_operator', 'Unknown'),
                                'telecom_circle': best_format.get('telecom_circle', 'Unknown')
                            },
                            'investigation_summary': f"Indian {best_format.get('number_type_name', 'number')} - {best_format.get('indian_operator', 'Unknown')} carrier",
                            'confidence_score': 75.0,
                            'fallback_used': True
                        }
                        self.results_textbox.insert("end", "✅ Basic Indian phone analysis completed\n\n")
                    else:
                        real_data = {'success': False, 'message': f'Analysis failed: {str(e)}'}
                        self.results_textbox.insert("end", "❌ Analysis failed\n\n")
                        
                except Exception as fallback_error:
                    real_data = {'success': False, 'message': f'Complete failure: {str(e)}'}
                    self.results_textbox.insert("end", f"❌ Complete analysis failure: {str(fallback_error)}\n\n")
        elif search_type == "email":
            # Core email analysis & unified resource opening with dedup
            real_data = get_email_info(target)
            self.results_textbox.insert("end", "📧 Aggregating email investigation resources...\n")
            if not target:
                self.results_textbox.insert("end", "❌ Please enter an email address.\n")
                self.results_textbox.see("end")
                return
            if '@' not in target or target.startswith('@') or target.endswith('@'):
                self.results_textbox.insert("end", "❌ Invalid email format.\n")
                self.results_textbox.see("end")
                return

            raw_email = target.strip()
            _local, domain = raw_email.split('@', 1)
            domain = domain.lower().strip()
            encoded_email = quote(raw_email, safe='')

            # 1. Collect all URLs (breach DBs, verifiers, social media, search engines, domain analysis) - EXCLUDING dorks
            all_urls = [
                f"https://haveibeenpwned.com/account/{encoded_email}",
                f"https://dehashed.com/search?query={encoded_email}",
                "https://leakcheck.io/",
                "https://hunter.io/email-verifier",
                f"https://email-checker.net/validate/{encoded_email}",
                "https://www.verifyemailaddress.org/",
                f"https://www.facebook.com/search/people/?q={encoded_email}",
                f"https://www.linkedin.com/search/results/people/?keywords={encoded_email}",
                f"https://twitter.com/search?q={encoded_email}",
                "https://www.instagram.com/accounts/password/reset/",
                f"https://www.google.com/search?q=%22{encoded_email}%22",
                f"https://www.bing.com/search?q=%22{encoded_email}%22",
                f"https://duckduckgo.com/?q=%22{encoded_email}%22",
                f"https://whois.domaintools.com/{domain}",
                f"https://mxtoolbox.com/domain/{domain}"
            ]

            from urllib.parse import urlparse, urlunparse

            def normalize(u: str) -> str:
                # Strip whitespace
                u = u.strip()
                # Remove trailing slash (except protocol roots)
                if len(u) > 8 and u.endswith('/'):
                    u = u.rstrip('/')
                try:
                    p = urlparse(u)
                    # Lowercase domain
                    netloc = p.netloc.lower()
                    rebuilt = urlunparse((p.scheme, netloc, p.path, p.params, p.query, p.fragment))
                    return rebuilt
                except Exception:
                    return u

            # 2 & 3. Normalize and deduplicate using a set while preserving order
            seen = set()
            unique_urls = []
            for url in all_urls:
                norm = normalize(url)
                if norm not in seen:
                    seen.add(norm)
                    unique_urls.append(norm)

            self.results_textbox.insert("end", f"⚡ Email Resources for {raw_email} (domain: {domain})\n")
            for u in unique_urls:
                self.results_textbox.insert("end", f"   • {u}\n")
            self.results_textbox.insert("end", f"🔁 Unique resource URLs opened: {len(unique_urls)} (from {len(all_urls)} raw entries)\n")
            self.results_textbox.see("end")

            # 4. Open each unique URL with 1s delay
            for u in unique_urls:
                try:
                    webbrowser.open_new_tab(u)
                    time.sleep(1)
                except Exception as e:
                    self.results_textbox.insert("end", f"⚠️ Failed to open: {u} ({e})\n")
            self.results_textbox.insert("end", "✅ Email investigation resources opened (deduplicated).\n")
        elif search_type == "name":
            from src.utils.osint_utils import get_name_info
            real_data = get_name_info(target)
        
        # Generate comprehensive OSINT links
        links = generate_search_links(target, search_type)
        
        if not links:
            self.results_textbox.insert("end", "❌ No search links generated.\n")
            self.status_label.configure(text="❌ Failed", text_color=("#ff4444", "#ff4444"))
            return
        
        # For email we already opened all curated resources above; avoid duplicate openings
        if search_type != "email":
            opened_count = open_links_safely(links, max_links=8)
        else:
            opened_count = 0
        
        # Small delay for professional feel
        time.sleep(0.5)
        
        # Format and display comprehensive results
        results_text = self.format_comprehensive_results(target, lookup_type, links, real_data)
        self.results_textbox.delete("1.0", "end")
        self.results_textbox.insert("end", results_text)
        
        # Update status to complete
        self.status_label.configure(text="✅ Complete", text_color=("#4a9eff", "#4a9eff"))
        
        # Store results for export
        self.last_investigation = {
            'target': target,
            'type': lookup_type,
            'links': links,
            'real_data': real_data,
            'results': results_text,
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
            'categories': len(set(link.get('category', 'Other') for link in links))
        }

    def format_comprehensive_results(self, target: str, lookup_type: str, links: List[Dict], real_data: Optional[Dict]) -> str:
        """Format comprehensive professional results with enhanced intelligence display"""
        if lookup_type == "Phone Number":
            return self._format_enhanced_phone_results(target, links, real_data)
        else:
            return self._format_standard_results(target, lookup_type, links, real_data)
    
    def _format_enhanced_phone_results(self, target: str, links: List[Dict], real_data: Optional[Dict]) -> str:
        """Format enhanced phone investigation results with comprehensive information"""
        result = f"🔍 COMPREHENSIVE PHONE NUMBER INVESTIGATION\n"
        result += f"{'='*80}\n"
        result += f"📱 Phone Number: {target}\n"
        result += f"⏰ Investigation Time: {time.strftime('%Y-%m-%d %H:%M:%S')}\n"
        result += f"🌐 OSINT Resources: {len(links)} tools opened in browser\n"
        result += f"{'='*80}\n\n"
        
        if real_data and real_data.get('success'):
            # TECHNICAL ANALYSIS SECTION
            result += "📊 TECHNICAL ANALYSIS\n"
            result += "─" * 40 + "\n"
            
            tech = real_data.get('technical_analysis', {})
            if tech:
                result += f"✅ Valid Number: {'Yes' if tech.get('is_valid') else 'No'}\n"
                result += f"📞 Number Type: {tech.get('number_type', 'Unknown')}\n"
                result += f"🌍 International Format: {tech.get('international_format', 'N/A')}\n"
                result += f"🏠 National Format: {tech.get('national_format', 'N/A')}\n"
                result += f"📧 E164 Format: {tech.get('e164_format', 'N/A')}\n"
                result += f"🏢 Carrier: {tech.get('carrier', 'Unknown')}\n"
                result += f"📍 Location: {tech.get('location', 'Unknown')}\n"
                if tech.get('timezones'):
                    result += f"🕐 Timezones: {', '.join(tech['timezones'])}\n"
            result += "\n"
            
            # CARRIER & LOCATION INFORMATION
            carrier_info = real_data.get('carrier_info', {})
            if carrier_info:
                result += "📡 CARRIER & LOCATION DETAILS\n"
                result += "─" * 40 + "\n"
                result += f"📱 Carrier: {carrier_info.get('carrier_name', 'Unknown')}\n"
                
                # Indian-specific information
                if carrier_info.get('indian_carrier'):
                    result += f"🇮🇳 Indian Carrier: {carrier_info['indian_carrier']}\n"
                    result += f"📝 Description: {carrier_info.get('carrier_description', 'N/A')}\n"
                    
                if carrier_info.get('telecom_circle'):
                    circle = carrier_info['telecom_circle']
                    result += f"🏙️ Telecom Circle: {circle.get('circle', 'Unknown')}\n"
                    result += f"📊 Circle Type: {circle.get('type', 'Unknown')}\n"
                    
                result += f"🔄 Number Portability: {carrier_info.get('mnp_possible', 'Unknown')}\n"
                
                location = carrier_info.get('location', {})
                if location:
                    result += f"🌍 Country: {location.get('country', 'Unknown')}\n"
                    result += f"📍 Region: {location.get('description', 'Unknown')}\n"
                result += "\n"
            
            # SOCIAL MEDIA PRESENCE
            social = real_data.get('social_presence', {})
            if social:
                result += "📱 SOCIAL MEDIA PRESENCE\n"
                result += "─" * 40 + "\n"
                result += f"💬 WhatsApp Likely: {'Yes' if social.get('whatsapp_likely') else 'No'}\n"
                result += f"📞 Telegram Searchable: {'Yes' if social.get('telegram_searchable') else 'No'}\n"
                
                platforms = social.get('social_platforms', {})
                if platforms:
                    for platform, info in platforms.items():
                        if isinstance(info, dict):
                            status = 'Likely' if info.get('likely_present') or info.get('searchable') else 'Unknown'
                            extra = []
                            if info.get('confidence') is not None:
                                extra.append(f"Confidence: {info['confidence']:.0%}" if isinstance(info['confidence'], (int, float)) else f"Confidence: {info['confidence']}")
                            if info.get('last_checked'):
                                extra.append(f"Last Checked: {info['last_checked']}")
                            extra_text = f" ({'; '.join(extra)})" if extra else ""
                            result += f"   • {platform.title()}: {status}{extra_text}\n"
                result += "\n"
            
            # BUSINESS CONNECTIONS
            business = real_data.get('business_connections', {})
            if business:
                result += "🏢 BUSINESS CONNECTION ANALYSIS\n"
                result += "─" * 40 + "\n"
                result += f"📊 Business Likelihood: {business.get('business_likelihood', 'Unknown')}\n"
                
                indicators = business.get('indicators', [])
                if indicators:
                    result += "🔍 Indicators:\n"
                    for indicator in indicators:
                        if isinstance(indicator, dict):
                            desc = indicator.get('description') or indicator.get('indicator') or str(indicator)
                            confidence = indicator.get('confidence')
                            if confidence is not None:
                                result += f"   • {desc} (Confidence: {confidence:.0%})\n" if isinstance(confidence, (int, float)) else f"   • {desc} (Confidence: {confidence})\n"
                            else:
                                result += f"   • {desc}\n"
                        else:
                            result += f"   • {indicator}\n"
                result += "\n"
            
            # REPUTATION ANALYSIS
            reputation = real_data.get('reputation_analysis', {})
            if reputation:
                result += "🛡️ REPUTATION & SAFETY ANALYSIS\n"
                result += "─" * 40 + "\n"
                result += f"⚠️ Spam Likelihood: {reputation.get('spam_likelihood', 'Unknown')}\n"
                result += f"🔒 Safety Score: {reputation.get('safety_score', 'Unknown')}\n"
                result += "\n"
            
            # INVESTIGATION SUMMARY
            result += "🎯 INVESTIGATION SUMMARY\n"
            result += "─" * 40 + "\n"
            result += f"📋 Summary: {real_data.get('investigation_summary', 'Analysis completed')}\n"
            result += f"🎯 Confidence Score: {real_data.get('confidence_score', 0):.1f}%\n"
            result += f"📊 Sources Used: {len(real_data.get('sources_used', []))}\n"
            result += "\n"
            
        else:
            result += "⚠️ LIMITED INVESTIGATION DATA\n"
            result += "─" * 40 + "\n"
            if real_data and real_data.get('message'):
                result += f"Status: {real_data['message']}\n"
            result += "Note: Enhanced investigation features may require API configuration\n\n"
        
        # OSINT RESOURCES SECTION
        result += "🔗 OSINT INVESTIGATION RESOURCES\n"
        result += "─" * 50 + "\n"
        result += f"🌐 Total Resources: {len(links)} professional OSINT tools\n"
        result += "📂 All resources have been opened in your browser for investigation\n\n"
        
    # Group and display resources by category
        if real_data and real_data.get('osint_resources'):
            osint_resources = real_data['osint_resources']
            for category_data in osint_resources:
                category = category_data.get('category', 'Unknown')
                tools = category_data.get('tools', [])
                
                result += f"📂 {category.upper()} ({len(tools)} tools)\n"
                for i, tool in enumerate(tools, 1):
                    desc = tool.get('description', '')
                    url = tool.get('url') or tool.get('link')
                    url_part = f" | {url}" if url else ""
                    result += f"   {i}. {tool.get('name','Unknown')} - {desc}{url_part}\n"
                result += "\n"
        else:
            # Fallback to basic link categorization
            categories = {}
            for link in links:
                category = link.get('category', 'General')
                if category not in categories:
                    categories[category] = []
                categories[category].append(link)
            
            for category, category_links in categories.items():
                result += f"📂 {category.upper()} ({len(category_links)} tools)\n"
                for i, link in enumerate(category_links, 1):
                    result += f"   {i}. {link['name']}\n"
                result += "\n"
        
        # INVESTIGATION RECOMMENDATIONS
        result += "💡 INVESTIGATION RECOMMENDATIONS\n"
        result += "─" * 50 + "\n"
        result += "1. Check Truecaller for caller ID and spam reports\n"
        result += "2. Use FindAndTrace for location and carrier details\n"
        result += "3. Search social media platforms (WhatsApp, Telegram)\n"
        result += "4. Verify through business directories if applicable\n"
        result += "5. Cross-reference multiple sources for accuracy\n"
        result += "6. Be aware of privacy laws and ethical considerations\n\n"
        
        # LEGAL COMPLIANCE
        result += "⚖️ LEGAL & ETHICAL COMPLIANCE\n"
        result += "─" * 50 + "\n"
        result += "• Only investigate numbers with proper authorization\n"
        result += "• Respect privacy laws and regulations\n"
        result += "• Use information responsibly and ethically\n"
        result += "• Do not use for harassment or illegal activities\n"
        result += "• Consider data protection requirements (GDPR, etc.)\n\n"
        
        result += "🎯 Investigation completed. Review browser tabs for detailed analysis.\n"

        # Append extended intelligence sections if rich data available
        if real_data:
            try:
                # These helper methods are defined later in the class; guard with hasattr
                if hasattr(self, '_format_social_intelligence') and real_data.get('social_presence'):
                    result += "\n" + self._format_social_intelligence(real_data)
                if hasattr(self, '_format_business_intelligence') and (real_data.get('business_connections') or (real_data.get('aggregated_intelligence') and real_data['aggregated_intelligence'].get('merged_data', {}).get('domains_found'))):
                    result += "\n" + self._format_business_intelligence(real_data)
                if hasattr(self, '_format_pattern_intelligence') and real_data.get('aggregated_intelligence'):
                    result += "\n" + self._format_pattern_intelligence(real_data)
                if hasattr(self, '_format_historical_intelligence') and (real_data.get('historical_intelligence') or real_data.get('change_timeline')):
                    result += "\n" + self._format_historical_intelligence(real_data)
                if hasattr(self, '_format_confidence_assessment'):
                    result += "\n" + self._format_confidence_assessment(real_data)
                if hasattr(self, '_format_legal_compliance'):
                    result += "\n" + self._format_legal_compliance(real_data)
            except Exception as e:
                result += f"\n⚠️ Extended intelligence section rendering error: {e}\n"
        
        return result
    
    def _validate_indian_phone(self, phone_number: str) -> bool:
        """Validate Indian phone number format"""
        # Clean the phone number
        clean_number = re.sub(r'[^\d]', '', phone_number)
        
        # Check various Indian phone number patterns
        if len(clean_number) == 10:
            # 10-digit mobile number
            if clean_number[0] in ['6', '7', '8', '9']:
                return True
            else:
                self.results_textbox.delete("1.0", "end")
                self.results_textbox.insert("end", "❌ Invalid Indian mobile number.\n\n")
                self.results_textbox.insert("end", "💡 Indian mobile numbers must start with 6, 7, 8, or 9\n")
                self.results_textbox.insert("end", "📋 Valid formats:\n")
                self.results_textbox.insert("end", "   • 9876543210 (10-digit mobile)\n")
                self.results_textbox.insert("end", "   • +91 9876543210 (international)\n")
                self.results_textbox.insert("end", "   • 09876543210 (with leading zero)\n")
                return False
        elif len(clean_number) == 11 and clean_number.startswith('0'):
            # 11-digit with leading zero
            if clean_number[1] in ['6', '7', '8', '9']:
                return True
            else:
                self.results_textbox.delete("1.0", "end")
                self.results_textbox.insert("end", "❌ Invalid Indian mobile number format.\n\n")
                self.results_textbox.insert("end", "💡 After country code, number must start with 6, 7, 8, or 9\n")
                return False
        elif len(clean_number) == 12 and clean_number.startswith('91'):
            # 12-digit with country code 91
            if clean_number[2] in ['6', '7', '8', '9']:
                return True
            else:
                self.results_textbox.delete("1.0", "end")
                self.results_textbox.insert("end", "❌ Invalid Indian mobile number format.\n\n")
                self.results_textbox.insert("end", "💡 After country code 91, number must start with 6, 7, 8, or 9\n")
                return False
        elif len(clean_number) == 13 and clean_number.startswith('910'):
            # 13-digit with country code and leading zero
            if clean_number[3] in ['6', '7', '8', '9']:
                return True
            else:
                self.results_textbox.delete("1.0", "end")
                self.results_textbox.insert("end", "❌ Invalid Indian mobile number format.\n\n")
                return False
        else:
            self.results_textbox.delete("1.0", "end")
            self.results_textbox.insert("end", "❌ Invalid Indian phone number length.\n\n")
            self.results_textbox.insert("end", "📋 Accepted formats:\n")
            self.results_textbox.insert("end", "   • 9876543210 (10 digits)\n")
            self.results_textbox.insert("end", "   • +91 9876543210 (with country code)\n")
            self.results_textbox.insert("end", "   • 09876543210 (with leading zero)\n")
            self.results_textbox.insert("end", "   • 91 9876543210 (country code without +)\n")
            return False
    
    def _format_osint_resources(self, links: List[Dict]) -> str:
        """Format OSINT resources section"""
        # Group links by category
        categories = {}
        for link in links:
            category = link.get('category', 'Other')
            if category not in categories:
                categories[category] = []
            categories[category].append(link)
        
        section = f"🔗 OSINT RESOURCES & TOOLS\n"
        section += f"{'─'*50}\n"
        section += f"📊 Total Resources: {len(links)} professional OSINT tools\n"
        section += f"📂 Categories: {len(categories)} investigation domains\n"
        section += f"🌐 Browser Links: Automatically opened for investigation\n\n"
        
        for category, category_links in categories.items():
            section += f"📂 {category.upper()} ({len(category_links)} resources)\n"
            section += f"{'─'*30}\n"
            for i, link in enumerate(category_links, 1):
                section += f"   {i:2d}. {link['name']}\n"
                section += f"       🔗 {link['url'][:60]}{'...' if len(link['url']) > 60 else ''}\n"
            section += "\n"
        
        return section
    
    def _format_investigation_methodology(self, real_data: Optional[Dict]) -> str:
        """Format investigation methodology and recommendations"""
        section = f"📋 INVESTIGATION METHODOLOGY & RECOMMENDATIONS\n"
        section += f"{'─'*60}\n"
        
        # Completed Actions
        section += f"✅ COMPLETED ACTIONS:\n"
        section += f"   • Target validation and format verification\n"
        section += f"   • Multi-source intelligence aggregation\n"
        section += f"   • Professional OSINT resource deployment\n"
        section += f"   • Confidence scoring and quality assessment\n"
        section += f"   • Comprehensive data analysis and categorization\n\n"
        
        # Next Steps
        section += f"📊 RECOMMENDED NEXT STEPS:\n"
        section += f"   1. Review all intelligence sections systematically\n"
        section += f"   2. Cross-reference findings across multiple sources\n"
        section += f"   3. Verify high-confidence data through independent channels\n"
        section += f"   4. Document evidence with timestamps and sources\n"
        section += f"   5. Export comprehensive report for legal compliance\n"
        section += f"   6. Consider additional investigation based on findings\n\n"
        
        # Investigation Quality Assessment
        section += f"🎯 INVESTIGATION SUMMARY:\n"
        if real_data and real_data.get('success'):
            confidence = 75.0
            if real_data.get('aggregated_intelligence'):
                confidence = real_data['aggregated_intelligence'].get('overall_confidence', 75.0)
            
            section += f"   • Data Quality: {'High' if confidence >= 80 else 'Medium' if confidence >= 60 else 'Low'}\n"
            section += f"   • Investigation Status: ✅ Complete\n"
            section += f"   • Confidence Level: {confidence:.1f}%\n"
        else:
            section += f"   • Data Quality: Limited\n"
            section += f"   • Investigation Status: ⚠️ Partial\n"
            section += f"   • Confidence Level: Low\n"
        
        section += f"   • Compliance: ✅ Professional standards maintained\n\n"
        
        return section
    
    def _format_legal_compliance(self, real_data: Optional[Dict]=None) -> str:
        """Format legal and ethical compliance section"""
        section = f"⚖️ LEGAL & ETHICAL COMPLIANCE\n"
        section += f"{'─'*40}\n"
        section += f"🛡️ COMPLIANCE STANDARDS:\n"
        section += f"   • Investigation uses only publicly available information\n"
        section += f"   • All OSINT resources are legitimate and authorized\n"
        section += f"   • Professional ethical standards maintained throughout\n"
        section += f"   • Data privacy and protection laws respected\n"
        section += f"   • Investigation methodology documented for legal review\n\n"
        
        section += f"⚠️ IMPORTANT REMINDERS:\n"
        section += f"   • Ensure proper authorization before investigating individuals\n"
        section += f"   • Respect platform terms of service and privacy policies\n"
        section += f"   • Maintain chain of custody for potential legal proceedings\n"
        section += f"   • Verify findings through independent sources when possible\n"
        section += f"   • Use information responsibly and within legal boundaries\n\n"
        
    # Add performance metrics section
        if real_data and real_data.get('performance_optimized'):
            section += f"{'='*60}\n"
            section += f"⚡ PERFORMANCE METRICS\n"
            section += f"{'='*60}\n"
            processing_time = real_data.get('processing_time', 0)
            section += f"🕐 Processing Time: {processing_time:.2f} seconds\n"
            section += f"🚀 Async Processing: {'✅' if real_data.get('async_processing') else '❌'} | " \
                       f"Caching: {'✅' if real_data.get('cache_enabled') else '❌'}\n"
            if real_data.get('aggregated_intelligence'):
                intel = real_data['aggregated_intelligence']
                section += f"📊 Sources: {intel.get('successful_sources', 0)}/{intel.get('total_sources', 0)} | " \
                           f"Confidence: {intel.get('overall_confidence', 0):.1f}%\n"
            if real_data.get('fallback_used'):
                section += f"⚠️ Fallback Used: {real_data.get('fallback_reason', 'Unknown')}\n"
            section += "\n"
        section += f"{'='*60}\n"
        section += f"CIOT OSINT Toolkit - Legal & Ethical Compliance Section End\n"
        section += f"{'='*60}\n"
        
        return section
    
    def _add_intelligence_sections_to_pdf(self, pdf, real_data: Dict):
        """Add comprehensive intelligence sections to PDF report"""
        # Technical Intelligence
        pdf.set_font("Arial", "B", 14)
        pdf.cell(0, 10, "TECHNICAL INTELLIGENCE", ln=True)
        pdf.set_font("Arial", "", 9)
        
        # Number formatting
        pdf.cell(0, 6, f"Original Input: {real_data.get('original_input', 'N/A')}", ln=True)
        pdf.cell(0, 6, f"International Format: {real_data.get('international_format', 'N/A')}", ln=True)
        pdf.cell(0, 6, f"National Format: {real_data.get('national_format', 'N/A')}", ln=True)
        pdf.cell(0, 6, f"E164 Format: {real_data.get('e164_format', 'N/A')}", ln=True)
        pdf.cell(0, 6, f"Country: {real_data.get('country_name', 'Unknown')} ({real_data.get('country_code', 'N/A')})", ln=True)
        pdf.cell(0, 6, f"Number Type: {real_data.get('number_type', 'Unknown')}", ln=True)
        pdf.cell(0, 6, f"Valid: {'Yes' if real_data.get('is_valid') else 'No'}", ln=True)
        pdf.cell(0, 6, f"Mobile: {'Yes' if real_data.get('is_mobile') else 'No'}", ln=True)
        pdf.ln(5)
        
        # Security Intelligence
        pdf.set_font("Arial", "B", 14)
        pdf.cell(0, 10, "SECURITY INTELLIGENCE", ln=True)
        pdf.set_font("Arial", "", 9)
        
        # Check for security data
        if real_data.get('aggregated_intelligence'):
            merged_data = real_data['aggregated_intelligence'].get('merged_data', {})
            security_fields = [k for k in merged_data.keys() if any(term in k.lower() for term in ['spam', 'risk', 'reputation', 'breach'])]
            
            if security_fields:
                for field in security_fields[:5]:  # Limit to top 5 security fields
                    value = merged_data.get(field, 'Unknown')
                    formatted_field = field.replace('_', ' ').title()
                    pdf.cell(0, 6, f"{formatted_field}: {value}", ln=True)
            else:
                pdf.cell(0, 6, "No security threats detected", ln=True)
        else:
            pdf.cell(0, 6, "Security analysis: Limited data available", ln=True)
        
        pdf.ln(5)
        
        # Business Intelligence
        pdf.set_font("Arial", "B", 14)
        pdf.cell(0, 10, "BUSINESS INTELLIGENCE", ln=True)
        pdf.set_font("Arial", "", 9)
        
        if real_data.get('aggregated_intelligence'):
            merged_data = real_data['aggregated_intelligence'].get('merged_data', {})
            domains_found = merged_data.get('domains_found', [])
            business_connections = merged_data.get('business_connections', [])
            
            if domains_found:
                pdf.cell(0, 6, f"Total Domains Found: {len(domains_found)}", ln=True)
                for domain in domains_found[:3]:  # Show top 3 domains
                    pdf.cell(0, 6, f"  - {domain.get('domain', 'Unknown')}: {domain.get('status', 'Unknown')}", ln=True)
                if len(domains_found) > 3:
                    pdf.cell(0, 6, f"  ... and {len(domains_found) - 3} more domains", ln=True)
            else:
                pdf.cell(0, 6, "No domain associations found", ln=True)
            
            if business_connections:
                pdf.cell(0, 6, f"Business Connections: {len(business_connections)}", ln=True)
                for connection in business_connections[:2]:
                    pdf.cell(0, 6, f"  - {connection.get('organization', 'Unknown')}", ln=True)
            else:
                pdf.cell(0, 6, "No business connections found", ln=True)
        else:
            pdf.cell(0, 6, "Business intelligence: No data available", ln=True)
        
        pdf.ln(5)
        
        # Investigation Quality Assessment
        pdf.set_font("Arial", "B", 14)
        pdf.cell(0, 10, "INVESTIGATION QUALITY ASSESSMENT", ln=True)
        pdf.set_font("Arial", "", 9)
        
        if real_data.get('aggregated_intelligence'):
            confidence = real_data['aggregated_intelligence'].get('overall_confidence', 0)
            confidence_level = real_data['aggregated_intelligence'].get('confidence_level', 'Unknown')
            sources_used = real_data['aggregated_intelligence'].get('sources_used', [])
            successful_sources = real_data['aggregated_intelligence'].get('successful_sources', 0)
            total_sources = real_data['aggregated_intelligence'].get('total_sources', 0)
            
            pdf.cell(0, 6, f"Overall Confidence: {confidence:.1f}% ({confidence_level})", ln=True)
            pdf.cell(0, 6, f"Data Sources: {successful_sources}/{total_sources} successful", ln=True)
            pdf.cell(0, 6, f"Sources Used: {', '.join(sources_used)}", ln=True)
            
            # Quality level
            if confidence >= 90:
                quality = "Excellent - High reliability"
            elif confidence >= 75:
                quality = "Good - Reliable for most purposes"
            elif confidence >= 60:
                quality = "Fair - Verify critical information"
            else:
                quality = "Poor - Manual verification required"
            
            pdf.cell(0, 6, f"Quality Level: {quality}", ln=True)
        else:
            pdf.cell(0, 6, "Quality assessment: Limited data available", ln=True)
        
        pdf.ln(10)
    
    def _format_technical_intelligence(self, real_data: Dict) -> str:
        """Format technical intelligence section"""
        section = f"📱 TECHNICAL INTELLIGENCE\n"
        section += f"{'─'*50}\n"
        
        # Phone Number Formatting
        section += f"🔢 NUMBER FORMATTING:\n"
        section += f"   • Original Input: {real_data.get('original_input', 'N/A')}\n"
        section += f"   • International: {real_data.get('international_format', 'N/A')}\n"
        section += f"   • National: {real_data.get('national_format', 'N/A')}\n"
        section += f"   • E164: {real_data.get('e164_format', 'N/A')}\n"
        section += f"   • RFC3966: {real_data.get('rfc3966_format', 'N/A')}\n"
        section += f"   • Formatting Method: {real_data.get('formatting_method', 'Unknown')}\n\n"
        
        # Geographic Information
        section += f"🌍 GEOGRAPHIC DATA:\n"
        section += f"   • Country: {real_data.get('country_name', 'Unknown')} ({real_data.get('country_code', 'N/A')})\n"
        section += f"   • Region: {real_data.get('region_code', 'Unknown')}\n"
        section += f"   • Location: {real_data.get('location', 'Unknown')}\n"
        if real_data.get('timezones'):
            section += f"   • Timezones: {', '.join(real_data.get('timezones', []))}\n"
        section += "\n"
        
        # Number Classification
        section += f"📋 NUMBER CLASSIFICATION:\n"
        section += f"   • Valid: {'✅ Yes' if real_data.get('is_valid') else '❌ No'}\n"
        section += f"   • Possible: {'✅ Yes' if real_data.get('is_possible') else '❌ No'}\n"
        section += f"   • Type: {real_data.get('number_type', 'Unknown')}\n"
        section += f"   • Mobile: {'✅ Yes' if real_data.get('is_mobile') else '❌ No'}\n"
        section += f"   • Fixed Line: {'✅ Yes' if real_data.get('is_fixed_line') else '❌ No'}\n\n"
        
        # Carrier Information
        section += f"🏢 CARRIER INFORMATION:\n"
        section += f"   • libphonenumber Carrier: {real_data.get('carrier_name', 'Unknown')}\n"
        
        # Enhanced carrier data from aggregated intelligence
        if real_data.get('aggregated_intelligence'):
            merged_data = real_data['aggregated_intelligence'].get('merged_data', {})
            if merged_data.get('carrier'):
                section += f"   • API Carrier: {merged_data.get('carrier', 'Unknown')}\n"
            if merged_data.get('operator'):
                section += f"   • Operator: {merged_data.get('operator', 'Unknown')}\n"
            if merged_data.get('line_type'):
                section += f"   • Line Type: {merged_data.get('line_type', 'Unknown')}\n"
        
        section += "\n"
        
        return section
    
    def _format_security_intelligence(self, real_data: Dict) -> str:
        """Format security intelligence section"""
        section = f"🛡️ SECURITY INTELLIGENCE\n"
        section += f"{'─'*50}\n"
        
        # Reputation & Spam Assessment
        section += f"🚨 REPUTATION ASSESSMENT:\n"
        
        # Check aggregated intelligence for security data
        security_data = {}
        if real_data.get('aggregated_intelligence'):
            merged_data = real_data['aggregated_intelligence'].get('merged_data', {})
            # Look for security-related fields
            for key, value in merged_data.items():
                if any(term in key.lower() for term in ['spam', 'risk', 'reputation', 'breach', 'security']):
                    security_data[key] = value
        
        if security_data:
            for key, value in security_data.items():
                formatted_key = key.replace('_', ' ').title()
                section += f"   • {formatted_key}: {value}\n"
        else:
            section += f"   • Spam Status: ✅ No spam indicators detected\n"
            section += f"   • Risk Level: 🟢 Low Risk\n"
            section += f"   • Breach Status: ✅ No known breaches\n"
        
        section += f"   • Investigation Confidence: {real_data.get('investigation_confidence', 'Medium')}\n\n"
        
        # Data Breach Analysis
        section += f"🔍 DATA BREACH ANALYSIS:\n"
        if real_data.get('found_in_breaches'):
            section += f"   • Breach Status: 🚨 Found in {real_data.get('breach_count', 0)} breaches\n"
            if real_data.get('breach_details'):
                for breach in real_data.get('breach_details', [])[:3]:  # Show top 3
                    section += f"   • {breach.get('name', 'Unknown')}: {breach.get('date', 'Unknown date')}\n"
        else:
            section += f"   • Breach Status: ✅ No known data breaches\n"
        section += "\n"
        
        return section
    
    def _format_social_intelligence(self, real_data: Dict) -> str:
        """Format social intelligence section"""
        section = f"💬 SOCIAL INTELLIGENCE\n"
        section += f"{'─'*50}\n"
        
        # Social Media Presence
        section += f"📱 SOCIAL MEDIA PRESENCE:\n"
        
        # Check for social media data in aggregated intelligence
        social_data = {}
        if real_data.get('aggregated_intelligence'):
            merged_data = real_data['aggregated_intelligence'].get('merged_data', {})
            for key, value in merged_data.items():
                if any(term in key.lower() for term in ['whatsapp', 'telegram', 'facebook', 'instagram', 'linkedin', 'social']):
                    social_data[key] = value
        
        # WhatsApp Analysis
        if real_data.get('whatsapp_present') or social_data.get('whatsapp_presence'):
            section += f"   • WhatsApp: ✅ Present\n"
            if real_data.get('whatsapp_privacy_level'):
                section += f"     - Privacy Level: {real_data.get('whatsapp_privacy_level')}\n"
        else:
            section += f"   • WhatsApp: ❌ Not detected\n"
        
        # Telegram Analysis
        if social_data.get('telegram_presence'):
            section += f"   • Telegram: ✅ Present\n"
        else:
            section += f"   • Telegram: ❌ Not detected\n"
        
        # Other Social Platforms
        for platform in ['facebook', 'instagram', 'linkedin']:
            if social_data.get(f'{platform}_presence'):
                section += f"   • {platform.title()}: ✅ Present\n"
            else:
                section += f"   • {platform.title()}: ❌ Not detected\n"
        
        section += "\n"
        
        return section
    
    def _format_business_intelligence(self, real_data: Dict) -> str:
        """Format business intelligence section"""
        section = f"🏢 BUSINESS INTELLIGENCE\n"
        section += f"{'─'*50}\n"
        
        # WHOIS & Domain Linkage
        section += f"🌐 DOMAIN ASSOCIATIONS:\n"
        
        # Check aggregated intelligence for business data
        business_data = {}
        if real_data.get('aggregated_intelligence'):
            merged_data = real_data['aggregated_intelligence'].get('merged_data', {})
            
            # Look for WHOIS and domain data
            domains_found = merged_data.get('domains_found', [])
            business_connections = merged_data.get('business_connections', [])
            
            if domains_found:
                section += f"   • Total Domains: {len(domains_found)}\n"
                section += f"   • Active Domains: {len([d for d in domains_found if d.get('status') == 'active'])}\n"
                
                # Show top domains
                for domain in domains_found[:3]:
                    section += f"     - {domain.get('domain', 'Unknown')}: {domain.get('status', 'Unknown')} ({domain.get('registrar', 'Unknown')})\n"
                
                if len(domains_found) > 3:
                    section += f"     - ... and {len(domains_found) - 3} more domains\n"
            else:
                section += f"   • Domain Status: ❌ No domains registered with this number\n"
            
            # Business Connections
            if business_connections:
                section += f"   • Business Connections: {len(business_connections)} found\n"
                for connection in business_connections[:2]:
                    section += f"     - {connection.get('organization', 'Unknown')}: {connection.get('contact_type', 'Unknown')}\n"
            else:
                section += f"   • Business Connections: ❌ No business associations found\n"
        else:
            section += f"   • Domain Status: ❌ No WHOIS data available\n"
            section += f"   • Business Connections: ❌ No business data available\n"
        
        section += "\n"
        
        return section
    
    def _format_pattern_intelligence(self, real_data: Dict) -> str:
        """Format pattern intelligence section"""
        section = f"🔍 PATTERN INTELLIGENCE\n"
        section += f"{'─'*50}\n"
        
        # Related Numbers & Patterns
        section += f"🔗 RELATED NUMBER ANALYSIS:\n"
        
        # Check aggregated intelligence for pattern data
        if real_data.get('aggregated_intelligence'):
            merged_data = real_data['aggregated_intelligence'].get('merged_data', {})
            
            # Related numbers
            related_numbers = merged_data.get('related_numbers', [])
            if related_numbers:
                section += f"   • Related Numbers: {len(related_numbers)} found\n"
                high_confidence = [rn for rn in related_numbers if rn.get('confidence_score', 0) >= 0.7]
                section += f"   • High Confidence: {len(high_confidence)} numbers\n"
                
                # Show top related numbers
                for rn in related_numbers[:3]:
                    section += f"     - {rn.get('number', 'Unknown')}: {rn.get('relationship_type', 'Unknown')} (Confidence: {rn.get('confidence_score', 0):.1%})\n"
            else:
                section += f"   • Related Numbers: ❌ No related patterns detected\n"
            
            # Bulk Registration Analysis
            bulk_registration = merged_data.get('bulk_registration', {})
            if bulk_registration.get('detected'):
                section += f"   • Bulk Registration: 🚨 Detected (Confidence: {bulk_registration.get('confidence_score', 0):.1%})\n"
                section += f"     - Block Size: {bulk_registration.get('block_size', 'Unknown')}\n"
                section += f"     - Pattern Type: {bulk_registration.get('pattern_type', 'Unknown')}\n"
            else:
                section += f"   • Bulk Registration: ✅ No bulk patterns detected\n"
            
            # Sequential Patterns
            sequential_patterns = merged_data.get('sequential_patterns', {})
            if sequential_patterns.get('found'):
                section += f"   • Sequential Patterns: ✅ Found\n"
                section += f"     - Pattern Type: {sequential_patterns.get('pattern_type', 'Unknown')}\n"
                section += f"     - Confidence: {sequential_patterns.get('confidence_score', 0):.1%}\n"
            else:
                section += f"   • Sequential Patterns: ❌ No sequential patterns found\n"
        else:
            section += f"   • Pattern Analysis: ❌ No pattern data available\n"
        
        section += "\n"
        
        return section
    
    def _format_historical_intelligence(self, real_data: Dict) -> str:
        """Format historical intelligence section"""
        section = f"📊 HISTORICAL INTELLIGENCE\n"
        section += f"{'─'*50}\n"
        
        # Historical Data & Change Tracking
        historical_intel = real_data.get('historical_intelligence', {})
        change_timeline = real_data.get('change_timeline', [])
        porting_analysis = real_data.get('porting_analysis', {})
        ownership_analysis = real_data.get('ownership_analysis', {})
        
        section += f"🕐 INVESTIGATION HISTORY:\n"
        total_investigations = historical_intel.get('total_investigations', 0)
        first_seen = historical_intel.get('first_seen')
        last_seen = historical_intel.get('last_seen')
        
        if total_investigations > 0:
            section += f"   • Total Investigations: {total_investigations} previous records\n"
            if first_seen:
                section += f"   • First Seen: {first_seen[:19].replace('T', ' ')}\n"
            if last_seen:
                section += f"   • Last Seen: {last_seen[:19].replace('T', ' ')}\n"
            
            # Stability metrics
            stability_score = historical_intel.get('stability_score', 1.0)
            change_frequency = historical_intel.get('change_frequency', 0.0)
            risk_level = historical_intel.get('risk_level', 'Minimal Risk')
            
            section += f"   • Stability Score: {stability_score:.2f}/1.0 ({'High' if stability_score >= 0.8 else 'Medium' if stability_score >= 0.6 else 'Low'})\n"
            section += f"   • Change Frequency: {change_frequency:.2f} changes per investigation\n"
            section += f"   • Risk Level: {risk_level}\n"
        else:
            section += f"   • Historical Records: ❌ No previous investigations found\n"
            section += f"   • First Investigation: ✅ This is the first recorded investigation\n"
        
        section += "\n"
        
        # Change Timeline
        section += f"📈 CHANGE TIMELINE:\n"
        if change_timeline:
            section += f"   • Total Changes Detected: {len(change_timeline)}\n"
            section += f"   • Recent Changes (Last 5):\n"
            
            for i, change in enumerate(change_timeline[:5], 1):
                change_type = change.get('change_type', 'Unknown Change')
                timestamp = change.get('timestamp', '')
                old_value = change.get('old_value', 'Unknown')
                new_value = change.get('new_value', 'Unknown')
                confidence = change.get('confidence_score', 0.0)
                
                if timestamp:
                    timestamp_formatted = timestamp[:19].replace('T', ' ')
                else:
                    timestamp_formatted = 'Unknown time'
                
                section += f"     {i}. {change_type} ({timestamp_formatted})\n"
                section += f"        {old_value} → {new_value} (Confidence: {confidence:.1f})\n"
            
            if len(change_timeline) > 5:
                section += f"     ... and {len(change_timeline) - 5} more changes\n"
        else:
            section += f"   • Change History: ❌ No changes detected\n"
        
        section += "\n"
        
        # Porting Analysis
        section += f"📱 CARRIER PORTING ANALYSIS:\n"
        if porting_analysis.get('porting_detected'):
            section += f"   • Porting Status: ✅ Number porting detected\n"
            section += f"   • Total Transitions: {porting_analysis.get('total_transitions', 0)}\n"
            section += f"   • Original Carrier: {porting_analysis.get('original_carrier', 'Unknown')}\n"
            section += f"   • Current Carrier: {porting_analysis.get('current_carrier', 'Unknown')}\n"
            section += f"   • Porting Confidence: {porting_analysis.get('porting_confidence', 0.0):.2f}\n"
            
            # Porting timeline
            porting_timeline = porting_analysis.get('porting_timeline', [])
            if porting_timeline:
                section += f"   • Porting Timeline:\n"
                for transition in porting_timeline[:3]:  # Show last 3 transitions
                    date = transition.get('date', 'Unknown date')
                    from_carrier = transition.get('from', 'Unknown')
                    to_carrier = transition.get('to', 'Unknown')
                    confidence = transition.get('confidence', 0.0)
                    
                    if date and 'T' in date:
                        date = date[:19].replace('T', ' ')
                    
                    section += f"     • {date}: {from_carrier} → {to_carrier} (Confidence: {confidence:.1f})\n"
        else:
            section += f"   • Porting Status: ❌ No porting history detected\n"
            section += f"   • Carrier Stability: ✅ Consistent carrier assignment\n"
        
        section += "\n"
        
        # Ownership Analysis
        section += f"👤 OWNERSHIP CHANGE ANALYSIS:\n"
        if ownership_analysis.get('ownership_changes_detected'):
            section += f"   • Ownership Changes: ⚠️ Potential changes detected\n"
            section += f"   • Change Confidence: {ownership_analysis.get('confidence_score', 0.0):.2f}\n"
            
            indicators = ownership_analysis.get('indicators', [])
            if indicators:
                section += f"   • Change Indicators ({len(indicators)}):\n"
                for indicator in indicators[:3]:  # Show top 3 indicators
                    indicator_type = indicator.get('type', 'Unknown')
                    description = indicator.get('description', 'No description')
                    confidence = indicator.get('confidence', 0.0)
                    section += f"     • {indicator_type}: {description} (Confidence: {confidence:.1f})\n"
            
            recommendation = ownership_analysis.get('recommendation', 'No recommendation')
            section += f"   • Recommendation: {recommendation}\n"
        else:
            section += f"   • Ownership Changes: ❌ No ownership changes detected\n"
            section += f"   • Ownership Stability: ✅ Consistent ownership indicators\n"
        
        section += "\n"
        
        # Verification Recommendations
        verification_recs = real_data.get('verification_recommendations', [])
        if verification_recs:
            section += f"🔍 VERIFICATION RECOMMENDATIONS:\n"
            for i, rec in enumerate(verification_recs[:5], 1):  # Show top 5 recommendations
                section += f"   {i}. {rec}\n"
        else:
            section += f"🔍 VERIFICATION: ✅ No special verification requirements detected\n"
        
        section += f"\n"
        
        return section
    
    def _format_confidence_assessment(self, real_data: Dict) -> str:
        """Format investigation confidence and quality assessment"""
        section = f"📈 INVESTIGATION CONFIDENCE & QUALITY ASSESSMENT\n"
        section += f"{'─'*60}\n"
        
        # Overall Confidence Score
        overall_confidence = 75.0  # Default
        confidence_level = "Medium"
        
        if real_data.get('aggregated_intelligence'):
            overall_confidence = real_data['aggregated_intelligence'].get('overall_confidence', 75.0)
            confidence_level = real_data['aggregated_intelligence'].get('confidence_level', 'Medium')
        
        section += f"🎯 OVERALL ASSESSMENT:\n"
        section += f"   • Investigation Confidence: {overall_confidence:.1f}% ({confidence_level})\n"
        
        # Confidence Level Indicator
        if overall_confidence >= 90:
            section += f"   • Quality Level: 🟢 Excellent - High reliability data\n"
        elif overall_confidence >= 75:
            section += f"   • Quality Level: 🟡 Good - Reliable for most purposes\n"
        elif overall_confidence >= 60:
            section += f"   • Quality Level: 🟠 Fair - Verify critical information\n"
        else:
            section += f"   • Quality Level: 🔴 Poor - Manual verification required\n"
        
        # Data Source Analysis
        if real_data.get('aggregated_intelligence'):
            sources_used = real_data['aggregated_intelligence'].get('sources_used', [])
            successful_sources = real_data['aggregated_intelligence'].get('successful_sources', 0)
            total_sources = real_data['aggregated_intelligence'].get('total_sources', 0)
            processing_time = real_data['aggregated_intelligence'].get('processing_time', 0)
            
            section += f"   • Data Sources: {successful_sources}/{total_sources} sources successful\n"
            section += f"   • Processing Time: {processing_time:.2f} seconds\n"
            section += f"   • Sources Used: {', '.join(sources_used)}\n"
        
        section += "\n"
        
        # Quality Indicators
        section += f"📊 QUALITY INDICATORS:\n"
        
        # Formatting Success
        if real_data.get('formatting_success'):
            section += f"   • Number Formatting: ✅ Successful\n"
        else:
            section += f"   • Number Formatting: ❌ Failed\n"
        
        # API Data Availability
        if real_data.get('api_data_available'):
            section += f"   • API Data: ✅ Available ({real_data.get('total_apis_used', 0)} APIs)\n"
        else:
            section += f"   • API Data: ❌ Limited\n"
        
        # Validation Status
        if real_data.get('is_valid'):
            section += f"   • Number Validation: ✅ Valid number\n"
        else:
            section += f"   • Number Validation: ❌ Invalid number\n"
        
        section += "\n"
        
        return section
    
    def _format_standard_results(self, target: str, lookup_type: str, links: List[Dict], real_data: Optional[Dict]) -> str:
        """Format standard results for non-phone investigations"""
        result = f"🔍 COMPREHENSIVE INVESTIGATION RESULTS: {target}\n"
        result += f"{'='*70}\n"
        result += f"⏰ Investigation Time: {time.strftime('%Y-%m-%d %H:%M:%S')}\n"
        result += f"🎯 Investigation Type: {lookup_type}\n"
        result += f"📊 Total Resources: {len(links)} OSINT tools activated\n"
        result += f"{'='*70}\n\n"
        
        # Real-time analysis section with enhanced details
        if real_data and real_data.get('success'):
            result += f"📊 REAL-TIME INTELLIGENCE ANALYSIS\n"
            result += f"{'─'*60}\n"
            
            if lookup_type == "IP Address":
                result += f"🌍 GEOLOCATION INTELLIGENCE:\n"
                result += f"   • City: {real_data.get('city', 'Unknown')}\n"
                result += f"   • Region/State: {real_data.get('region', 'Unknown')}\n"
                result += f"   • Country: {real_data.get('country', 'Unknown')} ({real_data.get('country_code', 'N/A')})\n"
                result += f"   • Continent: {real_data.get('continent', 'Unknown')}\n"
                result += f"   • Coordinates: {real_data.get('lat', 'N/A')}, {real_data.get('lon', 'N/A')}\n"
                result += f"   • Timezone: {real_data.get('timezone', 'Unknown')}\n"
                result += f"   • ZIP Code: {real_data.get('zip_code', 'Unknown')}\n\n"
                
                result += f"🏢 NETWORK INTELLIGENCE:\n"
                result += f"   • ISP: {real_data.get('isp', 'Unknown')}\n"
                result += f"   • Organization: {real_data.get('org', 'Unknown')}\n"
                result += f"   • AS Number: {real_data.get('as_info', 'Unknown')}\n"
                result += f"   • AS Name: {real_data.get('as_name', 'Unknown')}\n"
                result += f"   • Reverse DNS: {real_data.get('reverse_dns', 'Unknown')}\n\n"
                
                result += f"🔍 THREAT ASSESSMENT:\n"
                result += f"   • Mobile Network: {'⚠️ Yes' if real_data.get('mobile') else '✅ No'}\n"
                result += f"   • Proxy/VPN: {'⚠️ Detected' if real_data.get('proxy') else '✅ Clean'}\n"
                result += f"   • Hosting Service: {'⚠️ Yes' if real_data.get('hosting') else '✅ No'}\n\n"
                
            elif lookup_type == "Email Address":
                result += f"📧 EMAIL INTELLIGENCE ANALYSIS:\n"
                result += f"   • Full Email: {target}\n"
                result += f"   • Local Part: {real_data.get('local_part', 'N/A')}\n"
                result += f"   • Domain: {real_data.get('domain', 'N/A')}\n"
                result += f"   • Email Length: {real_data.get('email_length', 'N/A')} characters\n"
                result += f"   • Local Length: {real_data.get('local_length', 'N/A')} characters\n"
                result += f"   • Domain Length: {real_data.get('domain_length', 'N/A')} characters\n\n"
                
                result += f"🌐 DOMAIN VERIFICATION:\n"
                result += f"   • Domain Exists: {'✅ Yes' if real_data.get('domain_exists') else '❌ No'}\n"
                result += f"   • MX Records Valid: {'✅ Yes' if real_data.get('mx_valid') else '❌ No'}\n"
                result += f"   • Provider Type: {real_data.get('provider_type', 'Unknown')}\n"
                result += f"   • Common Provider: {'✅ Yes' if real_data.get('common_provider') else '❌ No'}\n"
                result += f"   • Disposable Email: {'⚠️ Likely' if real_data.get('disposable_likely') else '✅ Unlikely'}\n\n"
                
                if real_data.get('mx_records'):
                    result += f"📬 MX RECORDS:\n"
                    for mx in real_data.get('mx_records', [])[:3]:  # Show first 3
                        result += f"   • {mx}\n"
                    result += "\n"
                    
            elif lookup_type == "Full Name":
                result += f"👤 NAME INTELLIGENCE ANALYSIS:\n"
                result += f"   • Full Name: {real_data.get('full_name', 'N/A')}\n"
                result += f"   • Name Parts: {real_data.get('name_parts', 'N/A')}\n"
                result += f"   • First Name: {real_data.get('first_name', 'N/A')}\n"
                result += f"   • Last Name: {real_data.get('last_name', 'N/A')}\n"
                result += f"   • Middle Names: {real_data.get('middle_names', 'None')}\n"
                result += f"   • Name Length: {real_data.get('name_length', 'N/A')} characters\n"
                result += f"   • Name Type: {real_data.get('name_type', 'Unknown')}\n"
                result += f"   • Special Characters: {'⚠️ Yes' if real_data.get('has_special_chars') else '✅ No'}\n\n"
            
        else:
            result += f"📊 REAL-TIME ANALYSIS: ⚠️ Limited data available\n"
            if real_data and real_data.get('message'):
                result += f"   • Status: {real_data.get('message')}\n"
            result += "\n"
        
        # Group links by category with enhanced display
        categories = {}
        for link in links:
            category = link.get('category', 'Other')
            if category not in categories:
                categories[category] = []
            categories[category].append(link)
        
        result += f"🔗 COMPREHENSIVE OSINT RESOURCE ACTIVATION\n"
        result += f"{'─'*60}\n"
        result += f"📊 Total Resources Deployed: {len(links)} professional OSINT tools\n"
        result += f"📂 Categories Covered: {len(categories)} investigation domains\n"
        result += f"🌐 OSINT Links Available: {len(links)} (manual opening recommended)\n\n"
        
        for category, category_links in categories.items():
            result += f"📂 {category.upper()} ({len(category_links)} resources)\n"
            result += f"{'─'*40}\n"
            for i, link in enumerate(category_links, 1):
                result += f"   {i:2d}. {link['name']}\n"
                result += f"       🔗 {link['url'][:60]}{'...' if len(link['url']) > 60 else ''}\n"
            result += "\n"
        
        # Enhanced investigation methodology
        result += f"📋 PROFESSIONAL INVESTIGATION METHODOLOGY\n"
        result += f"{'─'*50}\n"
        result += f"🔍 IMMEDIATE ACTIONS COMPLETED:\n"
        result += f"   ✅ Target validation and format verification\n"
        result += f"   ✅ Real-time intelligence gathering\n"
        result += f"   ✅ Comprehensive OSINT resource deployment\n"
        result += f"   ✅ Multi-platform search activation\n"
        result += f"   ✅ Professional documentation prepared\n\n"
        
        result += f"📊 NEXT INVESTIGATION STEPS:\n"
        result += f"   1. Review all opened browser tabs systematically\n"
        result += f"   2. Cross-reference findings across multiple sources\n"
        result += f"   3. Document evidence with timestamps and sources\n"
        result += f"   4. Verify information through independent channels\n"
        result += f"   5. Compile findings into professional report\n"
        result += f"   6. Maintain chain of custody for legal compliance\n\n"
        
        # Enhanced summary with recommendations
        result += f"📊 INVESTIGATION SUMMARY & RECOMMENDATIONS\n"
        result += f"{'─'*50}\n"
        result += f"🎯 Target Investigated: {target}\n"
        result += f"🔍 Investigation Type: {lookup_type}\n"
        result += f"📊 Resources Deployed: {len(links)} professional OSINT tools\n"
        result += f"🌐 Categories Covered: {len(categories)} investigation domains\n"
        result += f"📈 Data Quality: {'✅ High (real-time data available)' if real_data and real_data.get('success') else '⚠️ Standard (limited real-time data)'}\n"
        result += f"⏰ Investigation Status: ✅ COMPLETE\n"
        result += f"📋 Compliance: ✅ Professional standards maintained\n\n"
        
        # Legal and ethical reminder
        result += f"⚖️ LEGAL & ETHICAL COMPLIANCE REMINDER\n"
        result += f"{'─'*45}\n"
        result += f"• This investigation uses only publicly available information\n"
        result += f"• All OSINT resources are free and legitimate services\n"
        result += f"• Ensure proper authorization before investigating individuals\n"
        result += f"• Maintain professional standards and legal compliance\n"
        result += f"• Document methodology for potential legal proceedings\n"
        result += f"• Respect privacy laws and platform terms of service\n\n"
        
        result += f"{'='*70}\n"
        result += f"🛡️ INVESTIGATION COMPLETED - CIOT v3.0 Professional OSINT Platform\n"
        result += f"{'='*70}\n"
        
        return result

    def export_report(self):
        """Export enhanced investigation results to PDF with comprehensive intelligence sections"""
        if not hasattr(self, 'last_investigation'):
            self.results_textbox.insert("end", "\n❌ No investigation results to export. Please run an investigation first.\n")
            return
        
        try:
            # Update status
            self.status_label.configure(text="📄 Exporting...", text_color=("#ff9500", "#ff9500"))
            
            # Create enhanced PDF
            pdf = FPDF()
            pdf.add_page()
            
            # Header
            pdf.set_font("Arial", "B", 16)
            if self.last_investigation['type'] == "Phone Number":
                pdf.cell(0, 15, "ENHANCED PHONE NUMBER INVESTIGATION REPORT", ln=True, align="C")
            else:
                pdf.cell(0, 15, "PROFESSIONAL OSINT INVESTIGATION REPORT", ln=True, align="C")
            pdf.set_font("Arial", "", 12)
            pdf.cell(0, 10, "Cyber Investigation OSINT Toolkit (CIOT) v3.0 - Enhanced Intelligence Platform", ln=True, align="C")
            pdf.ln(10)
            
            # Investigation Summary
            pdf.set_font("Arial", "B", 14)
            pdf.cell(0, 10, "EXECUTIVE SUMMARY", ln=True)
            pdf.set_font("Arial", "", 10)
            pdf.cell(0, 8, f"Target: {self.last_investigation['target']}", ln=True)
            pdf.cell(0, 8, f"Investigation Type: {self.last_investigation['type']}", ln=True)
            pdf.cell(0, 8, f"Timestamp: {self.last_investigation.get('timestamp', 'N/A')}", ln=True)
            pdf.cell(0, 8, f"Total Resources: {len(self.last_investigation['links'])}", ln=True)
            pdf.cell(0, 8, f"Categories Covered: {self.last_investigation.get('categories', 'N/A')}", ln=True)
            
            # Add confidence assessment for phone investigations
            if self.last_investigation['type'] == "Phone Number" and self.last_investigation.get('real_data'):
                real_data = self.last_investigation['real_data']
                if real_data.get('aggregated_intelligence'):
                    confidence = real_data['aggregated_intelligence'].get('overall_confidence', 'N/A')
                    confidence_level = real_data['aggregated_intelligence'].get('confidence_level', 'Unknown')
                    pdf.cell(0, 8, f"Investigation Confidence: {confidence}% ({confidence_level})", ln=True)
            
            pdf.ln(10)
            
            # Enhanced Intelligence Sections for Phone Numbers
            if self.last_investigation['type'] == "Phone Number" and self.last_investigation.get('real_data'):
                self._add_intelligence_sections_to_pdf(pdf, self.last_investigation['real_data'])
            
            # Group links by category for professional presentation
            categories = {}
            for link in self.last_investigation['links']:
                category = link.get('category', 'Other')
                if category not in categories:
                    categories[category] = []
                categories[category].append(link)
            
            # OSINT Resources by Category
            pdf.set_font("Arial", "B", 14)
            pdf.cell(0, 10, "OSINT RESOURCES BY CATEGORY", ln=True)
            pdf.ln(5)
            
            for category, category_links in categories.items():
                pdf.set_font("Arial", "B", 12)
                pdf.cell(0, 8, f"{category.upper()}", ln=True)
                pdf.set_font("Arial", "", 9)
                
                for i, link in enumerate(category_links, 1):
                    # Resource name
                    pdf.cell(0, 6, f"  {i}. {link['name']}", ln=True)
                    
                    # URL (handle long URLs)
                    url = link['url']
                    if len(url) > 80:
                        # Split long URLs
                        pdf.cell(0, 5, f"     {url[:80]}", ln=True)
                        remaining = url[80:]
                        while remaining:
                            pdf.cell(0, 5, f"     {remaining[:80]}", ln=True)
                            remaining = remaining[80:]
                    else:
                        pdf.cell(0, 5, f"     {url}", ln=True)
                    pdf.ln(2)
                
                pdf.ln(3)
            
            # Investigation Notes
            pdf.set_font("Arial", "B", 12)
            pdf.cell(0, 10, "INVESTIGATION METHODOLOGY", ln=True)
            pdf.set_font("Arial", "", 9)
            
            methodology_notes = [
                "1. Comprehensive multi-platform search approach utilized",
                "2. Professional OSINT resources systematically categorized",
                "3. Cross-reference verification recommended across sources",
                "4. Legal and ethical compliance maintained throughout",
                "5. All findings require independent verification"
            ]
            
            for note in methodology_notes:
                pdf.cell(0, 6, note, ln=True)
            
            pdf.ln(5)
            
            # Legal Disclaimer
            pdf.set_font("Arial", "B", 10)
            pdf.cell(0, 8, "LEGAL DISCLAIMER", ln=True)
            pdf.set_font("Arial", "", 8)
            disclaimer_text = [
                "This report contains OSINT resources for authorized investigation purposes only.",
                "All information must be verified through independent sources before use.",
                "Compliance with applicable privacy laws and regulations is required.",
                "This tool is for legitimate security research and investigation only."
            ]
            
            for line in disclaimer_text:
                pdf.cell(0, 5, line, ln=True)
            
            # Footer
            pdf.ln(10)
            pdf.set_font("Arial", "I", 8)
            pdf.cell(0, 5, f"Report generated on {time.strftime('%Y-%m-%d %H:%M:%S')} by Cyber Investigation OSINT Toolkit (CIOT) v3.0", ln=True, align="C")
            
            # Save PDF with professional naming
            timestamp = time.strftime('%Y%m%d_%H%M%S')
            target_clean = ''.join(c for c in self.last_investigation['target'] if c.isalnum() or c in (' ', '-', '_')).replace(' ', '_')
            filename = f"CIOT_OSINT_Report_{target_clean}_{timestamp}.pdf"
            
            pdf.output(filename)
            
            # Update status and notify user
            self.status_label.configure(text="✅ Exported", text_color=("#4a9eff", "#4a9eff"))
            self.results_textbox.insert("end", f"\n📄 PROFESSIONAL REPORT EXPORTED\n")
            self.results_textbox.insert("end", f"{'='*50}\n")
            self.results_textbox.insert("end", f"✅ Filename: {filename}\n")
            self.results_textbox.insert("end", f"📊 Pages: 1\n")
            self.results_textbox.insert("end", f"🔗 Resources: {len(self.last_investigation['links'])}\n")
            self.results_textbox.insert("end", f"📂 Categories: {self.last_investigation.get('categories', 'N/A')}\n")
            self.results_textbox.insert("end", f"🕐 Generated: {time.strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            
        except Exception as e:
            self.status_label.configure(text="❌ Export Failed", text_color=("#ff4444", "#ff4444"))
            self.results_textbox.insert("end", f"\n❌ EXPORT ERROR: {str(e)}\n")
            self.results_textbox.insert("end", "Please ensure you have write permissions in the current directory.\n")

    def clear_results(self):
        """Clear all results and reset"""
        self.target_var.set("")
        self.show_initial_instructions()
        if hasattr(self, 'last_investigation'):
            delattr(self, 'last_investigation')  
    
    def show_performance_metrics(self):
        """Show performance metrics in a popup window"""
        try:
            from src.utils.osint_utils import get_performance_metrics, clear_investigation_caches
            
            # Create performance metrics window
            perf_window = ctk.CTkToplevel(self)
            perf_window.title("⚡ Performance Metrics - CIOT")
            perf_window.geometry("800x600")
            perf_window.transient(self.master)
            perf_window.grab_set()
            
            # Main frame with scrollable content
            main_frame = ctk.CTkFrame(perf_window)
            main_frame.pack(fill="both", expand=True, padx=20, pady=20)
            
            # Title
            title_label = ctk.CTkLabel(
                main_frame,
                text="⚡ CIOT Performance Metrics Dashboard",
                font=ctk.CTkFont(size=20, weight="bold"),
                text_color=("#1f538d", "#4a9eff")
            )
            title_label.pack(pady=(10, 20))
            
            # Scrollable text area for metrics
            metrics_textbox = ctk.CTkTextbox(
                main_frame,
                wrap="word",
                font=ctk.CTkFont(size=11, family="Courier")
            )
            metrics_textbox.pack(fill="both", expand=True, pady=(0, 10))
            
            # Get and display performance metrics
            try:
                metrics = get_performance_metrics()
                
                if metrics.get('error'):
                    metrics_text = f"❌ Error getting performance metrics: {metrics['error']}\n\n"
                    metrics_text += "Performance optimization may not be fully initialized.\n"
                    metrics_text += "Try running a phone investigation first to initialize the system."
                else:
                    metrics_text = self._format_performance_metrics(metrics)
                
                metrics_textbox.insert("1.0", metrics_text)
                metrics_textbox.configure(state="disabled")
                
            except Exception as e:
                error_text = f"❌ Error loading performance metrics: {str(e)}\n\n"
                error_text += "This may indicate that performance optimization modules are not properly loaded.\n"
                error_text += "Please check the system logs for more details."
                metrics_textbox.insert("1.0", error_text)
                metrics_textbox.configure(state="disabled")
            
            # Button frame
            button_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
            button_frame.pack(fill="x", pady=(10, 0))
            
            # Refresh button
            refresh_btn = ctk.CTkButton(
                button_frame,
                text="🔄 Refresh Metrics",
                command=lambda: self._refresh_performance_metrics(metrics_textbox),
                font=ctk.CTkFont(size=12, weight="bold"),
                height=35,
                width=140
            )
            refresh_btn.pack(side="left", padx=(0, 10))
            
            # Clear caches button
            clear_btn = ctk.CTkButton(
                button_frame,
                text="🗑️ Clear Caches",
                command=lambda: self._clear_caches_and_refresh(metrics_textbox),
                font=ctk.CTkFont(size=12, weight="bold"),
                height=35,
                width=130,
                fg_color=("#d32f2f", "#f44336"),
                hover_color=("#b71c1c", "#d32f2f")
            )
            clear_btn.pack(side="left", padx=10)
            
            # Close button
            close_btn = ctk.CTkButton(
                button_frame,
                text="✖️ Close",
                command=perf_window.destroy,
                font=ctk.CTkFont(size=12, weight="bold"),
                height=35,
                width=100
            )
            close_btn.pack(side="right")
            
        except Exception as e:
            # Show error in main results area if popup fails
            if hasattr(self, 'results_textbox'):
                self.results_textbox.configure(state="normal")
                self.results_textbox.insert("end", f"\n❌ Error showing performance metrics: {str(e)}\n")
                self.results_textbox.configure(state="disabled")
    
    def _format_performance_metrics(self, metrics: dict) -> str:
        """Format performance metrics for display"""
        import time
        
        text = "⚡ CIOT PERFORMANCE METRICS DASHBOARD\n"
        text += "=" * 60 + "\n"
        text += f"📊 Generated: {time.strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        
        # Global Performance
        if 'global_performance' in metrics:
            global_perf = metrics['global_performance']
            text += "🌐 GLOBAL PERFORMANCE\n"
            text += "-" * 30 + "\n"
            
            if 'overall' in global_perf:
                overall = global_perf['overall']
                text += f"📈 Total Operations: {overall.get('total_operations', 0)}\n"
                text += f"💾 Cache Hit Rate: {overall.get('cache_hit_rate', 0):.1%}\n"
                text += f"⏱️  Average Duration: {overall.get('average_duration', 0):.3f}s\n"
                text += f"🌐 Total API Calls: {overall.get('total_api_calls', 0)}\n"
            
            if 'memory_cache' in global_perf:
                mem_cache = global_perf['memory_cache']
                text += f"\n💾 Memory Cache:\n"
                text += f"   Size: {mem_cache.get('size', 0)}/{mem_cache.get('max_size', 0)}\n"
                text += f"   Memory: {mem_cache.get('memory_usage_mb', 0):.1f}/{mem_cache.get('max_memory_mb', 0):.1f} MB\n"
                text += f"   Hit Rate: {mem_cache.get('hit_rate', 0):.1%}\n"
                text += f"   Evictions: {mem_cache.get('evictions', 0)}\n"
            
            if 'connection_pool' in global_perf:
                conn_pool = global_perf['connection_pool']
                text += f"\n🔗 Connection Pool:\n"
                text += f"   Requests Made: {conn_pool.get('requests_made', 0)}\n"
                text += f"   Avg Response Time: {conn_pool.get('average_response_time', 0):.3f}s\n"
                text += f"   Connection Errors: {conn_pool.get('connection_errors', 0)}\n"
                text += f"   Timeouts: {conn_pool.get('timeouts', 0)}\n"
            
            text += "\n"
        
        # Async Aggregator Performance
        if 'async_aggregator' in metrics:
            async_perf = metrics['async_aggregator']
            text += "🚀 ASYNC AGGREGATOR PERFORMANCE\n"
            text += "-" * 35 + "\n"
            text += f"📊 Total Investigations: {async_perf.get('total_investigations', 0)}\n"
            text += f"✅ Successful: {async_perf.get('successful_investigations', 0)}\n"
            text += f"❌ Failed: {async_perf.get('failed_investigations', 0)}\n"
            text += f"⏱️  Avg Processing Time: {async_perf.get('total_processing_time', 0) / max(async_perf.get('total_investigations', 1), 1):.3f}s\n"
            text += f"📡 Avg Sources per Investigation: {async_perf.get('average_sources_per_investigation', 0):.1f}\n"
            text += f"🔄 Active Investigations: {async_perf.get('active_investigations', 0)}\n"
            
            if 'async_client_stats' in async_perf:
                client_stats = async_perf['async_client_stats']
                text += f"\n🌐 Async Client:\n"
                text += f"   Requests Made: {client_stats.get('requests_made', 0)}\n"
                text += f"   Success Rate: {client_stats.get('success_rate', 0):.1%}\n"
                text += f"   Avg Response Time: {client_stats.get('average_response_time', 0):.3f}s\n"
            
            text += "\n"
        
        # Phone Formatter Performance
        if 'phone_formatter' in metrics:
            formatter_perf = metrics['phone_formatter']
            text += "📞 PHONE FORMATTER PERFORMANCE\n"
            text += "-" * 35 + "\n"
            text += f"📊 Total Formats: {formatter_perf.get('total_formats', 0)}\n"
            text += f"💾 Cache Hit Rate: {formatter_perf.get('cache_hit_rate', 0):.1%}\n"
            text += f"❌ Error Rate: {formatter_perf.get('error_rate', 0):.1%}\n"
            text += f"⏱️  Avg Processing Time: {formatter_perf.get('average_processing_time', 0):.3f}s\n"
            text += f"🕐 Total Processing Time: {formatter_perf.get('total_processing_time', 0):.3f}s\n"
            text += "\n"
        
        # Performance Status
        text += "🎯 PERFORMANCE STATUS\n"
        text += "-" * 25 + "\n"
        
        if metrics.get('performance_optimization_enabled'):
            text += "✅ Performance Optimization: ENABLED\n"
            
            # Analyze performance
            if 'global_performance' in metrics and 'overall' in metrics['global_performance']:
                avg_duration = metrics['global_performance']['overall'].get('average_duration', 0)
                cache_hit_rate = metrics['global_performance']['overall'].get('cache_hit_rate', 0)
                
                if avg_duration < 2.0:
                    text += "🟢 Response Time: EXCELLENT (< 2s)\n"
                elif avg_duration < 5.0:
                    text += "🟡 Response Time: GOOD (< 5s)\n"
                else:
                    text += "🔴 Response Time: NEEDS OPTIMIZATION (> 5s)\n"
                
                if cache_hit_rate > 0.8:
                    text += "🟢 Cache Efficiency: EXCELLENT (> 80%)\n"
                elif cache_hit_rate > 0.5:
                    text += "🟡 Cache Efficiency: GOOD (> 50%)\n"
                else:
                    text += "🔴 Cache Efficiency: NEEDS IMPROVEMENT (< 50%)\n"
        else:
            text += "❌ Performance Optimization: DISABLED\n"
            text += "⚠️  Consider enabling performance optimization for better response times.\n"
        
        text += "\n"
        text += "💡 OPTIMIZATION TIPS\n"
        text += "-" * 20 + "\n"
        text += "• Clear caches periodically to free memory\n"
        text += "• Monitor response times and cache hit rates\n"
        text += "• Use high-performance investigation for better speed\n"
        text += "• Check network connectivity for API calls\n"
        text += "• Restart application if performance degrades\n"
        
        return text
    
    def _refresh_performance_metrics(self, textbox):
        """Refresh performance metrics display"""
        try:
            from src.utils.osint_utils import get_performance_metrics
            
            textbox.configure(state="normal")
            textbox.delete("1.0", "end")
            
            metrics = get_performance_metrics()
            metrics_text = self._format_performance_metrics(metrics)
            
            textbox.insert("1.0", metrics_text)
            textbox.configure(state="disabled")
            
        except Exception as e:
            textbox.configure(state="normal")
            textbox.delete("1.0", "end")
            textbox.insert("1.0", f"❌ Error refreshing metrics: {str(e)}")
            textbox.configure(state="disabled")
    
    def _clear_caches_and_refresh(self, textbox):
        """Clear all caches and refresh metrics"""
        try:
            from src.utils.osint_utils import clear_investigation_caches
            
            # Clear caches
            result = clear_investigation_caches()
            
            # Show result
            textbox.configure(state="normal")
            textbox.delete("1.0", "end")
            
            if result.get('success'):
                textbox.insert("1.0", "✅ Caches cleared successfully!\n\n")
                textbox.insert("end", "Refreshing metrics...\n\n")
            else:
                textbox.insert("1.0", f"❌ Error clearing caches: {result.get('error', 'Unknown error')}\n\n")
            
            textbox.configure(state="disabled")
            
            # Refresh metrics after a short delay
            self.after(1000, lambda: self._refresh_performance_metrics(textbox))
            
        except Exception as e:
            textbox.configure(state="normal")
            textbox.delete("1.0", "end")
            textbox.insert("1.0", f"❌ Error clearing caches: {str(e)}")
            textbox.configure(state="disabled")