import customtkinter as ctk
import re
import webbrowser

class AadhaarTab(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.setup_ui()

    def show_info_popup(self):
        """Show information about Aadhaar Analysis"""
        info_window = ctk.CTkToplevel(self)
        info_window.title("Aadhaar Analysis - Information")
        info_window.geometry("600x400")
        info_window.transient(self.master)
        info_window.grab_set()
        
        content = ctk.CTkTextbox(info_window, wrap="word")
        content.pack(fill="both", expand=True, padx=20, pady=20)
        
        info_text = """🆔 AADHAAR ANALYSIS TAB

WHAT IT DOES:
Validates Indian Aadhaar numbers using the official Verhoeff algorithm and provides security analysis.

KEY FEATURES:
• Aadhaar Number Validation - Check if format and checksum are correct
• Verhoeff Algorithm - Mathematical validation used by UIDAI
• Security Analysis - Privacy and safety recommendations
• Format Checking - Ensures proper 12-digit structure

HOW TO USE:
1. Enter a 12-digit Aadhaar number (with or without dashes/spaces)
2. Click 'Validate Aadhaar' to check mathematical validity
3. Click 'Check Online' to access official UIDAI resources
4. Review analysis results and security recommendations

CYBER INVESTIGATION APPLICATIONS:
• Document verification in fraud cases
• Identity validation during investigations
• KYC (Know Your Customer) compliance
• Digital forensics and evidence verification
• Detecting fake or invalid Aadhaar numbers
• Educational purposes for understanding Aadhaar structure

VALIDATION ALGORITHM:
This tool uses the Verhoeff checksum algorithm, the same mathematical 
formula used by UIDAI to generate and validate Aadhaar numbers.

WHAT GETS VALIDATED:
✓ 12-digit length requirement
✓ Numerical format (digits only)
✓ Verhoeff checksum calculation
✓ Mathematical validity according to UIDAI standards

SECURITY FEATURES:
• No Aadhaar numbers are stored or transmitted
• All validation happens locally on your computer
• Privacy protection guidance provided
• Security best practices recommended

IMPORTANT LEGAL NOTES:
• Only use for legitimate purposes (verification, investigation)
• Comply with India's data protection laws
• Aadhaar Act 2016 and amendments apply
• Do not use for unauthorized access or identity theft
• Respect individual privacy rights

PRIVACY RECOMMENDATIONS:
• Never share Aadhaar numbers publicly
• Use masked Aadhaar (showing only last 4 digits)
• Enable biometric lock through official UIDAI website
• Be cautious of phishing attempts requesting Aadhaar data
• Regularly check for unauthorized usage

This tool is for educational and legitimate investigative purposes only."""

        content.insert("1.0", info_text)
        content.configure(state="disabled")

    def setup_ui(self):
        # Title
        title_label = ctk.CTkLabel(self, text="🆔 Aadhaar Validation & Analysis", 
                                 font=ctk.CTkFont(size=24, weight="bold"))
        title_label.pack(pady=20)

        # Description
        desc_label = ctk.CTkLabel(self, text="Validate Indian Aadhaar numbers using official Verhoeff algorithm", 
                                 font=ctk.CTkFont(size=14))
        desc_label.pack(pady=(0, 20))

        # Input frame
        input_frame = ctk.CTkFrame(self)
        input_frame.pack(fill="x", padx=40, pady=20)

        ctk.CTkLabel(input_frame, text="Enter Aadhaar Number:", 
                    font=ctk.CTkFont(size=16, weight="bold")).pack(pady=(15, 5))
        
        # Input with better styling
        self.aadhaar_var = ctk.StringVar()
        self.aadhaar_entry = ctk.CTkEntry(input_frame, textvariable=self.aadhaar_var, 
                                        width=300, height=40,
                                        placeholder_text="1234-5678-9012 or 123456789012",
                                        font=ctk.CTkFont(size=14))
        self.aadhaar_entry.pack(pady=15)

        # Buttons
        button_frame = ctk.CTkFrame(input_frame)
        button_frame.pack(pady=15)

        ctk.CTkButton(button_frame, text="✓ Validate Aadhaar", 
                     command=self.validate_aadhaar,
                     font=ctk.CTkFont(size=12, weight="bold"),
                     height=35).pack(side="left", padx=10)
        ctk.CTkButton(button_frame, text="🌐 UIDAI Portal", 
                     command=self.check_online,
                     font=ctk.CTkFont(size=12),
                     height=35).pack(side="left", padx=10)
        ctk.CTkButton(button_frame, text="🗑️ Clear", 
                     command=self.clear_results,
                     font=ctk.CTkFont(size=12),
                     height=35).pack(side="left", padx=10)

        # Standardized results section - consistent with Surface Web OSINT
        results_frame = ctk.CTkFrame(self, corner_radius=12)
        results_frame.pack(fill="both", expand=True, padx=20, pady=(10, 20))
        
        # Compact results header
        results_header = ctk.CTkFrame(results_frame, fg_color="transparent")
        results_header.pack(fill="x", padx=12, pady=(12, 8))
        
        results_icon = ctk.CTkLabel(results_header, text="📊", font=ctk.CTkFont(size=16))
        results_icon.pack(side="left")
        
        results_title = ctk.CTkLabel(
            results_header, 
            text="Analysis Results", 
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
        
        # Standardized results textbox - consistent dimensions
        self.results_textbox = ctk.CTkTextbox(
            results_frame, 
            font=ctk.CTkFont(size=11),
            corner_radius=8,
            border_width=1,
            wrap="word"
        )
        self.results_textbox.pack(fill="both", expand=True, padx=8, pady=(0, 8))
        
        # Initial instructions
        initial_text = """🆔 AADHAAR VALIDATION TOOL

WHAT THIS TOOL DOES:
✓ Validates Aadhaar number format and mathematical correctness
✓ Uses official Verhoeff algorithm employed by UIDAI
✓ Provides security and privacy recommendations
✓ Helps detect invalid or fake Aadhaar numbers

ENTER AN AADHAAR NUMBER ABOVE TO BEGIN ANALYSIS

Supported formats:
• 123456789012 (12 digits)
• 1234-5678-9012 (with dashes) 
• 1234 5678 9012 (with spaces)

IMPORTANT NOTES:
• This tool validates format only - it cannot verify if an Aadhaar number is actually assigned to a person
• All validation happens locally on your computer
• No Aadhaar numbers are stored or transmitted
• Only use for legitimate purposes (verification, investigation)
• Comply with Indian data protection laws

LEGAL COMPLIANCE:
This tool is designed for legitimate use cases including:
• Document verification in investigations
• KYC compliance validation  
• Educational purposes
• Fraud detection and prevention

Always ensure you have proper authorization before validating others' Aadhaar numbers."""

        self.results_textbox.insert("end", initial_text)

    def validate_aadhaar(self):
        aadhaar_input = self.aadhaar_var.get().strip()
        
        if not aadhaar_input:
            self.results_textbox.delete("1.0", "end")
            self.results_textbox.insert("end", "❌ Please enter an Aadhaar number to validate.\n")
            return

        # Clean the input (remove dashes, spaces)
        aadhaar = re.sub(r'[^0-9]', '', aadhaar_input)
        
        self.results_textbox.delete("1.0", "end")
        self.results_textbox.insert("end", "🔍 AADHAAR VALIDATION ANALYSIS\n")
        self.results_textbox.insert("end", "=" * 60 + "\n\n")
        
        self.results_textbox.insert("end", f"Input: {aadhaar_input}\n")
        self.results_textbox.insert("end", f"Cleaned: {aadhaar}\n\n")

        # Basic format validation
        validation_results = []
        
        # Length check
        if len(aadhaar) == 12:
            validation_results.append("✅ Length: 12 digits (Valid)")
        elif len(aadhaar) < 12:
            validation_results.append(f"❌ Length: {len(aadhaar)} digits (Too short - should be 12)")
        else:
            validation_results.append(f"❌ Length: {len(aadhaar)} digits (Too long - should be 12)")
        
        # Numeric check
        if aadhaar.isdigit():
            validation_results.append("✅ Format: All digits (Valid)")
        else:
            validation_results.append("❌ Format: Contains non-numeric characters (Invalid)")
            
        # Zero check (Aadhaar cannot start with 0 or 1)
        if aadhaar and aadhaar[0] not in ['0', '1']:
            validation_results.append("✅ First digit: Valid (not 0 or 1)")
        elif aadhaar and aadhaar[0] in ['0', '1']:
            validation_results.append("❌ First digit: Invalid (cannot start with 0 or 1)")
        
        self.results_textbox.insert("end", "📋 FORMAT VALIDATION RESULTS:\n")
        for result in validation_results:
            self.results_textbox.insert("end", f"  {result}\n")
        self.results_textbox.insert("end", "\n")

        # Proceed with Verhoeff validation only if basic format is correct
        if len(aadhaar) == 12 and aadhaar.isdigit() and aadhaar[0] not in ['0', '1']:
            is_valid = self.verhoeff_validate(aadhaar)
            
            self.results_textbox.insert("end", "🔬 VERHOEFF ALGORITHM VALIDATION:\n")
            if is_valid:
                self.results_textbox.insert("end", "✅ Mathematical validation: PASSED\n")
                self.results_textbox.insert("end", "✅ Checksum verification: VALID\n")
                self.results_textbox.insert("end", "✅ Overall result: VALID AADHAAR NUMBER\n\n")
                
                self.results_textbox.insert("end", "📊 DETAILED ANALYSIS:\n")
                self.results_textbox.insert("end", f"• First 11 digits: {aadhaar[:11]}\n")
                self.results_textbox.insert("end", f"• Check digit: {aadhaar[11]}\n")
                self.results_textbox.insert("end", f"• Calculated checksum: Valid ✓\n")
                
            else:
                self.results_textbox.insert("end", "❌ Mathematical validation: FAILED\n")
                self.results_textbox.insert("end", "❌ Checksum verification: INVALID\n")
                self.results_textbox.insert("end", "❌ Overall result: INVALID AADHAAR NUMBER\n\n")
                
                self.results_textbox.insert("end", "📊 DETAILED ANALYSIS:\n")
                self.results_textbox.insert("end", f"• Input number: {aadhaar}\n")
                self.results_textbox.insert("end", f"• Check digit: {aadhaar[11]}\n")
                self.results_textbox.insert("end", f"• Verhoeff validation: Failed ✗\n")
                self.results_textbox.insert("end", "• This number does not conform to UIDAI standards\n")
        
        else:
            self.results_textbox.insert("end", "❌ Cannot perform Verhoeff validation due to format errors\n\n")
        
        # Security and privacy recommendations
        self.results_textbox.insert("end", "\n🔒 SECURITY & PRIVACY RECOMMENDATIONS:\n")
        self.results_textbox.insert("end", "━" * 50 + "\n")
        self.results_textbox.insert("end", "🛡️ For Aadhaar holders:\n")
        self.results_textbox.insert("end", "  • Never share your Aadhaar number publicly\n")
        self.results_textbox.insert("end", "  • Use masked Aadhaar (show only last 4 digits)\n")
        self.results_textbox.insert("end", "  • Enable biometric lock through UIDAI website\n")
        self.results_textbox.insert("end", "  • Regularly check mAadhaar app for updates\n")
        self.results_textbox.insert("end", "  • Report suspicious activity to UIDAI immediately\n\n")
        
        self.results_textbox.insert("end", "🔍 For investigators:\n")
        self.results_textbox.insert("end", "  • This validates format only, not actual assignment\n")
        self.results_textbox.insert("end", "  • Always verify through official channels\n")
        self.results_textbox.insert("end", "  • Ensure legal authorization for investigation\n")
        self.results_textbox.insert("end", "  • Document validation results properly\n")
        self.results_textbox.insert("end", "  • Comply with data protection regulations\n\n")
        
        # Investigation notes
        self.results_textbox.insert("end", "📝 INVESTIGATIVE NOTES:\n")
        self.results_textbox.insert("end", "━" * 50 + "\n")
        if len(aadhaar) == 12 and aadhaar.isdigit():
            if self.verhoeff_validate(aadhaar):
                self.results_textbox.insert("end", "• Number structure suggests it could be a genuine Aadhaar\n")
                self.results_textbox.insert("end", "• Recommend verification through official UIDAI channels\n")
                self.results_textbox.insert("end", "• Document this validation for case records\n")
            else:
                self.results_textbox.insert("end", "• Number is mathematically invalid per UIDAI standards\n") 
                self.results_textbox.insert("end", "• Likely a fake, random, or incorrectly transcribed number\n")
                self.results_textbox.insert("end", "• Consider investigating source of this number\n")
        else:
            self.results_textbox.insert("end", "• Format errors suggest data entry mistakes or intentional obfuscation\n")
            self.results_textbox.insert("end", "• Verify original source and correct any transcription errors\n")

    def verhoeff_validate(self, aadhaar):
        """Validate Aadhaar using Verhoeff algorithm - official UIDAI method"""
        # Verhoeff multiplication table
        d = [
            [0, 1, 2, 3, 4, 5, 6, 7, 8, 9],
            [1, 2, 3, 4, 0, 6, 7, 8, 9, 5],
            [2, 3, 4, 0, 1, 7, 8, 9, 5, 6],
            [3, 4, 0, 1, 2, 8, 9, 5, 6, 7],
            [4, 0, 1, 2, 3, 9, 5, 6, 7, 8],
            [5, 9, 8, 7, 6, 0, 4, 3, 2, 1],
            [6, 5, 9, 8, 7, 1, 0, 4, 3, 2],
            [7, 6, 5, 9, 8, 2, 1, 0, 4, 3],
            [8, 7, 6, 5, 9, 3, 2, 1, 0, 4],
            [9, 8, 7, 6, 5, 4, 3, 2, 1, 0]
        ]

        # Permutation table
        p = [
            [0, 1, 2, 3, 4, 5, 6, 7, 8, 9],
            [1, 5, 7, 6, 2, 8, 3, 0, 9, 4],
            [5, 8, 0, 3, 7, 9, 6, 1, 4, 2],
            [8, 9, 1, 6, 0, 4, 3, 5, 2, 7],
            [9, 4, 5, 3, 1, 2, 6, 8, 7, 0],
            [4, 2, 8, 6, 5, 7, 3, 9, 0, 1],
            [2, 7, 9, 3, 8, 0, 6, 4, 1, 5],
            [7, 0, 4, 6, 9, 1, 3, 2, 5, 8]
        ]

        c = 0
        for i, digit in enumerate(reversed(aadhaar)):
            c = d[c][p[i % 8][int(digit)]]

        return c == 0

    def check_online(self):
        self.results_textbox.insert("end", "\n🌐 Opening official UIDAI resources...\n")
        webbrowser.open("https://uidai.gov.in/")

    def clear_results(self):
        self.aadhaar_var.set("")
        self.results_textbox.delete("1.0", "end")
        
        initial_text = """🆔 Ready for new Aadhaar validation

Enter an Aadhaar number above and click 'Validate Aadhaar' to begin analysis."""
        
        self.results_textbox.insert("end", initial_text)

