import customtkinter as ctk
import threading
import urllib.parse

class AIAssistantTab(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.setup_ui()

    def show_info_popup(self):
        """Show information about AI Assistant"""
        info_window = ctk.CTkToplevel(self)
        info_window.title("AI Assistant - Information")
        info_window.geometry("600x400")
        info_window.transient(self.master)
        info_window.grab_set()
        
        content = ctk.CTkTextbox(info_window, wrap="word")
        content.pack(fill="both", expand=True, padx=20, pady=20)
        
        info_text = """🤖 AI ASSISTANT TAB

WHAT IT DOES:
Your intelligent OSINT investigation assistant that provides methodology guidance, tool recommendations, and analysis help.

AVAILABLE SERVICES:
• Free AI Chat - Get basic AI responses for OSINT questions
• Offline Analysis - Local keyword and pattern analysis
• Web Search - Search-based intelligent answers

HOW TO USE:
1. Select your preferred AI service from the dropdown
2. Type your OSINT-related question in the text box
3. Click 'Ask AI' to get intelligent guidance
4. Use 'Clear' to reset for new questions

EXAMPLE QUESTIONS:
• "How do I investigate a suspicious email address?"
• "What OSINT techniques work best for social media analysis?"
• "How can I trace cryptocurrency transactions?"
• "What are the best practices for IP address investigation?"
• "How do I verify information found during OSINT research?"

CYBER INVESTIGATION APPLICATIONS:
• Investigation methodology planning
• Tool selection guidance
• Best practices consultation
• Research strategy development
• Training and education support
• Case analysis assistance

FEATURES:
• Rule-based responses for common OSINT scenarios
• Keyword analysis and pattern recognition
• Investigation workflow suggestions
• Legal and ethical guidance reminders

NOTE:
This assistant provides guidance based on established OSINT methodologies and best practices. Always verify information through multiple sources and ensure compliance with legal requirements."""

        content.insert("1.0", info_text)
        content.configure(state="disabled")

    def setup_ui(self):
        # Title
        title_label = ctk.CTkLabel(self, text="🤖 OSINT Investigation Assistant", 
                                 font=ctk.CTkFont(size=24, weight="bold"))
        title_label.pack(pady=20)

        # AI Service selection
        service_frame = ctk.CTkFrame(self)
        service_frame.pack(fill="x", padx=20, pady=10)

        ctk.CTkLabel(service_frame, text="AI Service:", 
                    font=ctk.CTkFont(size=14, weight="bold")).pack(side="left", padx=10)
        
        self.ai_service = ctk.StringVar(value="Free AI Chat")
        ai_menu = ctk.CTkOptionMenu(service_frame, variable=self.ai_service,
                                   values=["Free AI Chat", "Offline Analysis", "Web Search"],
                                   font=ctk.CTkFont(size=12))
        ai_menu.pack(side="left", padx=10)

        # Input frame
        input_frame = ctk.CTkFrame(self)
        input_frame.pack(fill="x", padx=20, pady=10)

        ctk.CTkLabel(input_frame, text="Ask your OSINT question:", 
                    font=ctk.CTkFont(size=14, weight="bold")).pack(anchor="w", padx=10, pady=5)

        self.question_text = ctk.CTkTextbox(input_frame, height=100, 
                                           font=ctk.CTkFont(size=12))
        self.question_text.pack(fill="x", padx=10, pady=5)
        self.question_text.insert("1.0", "Example: How do I investigate a suspicious email address?")

        # Buttons
        button_frame = ctk.CTkFrame(input_frame)
        button_frame.pack(pady=10)

        ctk.CTkButton(button_frame, text="🤖 Ask AI", command=self.ask_ai,
                     font=ctk.CTkFont(size=12, weight="bold")).pack(side="left", padx=10)
        ctk.CTkButton(button_frame, text="🗑️ Clear", command=self.clear_all,
                     font=ctk.CTkFont(size=12)).pack(side="left", padx=10)

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
            text="AI Assistant Response", 
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
        
        # Initial welcome message
        welcome_msg = """🤖 OSINT Investigation Assistant Ready!

Available Services:
• Free AI Chat - Basic AI responses for OSINT guidance
• Offline Analysis - Local analysis and keyword extraction  
• Web Search - Search-based intelligent answers

I can help you with:
✓ Investigation methodology planning
✓ Tool selection and recommendations
✓ Best practices and legal considerations
✓ Research strategy development
✓ Case analysis guidance

Ask me anything about OSINT techniques, tools, or methodologies!

Example questions:
• "What's the best approach to investigate a phone number?"
• "How do I safely research dark web activities?"
• "What tools should I use for social media investigation?"
"""
        self.results_textbox.insert("end", welcome_msg)

    def ask_ai(self):
        question = self.question_text.get("1.0", "end").strip()
        service = self.ai_service.get()
        
        if not question or question == "Example: How do I investigate a suspicious email address?":
            self.results_textbox.insert("end", "\n❌ Please enter a specific question about OSINT techniques.\n")
            return

        self.results_textbox.insert("end", f"\n{'='*60}\n")
        self.results_textbox.insert("end", f"🤔 Your Question: {question}\n")
        self.results_textbox.insert("end", f"🤖 Service: {service}\n")
        self.results_textbox.insert("end", f"{'='*60}\n\n")

        if service == "Free AI Chat":
            threading.Thread(target=self.free_ai_response, args=(question,)).start()
        elif service == "Offline Analysis":
            self.offline_analysis(question)
        elif service == "Web Search":
            self.web_search_response(question)

    def free_ai_response(self, question):
        self.results_textbox.insert("end", "🔄 Generating AI response...\n\n")
        
        try:
            response = self.generate_osint_response(question)
            self.results_textbox.insert("end", f"💬 AI Response:\n{response}\n")
        except Exception as e:
            self.results_textbox.insert("end", f"❌ Error: {str(e)}\n")
            self.offline_analysis(question)

    def generate_osint_response(self, question):
        """Generate intelligent OSINT responses based on keywords"""
        question_lower = question.lower()
        
        # Email investigation
        if any(word in question_lower for word in ["email", "e-mail", "mail"]):
            return """📧 EMAIL INVESTIGATION METHODOLOGY:

1. VALIDATION & VERIFICATION:
   • Use email validation services (Hunter.io, NeverBounce)
   • Check if email exists without sending mail
   • Verify domain legitimacy and MX records

2. BREACH & COMPROMISE CHECK:
   • Have I Been Pwned - check for known breaches
   • Dehashed - search leaked databases
   • h8mail tool for automated breach hunting

3. GOOGLE DORKING:
   • site:pastebin.com "email@domain.com"
   • "email@domain.com" filetype:pdf
   • site:linkedin.com "email@domain.com"

4. SOCIAL MEDIA INVESTIGATION:
   • Search email on major platforms
   • Check for associated usernames
   • Look for profile pictures and personal info

5. ASSOCIATED ACCOUNTS:
   • Use email to recover accounts (carefully)
   • Check registration patterns
   • Look for connected social profiles

LEGAL NOTE: Ensure you have authorization before investigating others' emails."""

        # Phone investigation
        elif any(word in question_lower for word in ["phone", "number", "mobile", "cell"]):
            return """📞 PHONE NUMBER INVESTIGATION METHODOLOGY:

1. VALIDATION:
   • NumVerify API for carrier/location info
   • TrueCaller for registered name/details
   • Carrier lookup services

2. REVERSE LOOKUP:
   • WhitePages reverse phone lookup
   • Sync.me social media connections
   • FastPeopleSearch for associated records

3. OSINT TECHNIQUES:
   • Google search with quotes "phone number"
   • Social media platform searches
   • Business directory searches

4. TECHNICAL ANALYSIS:
   • Check for VoIP vs landline vs mobile
   • Identify carrier and region
   • Port history if available

5. SOCIAL ENGINEERING AWARENESS:
   • Never call unknown numbers directly
   • Be aware of callback scams
   • Document all findings properly

LEGAL NOTE: Phone investigation must comply with local privacy laws."""

        # IP investigation  
        elif any(word in question_lower for word in ["ip", "address", "network"]):
            return """🌐 IP ADDRESS INVESTIGATION METHODOLOGY:

1. GEOLOCATION:
   • ip-api.com for basic geo data
   • MaxMind GeoIP databases
   • IPinfo.io for detailed analysis

2. OWNERSHIP & ISP:
   • WHOIS lookup for registration data
   • ARIN/RIPE database searches
   • AS (Autonomous System) information

3. THREAT INTELLIGENCE:
   • VirusTotal for malware associations
   • AbuseIPDB for abuse reports
   • Shodan for open ports/services

4. HISTORICAL DATA:
   • PassiveTotal for DNS history
   • SecurityTrails for domain associations
   • Archive.org for website history

5. NETWORK ANALYSIS:
   • Traceroute for routing path
   • Port scanning (only if authorized)
   • Banner grabbing for service info

LEGAL NOTE: Only scan IPs you own or have explicit permission to test."""

        # Social media investigation
        elif any(word in question_lower for word in ["social", "media", "facebook", "twitter", "instagram"]):
            return """📱 SOCIAL MEDIA INVESTIGATION METHODOLOGY:

1. USERNAME ENUMERATION:
   • Sherlock tool for cross-platform search
   • NameChk for availability checking
   • Manual searches across platforms

2. PROFILE ANALYSIS:
   • Profile pictures reverse image search
   • Bio information extraction
   • Connection/friend list analysis

3. CONTENT ANALYSIS:
   • Timeline analysis for patterns
   • Geolocation from posts/photos
   • Language and behavior patterns

4. METADATA EXTRACTION:
   • EXIF data from uploaded photos
   • Timestamp analysis
   • Device/app information

5. RELATIONSHIP MAPPING:
   • Identify close connections
   • Mutual friends/followers
   • Group memberships

PRIVACY CONSIDERATIONS:
• Respect privacy settings and boundaries
• Only collect publicly available information
• Be aware of terms of service violations"""

        # Cryptocurrency investigation
        elif any(word in question_lower for word in ["bitcoin", "crypto", "blockchain", "wallet"]):
            return """₿ CRYPTOCURRENCY INVESTIGATION METHODOLOGY:

1. BLOCKCHAIN ANALYSIS:
   • Block explorers (Blockchain.info, Blockchair)
   • Transaction history tracing
   • Address clustering analysis

2. ATTRIBUTION TECHNIQUES:
   • Exchange identification
   • Wallet fingerprinting
   • Behavior pattern analysis

3. OSINT TOOLS:
   • Crystal Blockchain for visualization
   • Chainalysis for professional analysis
   • OXT.me for Bitcoin investigation

4. DATA COLLECTION:
   • Transaction amounts and timing
   • Address reuse patterns
   • Mixing service detection

5. REPORTING:
   • Document transaction flows
   • Create visual maps
   • Maintain chain of custody

COMPLIANCE NOTE: Cryptocurrency investigation often requires specialized training and legal authorization."""

        # General OSINT methodology
        elif any(word in question_lower for word in ["osint", "investigation", "research"]):
            return """🔍 GENERAL OSINT METHODOLOGY:

1. PLANNING PHASE:
   • Define investigation objectives
   • Identify target parameters
   • Choose appropriate tools

2. COLLECTION PHASE:
   • Passive information gathering
   • Multiple source verification
   • Document all findings

3. PROCESSING PHASE:
   • Data correlation and analysis
   • Timeline construction
   • Pattern identification

4. ANALYSIS PHASE:
   • Verify information accuracy
   • Identify gaps and inconsistencies
   • Draw evidence-based conclusions

5. REPORTING PHASE:
   • Document methodology used
   • Present findings clearly
   • Maintain evidence integrity

BEST PRACTICES:
• Always use multiple sources for verification
• Maintain detailed investigation logs
• Respect privacy and legal boundaries
• Stay within authorized scope"""

        # Dark web investigation
        elif any(word in question_lower for word in ["dark", "web", "tor", "onion"]):
            return """🕸️ DARK WEB INVESTIGATION METHODOLOGY:

1. SAFETY PREPARATION:
   • Use secure, isolated environment
   • VPN + Tor for anonymity layers
   • Never download unknown files

2. ACCESS METHODS:
   • Tor browser properly configured
   • Tails OS for maximum security
   • Never use real identity/accounts

3. INVESTIGATION TECHNIQUES:
   • Directory searches (DuckDuckGo onion)
   • Known marketplace monitoring
   • Forum and community analysis

4. DATA COLLECTION:
   • Screenshot everything (no downloads)
   • Document timestamps and URLs
   • Note vendor/user information

5. ANALYSIS:
   • Cross-reference with surface web
   • Track cryptocurrency transactions
   • Monitor for data breaches

CRITICAL WARNINGS:
• Only for legitimate security/law enforcement purposes
• Many activities are illegal to access or participate in
• Requires proper legal authorization
• Extreme security precautions necessary"""

        # Default response
        else:
            return f"""🤖 OSINT GUIDANCE FOR YOUR QUESTION:

Your question: "{question}"

GENERAL APPROACH:
1. Break down your investigation into specific components
2. Start with passive information gathering
3. Use multiple sources for verification
4. Document your methodology and findings

RECOMMENDED FIRST STEPS:
• Clearly define what you're investigating
• Identify the type of information you need
• Choose appropriate tools and techniques
• Ensure you have proper authorization

COMMON OSINT CATEGORIES:
• People investigation (social media, public records)
• Technical investigation (IP, domains, infrastructure)
• Digital forensics (images, documents, metadata)
• Financial investigation (cryptocurrency, transactions)

Would you like me to provide specific guidance for any of these areas?

IMPORTANT REMINDERS:
• Only investigate what you're authorized to research
• Respect privacy laws and platform terms of service
• Verify information through multiple independent sources
• Maintain detailed documentation of your process"""

    def offline_analysis(self, question):
        self.results_textbox.insert("end", "🔍 Performing offline analysis...\n\n")
        
        # Keyword analysis
        osint_keywords = {
            "investigation": ["methodology", "planning", "documentation"],
            "social": ["media", "profiles", "usernames", "connections"],
            "email": ["validation", "breaches", "dorking", "verification"],
            "phone": ["lookup", "carrier", "validation", "reverse search"],
            "ip": ["geolocation", "whois", "threat intelligence", "scanning"],
            "crypto": ["blockchain", "transactions", "wallets", "attribution"],
            "dark web": ["tor", "anonymity", "safety", "monitoring"],
            "osint": ["sources", "verification", "tools", "techniques"]
        }
        
        question_lower = question.lower()
        found_topics = []
        
        for topic, related_words in osint_keywords.items():
            if topic in question_lower or any(word in question_lower for word in related_words):
                found_topics.append(topic)
        
        self.results_textbox.insert("end", f"📊 Offline Analysis Results:\n")
        self.results_textbox.insert("end", f"• Question length: {len(question)} characters\n")
        self.results_textbox.insert("end", f"• Word count: {len(question.split())} words\n")
        self.results_textbox.insert("end", f"• Detected OSINT topics: {', '.join(found_topics) if found_topics else 'General inquiry'}\n\n")
        
        if found_topics:
            self.results_textbox.insert("end", f"💡 Recommended investigation approaches:\n")
            for topic in found_topics:
                if topic == "email":
                    self.results_textbox.insert("end", "• Email investigation: validation, breach checking, OSINT searches\n")
                elif topic == "social":
                    self.results_textbox.insert("end", "• Social media investigation: profile analysis, username enumeration\n")
                elif topic == "ip":
                    self.results_textbox.insert("end", "• IP investigation: geolocation, threat intelligence, network analysis\n")
                elif topic == "crypto":
                    self.results_textbox.insert("end", "• Cryptocurrency investigation: blockchain analysis, transaction tracing\n")

    def web_search_response(self, question):
        self.results_textbox.insert("end", "🔍 Generating web search guidance...\n\n")
        
        search_query = urllib.parse.quote(f"{question} OSINT methodology guide")
        search_url = f"https://www.google.com/search?q={search_query}"
        
        self.results_textbox.insert("end", f"🌐 Recommended Web Searches:\n")
        self.results_textbox.insert("end", f"Primary Query: {question} OSINT methodology\n")
        self.results_textbox.insert("end", f"Search URL: {search_url}\n\n")
        
        self.results_textbox.insert("end", "💡 Additional search suggestions:\n")
        suggestions = [
            f'"{question}" investigation guide',
            f'"{question}" OSINT techniques',
            f'"{question}" cyber investigation',
            f'"{question}" digital forensics',
            f'"{question}" security research'
        ]
        
        for suggestion in suggestions:
            self.results_textbox.insert("end", f"• {suggestion}\n")
        
        self.results_textbox.insert("end", f"\n🔗 Recommended Resources:\n")
        self.results_textbox.insert("end", "• OSINT Framework (osintframework.com)\n")
        self.results_textbox.insert("end", "• Bellingcat's Online Investigation Toolkit\n")
        self.results_textbox.insert("end", "• SANS Digital Forensics resources\n")

    def clear_all(self):
        self.question_text.delete("1.0", "end")
        self.question_text.insert("1.0", "Example: How do I investigate a suspicious email address?")
        self.results_textbox.delete("1.0", "end")
        
        welcome_msg = """🤖 Chat cleared! Ask me anything about OSINT techniques.

I'm ready to help with:
• Investigation methodology
• Tool recommendations  
• Best practices guidance
• Legal and ethical considerations
"""
        self.results_textbox.insert("end", welcome_msg)

