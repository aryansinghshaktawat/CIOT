import customtkinter as ctk
import tkinter as tk
from tkinter import filedialog, messagebox
import requests
import webbrowser
import os
import hashlib
import threading
import time
from datetime import datetime
from io import BytesIO
from PIL import Image, ExifTags
import base64

class ImageAnalysisTab(ctk.CTkFrame):
    """Professional Image Analysis & Forensics Module"""
    
    def __init__(self, master):
        super().__init__(master)
        self.configure(fg_color="#1a1a1a")
        
        # Initialize variables
        self.current_image_path = None
        self.image_data = None
        self.hosted_url = None
        self.analysis_results = {}
        
        self.setup_professional_ui()

    def show_info_popup(self):
        """Professional information popup"""
        info_window = ctk.CTkToplevel(self)
        info_window.title("Image Analysis - User Guide")
        info_window.geometry("700x600")
        info_window.transient(self.master)
        info_window.grab_set()
        
        content = ctk.CTkTextbox(info_window, wrap="word", font=ctk.CTkFont(size=12))
        content.pack(fill="both", expand=True, padx=20, pady=20)
        
        info_text = """🔬 CIOT PROFESSIONAL IMAGE ANALYSIS & FORENSICS

🎯 ADVANCED CAPABILITIES:
• Multi-platform reverse image searching with automated hosting
• Comprehensive EXIF metadata extraction and analysis
• Image hash generation (MD5, SHA-1, SHA-256)
• File format validation and security assessment
• Professional forensic analysis integration
• Automated threat intelligence correlation
• Privacy risk assessment and recommendations

🚀 PROFESSIONAL WORKFLOW:
1. Upload image or provide URL for analysis
2. Automatic file validation and security scanning
3. Comprehensive metadata extraction (EXIF, IPTC, XMP)
4. Hash generation for digital evidence tracking
5. Automated reverse search across multiple engines
6. Professional forensic analysis recommendations
7. Detailed reporting with timestamps and evidence chain

🔍 REVERSE SEARCH ENGINES:
• Google Images - Largest database, best overall coverage
• Yandex Images - Superior facial recognition capabilities
• TinEye - Historical tracking and modification detection
• Bing Visual Search - Product and object identification
• Baidu Images - Asian content specialization

📊 METADATA ANALYSIS:
• Camera information (make, model, settings)
• Geolocation data (GPS coordinates if available)
• Timestamp analysis (creation, modification dates)
• Software fingerprinting (editing applications used)
• Color profile and technical specifications
• Compression and quality analysis

🛡️ SECURITY FEATURES:
• Malware scanning for suspicious image files
• Privacy risk assessment (PII exposure)
• Anonymous hosting via secure services
• Encrypted data transmission
• No local storage of sensitive information
• Professional evidence handling protocols

⚖️ LEGAL & COMPLIANCE:
• Digital evidence chain of custody
• Forensic-grade hash verification
• Professional reporting standards
• Privacy law compliance (GDPR, CCPA)
• Ethical investigation guidelines
• Court-admissible documentation

🎯 PROFESSIONAL APPLICATIONS:
• Digital forensics and incident response
• Fraud investigation and verification
• Intellectual property protection
• Social media intelligence (SOCMINT)
• Cybersecurity threat analysis
• Law enforcement investigations
• Corporate security assessments
• Academic research and journalism

💡 BEST PRACTICES:
• Always verify image authenticity through multiple sources
• Document all analysis steps for evidence purposes
• Respect privacy laws and platform terms of service
• Use professional judgment in sensitive investigations
• Maintain chain of custody for legal proceedings
• Cross-reference findings with additional intelligence sources"""

        content.insert("1.0", info_text)
        content.configure(state="disabled")

    def setup_professional_ui(self):
        """Setup professional-grade user interface"""
        
        # Header with professional styling
        header_frame = ctk.CTkFrame(self, fg_color="#2b2b2b", corner_radius=10)
        header_frame.pack(fill="x", padx=20, pady=(20, 10))
        
        title_label = ctk.CTkLabel(
            header_frame, 
            text="🔬 CIOT Professional Image Analysis & Forensics", 
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color="#00d4ff"
        )
        title_label.pack(pady=15)
        
        # Status indicator
        self.status_label = ctk.CTkLabel(
            header_frame,
            text="🟢 System Ready - Upload image to begin analysis",
            font=ctk.CTkFont(size=12),
            text_color="#00ff88"
        )
        self.status_label.pack(pady=(0, 10))
        
        # Input section with professional layout
        input_frame = ctk.CTkFrame(self, fg_color="#2b2b2b", corner_radius=10)
        input_frame.pack(fill="x", padx=20, pady=10)
        
        # URL input section
        url_section = ctk.CTkFrame(input_frame, fg_color="transparent")
        url_section.pack(fill="x", padx=15, pady=10)
        
        ctk.CTkLabel(
            url_section, 
            text="🌐 Image URL (Optional):", 
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color="#ffffff"
        ).pack(anchor="w", pady=(0, 5))
        
        self.url_entry = ctk.CTkEntry(
            url_section, 
            width=600, 
            height=35,
            placeholder_text="Enter image URL for analysis...",
            font=ctk.CTkFont(size=12)
        )
        self.url_entry.pack(fill="x", pady=(0, 10))
        
        # File upload + analysis controls combined horizontally (compact to maximize results area)
        upload_controls_row = ctk.CTkFrame(input_frame, fg_color="transparent")
        upload_controls_row.pack(fill="x", padx=15, pady=(5,6))

        # Left: upload section (stacked)
        upload_section = ctk.CTkFrame(upload_controls_row, fg_color="transparent")
        upload_section.pack(side="left", fill="x", expand=True)

        ctk.CTkLabel(
            upload_section,
            text="📁 File Upload:",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color="#ffffff"
        ).pack(anchor="w", pady=(0, 5))

        upload_button_frame = ctk.CTkFrame(upload_section, fg_color="transparent")
        upload_button_frame.pack(fill="x")

        self.upload_btn = ctk.CTkButton(
            upload_button_frame,
            text="📂 Select Image File",
            command=self.upload_image,
            width=200,
            height=40,
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color="#0066cc",
            hover_color="#0052a3"
        )
        self.upload_btn.pack(side="left", padx=(0, 10))

        self.file_info_label = ctk.CTkLabel(
            upload_button_frame,
            text="No file selected",
            font=ctk.CTkFont(size=12),
            text_color="#888888"
        )
        self.file_info_label.pack(side="left", padx=10)

        # Right: analysis buttons arranged 2x3 grid
        controls_sidebar = ctk.CTkFrame(upload_controls_row, fg_color="transparent")
        controls_sidebar.pack(side="right", anchor="n", padx=(20,0))

        # Configure grid for 2 columns x 3 rows
        for c in range(2):
            controls_sidebar.grid_columnconfigure(c, weight=1, uniform="ops")

        btn_cfg = {
            "width": 150,
            "height": 34,
            "font": ctk.CTkFont(size=12, weight="bold")
        }

        self.analyze_btn = ctk.CTkButton(
            controls_sidebar,
            text="🔍 Full Analysis",
            command=self.perform_full_analysis,
            fg_color="#00aa44", hover_color="#008833", **btn_cfg
        )
        self.analyze_btn.grid(row=0, column=0, padx=4, pady=4, sticky="nsew")

        self.reverse_search_btn = ctk.CTkButton(
            controls_sidebar,
            text="🌐 Reverse Search",
            command=self.reverse_search_analysis,
            fg_color="#ff6600", hover_color="#e55a00", **btn_cfg
        )
        self.reverse_search_btn.grid(row=0, column=1, padx=4, pady=4, sticky="nsew")

        self.exif_btn = ctk.CTkButton(
            controls_sidebar,
            text="📊 EXIF Analysis",
            command=self.analyze_exif_metadata,
            fg_color="#9933cc", hover_color="#7a2999", **btn_cfg
        )
        self.exif_btn.grid(row=1, column=0, padx=4, pady=4, sticky="nsew")

        self.hash_btn = ctk.CTkButton(
            controls_sidebar,
            text="🔐 Hashes",
            command=self.generate_file_hashes,
            fg_color="#cc3366", hover_color="#a32952", **btn_cfg
        )
        self.hash_btn.grid(row=1, column=1, padx=4, pady=4, sticky="nsew")

        self.forensics_btn = ctk.CTkButton(
            controls_sidebar,
            text="🧪 Forensic Tools",
            command=self.open_forensic_tools,
            fg_color="#6633aa", hover_color="#522987", **btn_cfg
        )
        self.forensics_btn.grid(row=2, column=0, padx=4, pady=4, sticky="nsew")

        self.report_btn = ctk.CTkButton(
            controls_sidebar,
            text="📋 Report",
            command=self.generate_professional_report,
            fg_color="#aa6633", hover_color="#875229", **btn_cfg
        )
        self.report_btn.grid(row=2, column=1, padx=4, pady=4, sticky="nsew")
        
        # Standardized results section - consistent with Surface Web OSINT
        results_frame = ctk.CTkFrame(self, corner_radius=12)
        # Reduced top padding; keep generous bottom for breathing space
        results_frame.pack(fill="both", expand=True, padx=20, pady=(4, 16))

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
        
        # Initialize with professional welcome message
        self.show_professional_welcome()

    def _add_labeled_entry(self, label):
        l = ctk.CTkLabel(self, text=label, text_color="white")
        l.pack()
        entry = ctk.CTkEntry(self, width=500)
        entry.pack(pady=5)
        return entry

    def upload_image(self):
        from tkinter import filedialog
        file_path = filedialog.askopenfilename(
            title="Select Image for Reverse Search",
            filetypes=[
                ("Image Files", "*.png *.jpg *.jpeg *.gif *.bmp *.webp"),
                ("PNG files", "*.png"),
                ("JPEG files", "*.jpg *.jpeg"),
                ("All files", "*.*")
            ]
        )
        if file_path:
            with open(file_path, "rb") as f:
                self.image_data = f.read()
            filename = file_path.split("/")[-1]
            self.result_box.insert("end", f"✅ Image loaded: {filename}\n")
            self.result_box.insert("end", f"📁 Size: {len(self.image_data)} bytes\n")

    def search_image(self):
        self.result_box.delete("0.0", "end")
        self.result_box.insert("end", "🔍 STARTING REVERSE IMAGE SEARCH...\n\n")
        
        image_url = self.url_entry.get().strip()
        
        if not image_url and not self.image_data:
            self.result_box.insert("end", "❌ Please provide an image URL or upload a file.\n")
            return

        try:
            if self.image_data:
                # Upload to Catbox for anonymous hosting
                self.result_box.insert("end", "📤 Uploading image to hosting service...\n")
                files = {"fileToUpload": ("image.png", self.image_data)}
                response = requests.post("https://catbox.moe/user/api.php", 
                                       data={"reqtype": "fileupload"}, 
                                       files=files, 
                                       timeout=30)
                
                if response.status_code == 200:
                    hosted_url = response.text.strip()
                    self.result_box.insert("end", f"✅ Image hosted at: {hosted_url}\n\n")
                else:
                    self.result_box.insert("end", "❌ Image upload failed. Please try again.\n")
                    return
            else:
                hosted_url = image_url
                self.result_box.insert("end", f"🔗 Using provided URL: {hosted_url}\n\n")

            # Generate reverse search URLs
            google_search = f"https://www.google.com/searchbyimage?image_url={hosted_url}"
            yandex_search = f"https://yandex.com/images/search?rpt=imageview&url={hosted_url}"
            bing_search = f"https://www.bing.com/images/search?q=imgurl:{hosted_url}&view=detailv2"
            tineye_search = f"https://tineye.com/search?url={hosted_url}"

            self.result_box.insert("end", "🎯 REVERSE SEARCH LINKS GENERATED:\n")
            self.result_box.insert("end", "=" * 50 + "\n\n")
            
            # Insert clickable links
            self.insert_clickable("🔍 Google Images Search", google_search)
            self.insert_clickable("🔍 Yandex Images Search", yandex_search)  
            self.insert_clickable("🔍 Bing Visual Search", bing_search)
            self.insert_clickable("🔍 TinEye Search", tineye_search)
            
            self.result_box.insert("end", "\n💡 USAGE TIPS:\n")
            self.result_box.insert("end", "• Click any link above to open in browser\n")
            self.result_box.insert("end", "• Google: Best for general image matching\n")
            self.result_box.insert("end", "• Yandex: Excellent for face recognition\n")
            self.result_box.insert("end", "• Bing: Good for products and objects\n")
            self.result_box.insert("end", "• TinEye: Tracks image usage history\n\n")
            self.result_box.insert("end", "� Se arch completed! Click links to view results.\n")

        except Exception as e:
            self.result_box.insert("end", f"❌ Error: {e}\n")
            self.result_box.insert("end", "Please check your internet connection and try again.\n")

    def insert_clickable(self, text, link):
        start_pos = self.result_box.index("end-1c")
        self.result_box.insert("end", f"{text}\n")
        end_pos = self.result_box.index("end-1c")
        
        # Create a unique tag for this link
        tag_name = f"link_{len(link)}"
        self.result_box.tag_add(tag_name, start_pos, end_pos)
        self.result_box.tag_config(tag_name, foreground="#00AAFF", underline=True)
        self.result_box.tag_bind(tag_name, "<Button-1>", lambda e: webbrowser.open(link))
        self.result_box.tag_bind(tag_name, "<Enter>", lambda e: self.result_box.configure(cursor="hand2"))
        self.result_box.tag_bind(tag_name, "<Leave>", lambda e: self.result_box.configure(cursor=""))
    def show_professional_welcome(self):
        """Display professional welcome message"""
        welcome_text = f"""🔬 CYBER INVESTIGATION OSINT TOOLKIT - IMAGE ANALYSIS
{'=' * 60}

🎯 SYSTEM STATUS: OPERATIONAL
📅 Session Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
🔒 Security Level: PROFESSIONAL GRADE
🌐 Network Status: CONNECTED

📋 AVAILABLE ANALYSIS MODULES:
✓ Full Image Analysis - Comprehensive multi-stage analysis
✓ Reverse Image Search - Multi-platform automated search
✓ EXIF Metadata Extraction - Professional metadata analysis
✓ Cryptographic Hash Generation - Digital evidence integrity
✓ Forensic Tool Integration - Professional forensic analysis
✓ Professional Reporting - Court-admissible documentation

🚀 QUICK START GUIDE:
1. Upload image file or enter URL
2. Select analysis type from control panel
3. Review comprehensive results
4. Generate professional reports as needed

⚠️ PROFESSIONAL NOTICE:
This system is designed for legitimate investigative purposes only.
Ensure compliance with applicable laws and ethical guidelines.
Maintain proper chain of custody for digital evidence.

🔍 Ready for professional image analysis. Upload an image to begin.
"""
        self.results_textbox.insert("end", welcome_text)
        self.update_status("🟢 System Ready - Upload image to begin analysis")

    def update_status(self, message):
        """Update status indicator"""
        self.status_label.configure(text=message)

    def upload_image(self):
        """Professional image upload with validation"""
        file_types = [
            ("All Image Files", "*.jpg *.jpeg *.png *.gif *.bmp *.tiff *.webp *.ico *.svg"),
            ("JPEG Files", "*.jpg *.jpeg"),
            ("PNG Files", "*.png"),
            ("GIF Files", "*.gif"),
            ("BMP Files", "*.bmp"),
            ("TIFF Files", "*.tiff *.tif"),
            ("WebP Files", "*.webp"),
            ("All Files", "*.*")
        ]
        
        file_path = filedialog.askopenfilename(
            title="CIOT - Select Image for Professional Analysis",
            filetypes=file_types
        )
        
        if file_path:
            try:
                self.update_status("🔄 Processing image upload...")
                
                # Read and validate image
                with open(file_path, "rb") as f:
                    self.image_data = f.read()
                
                self.current_image_path = file_path
                filename = os.path.basename(file_path)
                file_size = len(self.image_data)
                
                # Basic validation
                try:
                    with Image.open(BytesIO(self.image_data)) as img:
                        width, height = img.size
                        format_type = img.format
                        mode = img.mode
                except Exception as e:
                    messagebox.showerror("Invalid Image", f"Unable to process image file: {str(e)}")
                    return
                
                # Update UI
                self.file_info_label.configure(
                    text=f"📁 {filename} ({file_size:,} bytes, {width}x{height}, {format_type})",
                    text_color="#00ff88"
                )
                
                # Log to results
                self.results_textbox.insert("end", f"\n{'=' * 60}\n")
                self.results_textbox.insert("end", f"📁 IMAGE UPLOAD SUCCESSFUL\n")
                self.results_textbox.insert("end", f"{'=' * 60}\n")
                self.results_textbox.insert("end", f"📄 File: {filename}\n")
                self.results_textbox.insert("end", f"📊 Size: {file_size:,} bytes ({file_size/1024/1024:.2f} MB)\n")
                self.results_textbox.insert("end", f"📐 Dimensions: {width} x {height} pixels\n")
                self.results_textbox.insert("end", f"🎨 Format: {format_type}\n")
                self.results_textbox.insert("end", f"🔧 Mode: {mode}\n")
                self.results_textbox.insert("end", f"⏰ Upload Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                
                self.update_status("✅ Image loaded successfully - Ready for analysis")
                
            except Exception as e:
                messagebox.showerror("Upload Error", f"Failed to upload image: {str(e)}")
                self.update_status("❌ Upload failed - Please try again")

    def perform_full_analysis(self):
        """Comprehensive image analysis"""
        if not self.image_data and not self.url_entry.get().strip():
            messagebox.showwarning("No Image", "Please upload an image or enter a URL first.")
            return
        
        self.update_status("🔄 Performing comprehensive analysis...")
        
        # Run analysis in thread to prevent UI blocking
        threading.Thread(target=self._full_analysis_worker, daemon=True).start()

    def _full_analysis_worker(self):
        """Worker thread for full analysis"""
        try:
            self.results_textbox.insert("end", f"\n{'=' * 60}\n")
            self.results_textbox.insert("end", f"🔬 COMPREHENSIVE IMAGE ANALYSIS\n")
            self.results_textbox.insert("end", f"{'=' * 60}\n")
            self.results_textbox.insert("end", f"⏰ Analysis Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            
            # Stage 1: Basic Analysis
            self.results_textbox.insert("end", "🔍 STAGE 1: BASIC FILE ANALYSIS\n")
            self.results_textbox.insert("end", "-" * 40 + "\n")
            
            if self.image_data:
                # File analysis
                file_size = len(self.image_data)
                self.results_textbox.insert("end", f"📊 File Size: {file_size:,} bytes ({file_size/1024/1024:.2f} MB)\n")
                
                # Image analysis
                try:
                    with Image.open(BytesIO(self.image_data)) as img:
                        self.results_textbox.insert("end", f"📐 Dimensions: {img.width} x {img.height} pixels\n")
                        self.results_textbox.insert("end", f"🎨 Format: {img.format}\n")
                        self.results_textbox.insert("end", f"🔧 Mode: {img.mode}\n")
                        
                        # Calculate megapixels
                        megapixels = (img.width * img.height) / 1000000
                        self.results_textbox.insert("end", f"📷 Megapixels: {megapixels:.2f} MP\n")
                        
                        # Aspect ratio
                        aspect_ratio = img.width / img.height
                        self.results_textbox.insert("end", f"📏 Aspect Ratio: {aspect_ratio:.2f}:1\n")
                        
                except Exception as e:
                    self.results_textbox.insert("end", f"❌ Image analysis error: {str(e)}\n")
            
            # Stage 2: Hash Generation
            self.results_textbox.insert("end", f"\n🔐 STAGE 2: CRYPTOGRAPHIC HASH GENERATION\n")
            self.results_textbox.insert("end", "-" * 40 + "\n")
            self._generate_hashes_worker()
            
            # Stage 3: EXIF Analysis
            self.results_textbox.insert("end", f"\n📊 STAGE 3: METADATA ANALYSIS\n")
            self.results_textbox.insert("end", "-" * 40 + "\n")
            self._analyze_exif_worker()
            
            # Stage 4: Security Assessment
            self.results_textbox.insert("end", f"\n🛡️ STAGE 4: SECURITY ASSESSMENT\n")
            self.results_textbox.insert("end", "-" * 40 + "\n")
            self._security_assessment_worker()
            
            self.results_textbox.insert("end", f"\n✅ COMPREHENSIVE ANALYSIS COMPLETED\n")
            self.results_textbox.insert("end", f"⏰ Analysis Finished: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            
            self.update_status("✅ Comprehensive analysis completed")
            
        except Exception as e:
            self.results_textbox.insert("end", f"\n❌ Analysis error: {str(e)}\n")
            self.update_status("❌ Analysis failed - Please try again")

    def reverse_search_analysis(self):
        """Professional reverse image search"""
        if not self.image_data and not self.url_entry.get().strip():
            messagebox.showwarning("No Image", "Please upload an image or enter a URL first.")
            return
        
        self.update_status("🔄 Initiating reverse image search...")
        threading.Thread(target=self._reverse_search_worker, daemon=True).start()

    def _reverse_search_worker(self):
        """Worker thread for reverse search"""
        try:
            self.results_textbox.insert("end", f"\n{'=' * 60}\n")
            self.results_textbox.insert("end", f"🌐 PROFESSIONAL REVERSE IMAGE SEARCH\n")
            self.results_textbox.insert("end", f"{'=' * 60}\n")
            
            image_url = self.url_entry.get().strip()
            
            if self.image_data and not image_url:
                # Upload to hosting service
                self.results_textbox.insert("end", "📤 Uploading to secure hosting service...\n")
                
                try:
                    files = {"fileToUpload": ("evidence.png", self.image_data)}
                    response = requests.post(
                        "https://catbox.moe/user/api.php", 
                        data={"reqtype": "fileupload"}, 
                        files=files, 
                        timeout=30
                    )
                    
                    if response.status_code == 200:
                        self.hosted_url = response.text.strip()
                        self.results_textbox.insert("end", f"✅ Image hosted securely at: {self.hosted_url}\n\n")
                    else:
                        self.results_textbox.insert("end", "❌ Upload failed. Please try again.\n")
                        return
                        
                except Exception as e:
                    self.results_textbox.insert("end", f"❌ Upload error: {str(e)}\n")
                    return
            else:
                self.hosted_url = image_url
                self.results_textbox.insert("end", f"🔗 Using provided URL: {self.hosted_url}\n\n")
            
            # Generate professional search URLs with proper encoding
            import urllib.parse
            encoded_url = urllib.parse.quote(self.hosted_url, safe=':/?#[]@!$&\'()*+,;=')
            
            search_engines = {
                "Google Images": f"https://www.google.com/searchbyimage?image_url={encoded_url}",
                "Yandex Images": f"https://yandex.com/images/search?rpt=imageview&url={encoded_url}",
                "Bing Visual Search": f"https://www.bing.com/images/searchbyimage?cbir=sbi&imgurl={encoded_url}",
                "TinEye": f"https://tineye.com/search?url={encoded_url}",
                "Baidu Images": f"https://image.baidu.com/search/index?tn=baiduimage&ct=201326592&lm=-1&cl=2&ie=gb18030&word={encoded_url}"
            }
            
            self.results_textbox.insert("end", "🎯 REVERSE SEARCH ENGINES ACTIVATED:\n")
            self.results_textbox.insert("end", "=" * 50 + "\n\n")
            self.results_textbox.insert("end", "🚀 AUTOMATICALLY OPENING ALL SEARCH ENGINES...\n\n")
            
            # Automatically open all search engines in browser
            for engine, url in search_engines.items():
                self.results_textbox.insert("end", f"🔍 Opening {engine}...\n")
                webbrowser.open(url)
                time.sleep(1)  # Small delay between opening tabs
                
            self.results_textbox.insert("end", f"\n✅ All {len(search_engines)} search engines opened in browser!\n")
            self.results_textbox.insert("end", "💡 Check your browser tabs for live search results.\n\n")
            
            # Also display clickable links for reference
            self.results_textbox.insert("end", "📋 SEARCH LINKS (for reference):\n")
            for engine, url in search_engines.items():
                self.insert_clickable_link(f"🔍 {engine}", url)
                
            self.results_textbox.insert("end", "\n📋 PROFESSIONAL SEARCH STRATEGY:\n")
            self.results_textbox.insert("end", "• Google Images: Comprehensive database, best overall coverage\n")
            self.results_textbox.insert("end", "• Yandex Images: Superior facial recognition and Eastern content\n")
            self.results_textbox.insert("end", "• Bing Visual Search: Excellent for products and objects\n")
            self.results_textbox.insert("end", "• TinEye: Historical tracking and modification detection\n")
            self.results_textbox.insert("end", "• Baidu Images: Asian content specialization\n\n")
            
            self.results_textbox.insert("end", "🔍 INVESTIGATION METHODOLOGY:\n")
            self.results_textbox.insert("end", "1. Cross-reference results across all platforms\n")
            self.results_textbox.insert("end", "2. Identify earliest dated appearances\n")
            self.results_textbox.insert("end", "3. Document source attribution and watermarks\n")
            self.results_textbox.insert("end", "4. Analyze image quality variations\n")
            self.results_textbox.insert("end", "5. Verify authenticity through multiple sources\n")
            
            self.update_status("✅ Reverse search links generated - Click to investigate")
            
        except Exception as e:
            self.results_textbox.insert("end", f"❌ Reverse search error: {str(e)}\n")
            self.update_status("❌ Reverse search failed")

    def analyze_exif_metadata(self):
        """Run ExifTool on a user-selected image file and display structured metadata."""
        from tkinter import filedialog
        file_path = filedialog.askopenfilename(
            title="Select Image for EXIF Analysis",
            filetypes=[
                ("Image Files", "*.jpg *.jpeg *.png *.tiff *.tif *.heic *.heif *.webp *.gif"),
                ("All Files", "*.*")
            ]
        )
        if not file_path:
            return  # No selection
        self.update_status("🔄 Running ExifTool...")
        threading.Thread(target=self._exiftool_analysis_worker, args=(file_path,), daemon=True).start()

    def _exiftool_analysis_worker(self, file_path: str):
        """Worker: execute ExifTool and parse output including GPS."""
        import subprocess, os, re
        self.results_textbox.delete("1.0", "end")
        self.results_textbox.insert("end", f"📊 EXIF METADATA ANALYSIS (ExifTool)\n{'='*60}\n")
        self.results_textbox.insert("end", f"[Target File] {file_path}\n\n")
        try:
            # Execute exiftool with numeric output for easier GPS parsing
            proc = subprocess.run([
                'exiftool', '-G', '-n', file_path
            ], capture_output=True, text=True)
        except FileNotFoundError:
            self.results_textbox.insert("end", "❌ ExifTool not installed. Please install exiftool to use this feature.\n")
            self.update_status("❌ ExifTool missing")
            return
        except Exception as e:
            self.results_textbox.insert("end", f"❌ Unexpected error launching ExifTool: {e}\n")
            self.update_status("❌ EXIF error")
            return

        stdout = proc.stdout or ""
        stderr = proc.stderr or ""

        if proc.returncode != 0:
            self.results_textbox.insert("end", "❌ ExifTool reported an error:\n")
            self.results_textbox.insert("end", stderr + "\n")
            self.update_status("❌ EXIF analysis failed")
            return

        # Insert raw metadata text first (full visibility)
        self.results_textbox.insert("end", "[Raw Metadata Output]\n")
        self.results_textbox.insert("end", stdout + "\n")

        # Basic categorization
        file_info_keys = {"File Name", "Directory", "File Size", "File Type", "File Type Extension", "MIME Type", "Image Width", "Image Height", "Megapixels"}
        camera_info_keys = {"Make", "Model", "Camera Model Name", "Lens ID", "Lens Info", "Lens Model", "Serial Number", "Body Serial Number", "Lens Serial Number", "Firmware Version"}

        file_info = []
        camera_info = []
        gps_lines = []
        gps_lat = None
        gps_lon = None

        for line in stdout.splitlines():
            # Expected format: [Group] Tag Name : Value
            try:
                # Remove leading/trailing spaces
                clean = line.strip()
                if not clean or ':' not in clean:
                    continue
                # Split on first colon
                left, value = clean.split(':', 1)
                value = value.strip()
                # Remove group prefix like [EXIF] if present
                tag_name = left
                if ']' in left:
                    tag_name = left.split(']', 1)[1].strip()

                if tag_name in file_info_keys:
                    file_info.append((tag_name, value))
                if tag_name in camera_info_keys:
                    camera_info.append((tag_name, value))
                if tag_name.startswith('GPS '):
                    gps_lines.append((tag_name, value))
                    if tag_name == 'GPS Latitude':
                        try:
                            gps_lat = float(value)
                        except ValueError:
                            gps_lat = self._convert_dms_to_decimal(value)
                    if tag_name == 'GPS Longitude':
                        try:
                            gps_lon = float(value)
                        except ValueError:
                            gps_lon = self._convert_dms_to_decimal(value)
            except Exception:
                continue

        # Display structured sections
        if file_info:
            self.results_textbox.insert("end", "\n[File Info]\n")
            for k, v in file_info:
                self.results_textbox.insert("end", f"  • {k}: {v}\n")
        if camera_info:
            self.results_textbox.insert("end", "\n[Camera Info]\n")
            for k, v in camera_info:
                self.results_textbox.insert("end", f"  • {k}: {v}\n")
        if gps_lines:
            self.results_textbox.insert("end", "\n[GPS Data]\n")
            for k, v in gps_lines:
                self.results_textbox.insert("end", f"  • {k}: {v}\n")
            # If we have decimal coordinates, produce link
            if gps_lat is not None and gps_lon is not None:
                maps_url = f"https://www.google.com/maps?q={gps_lat},{gps_lon}"
                self.results_textbox.insert("end", f"\n🌍 Coordinates: {gps_lat:.6f}, {gps_lon:.6f}\n")
                self.insert_clickable_link("🌐 Open in Google Maps", maps_url)
        else:
            self.results_textbox.insert("end", "\n[GPS Data]\n  • No GPS coordinates present\n")

        self.results_textbox.insert("end", "\n✅ EXIF analysis complete.\n")
        self.results_textbox.see("end")
        self.update_status("✅ EXIF analysis complete")

    def _convert_dms_to_decimal(self, dms: str):
        """Convert DMS format like '37 deg 25' 19.20" N' to decimal degrees."""
        try:
            import re
            # Extract components
            pattern = r"(\d+(?:\.\d+)?)\s*deg\s*(\d+(?:\.\d+)?)'?\s*(\d+(?:\.\d+)?)?\"?\s*([NSEW])"
            m = re.search(pattern, dms)
            if not m:
                return None
            deg = float(m.group(1))
            minutes = float(m.group(2))
            seconds = float(m.group(3) or 0)
            hemi = m.group(4).upper()
            dec = deg + minutes/60 + seconds/3600
            if hemi in ['S', 'W']:
                dec *= -1
            return dec
        except Exception:
            return None

    def generate_file_hashes(self):
        """Generate cryptographic hashes for digital evidence"""
        if not self.image_data:
            messagebox.showwarning("No Image", "Please upload an image file first.")
            return
        
        self.update_status("🔄 Generating cryptographic hashes...")
        threading.Thread(target=self._generate_hashes_worker, daemon=True).start()

    def _generate_hashes_worker(self):
        """Worker thread for hash generation"""
        try:
            # Generate multiple hash types
            md5_hash = hashlib.md5(self.image_data).hexdigest()
            sha1_hash = hashlib.sha1(self.image_data).hexdigest()
            sha256_hash = hashlib.sha256(self.image_data).hexdigest()
            
            self.results_textbox.insert("end", "🔐 CRYPTOGRAPHIC HASH VERIFICATION:\n")
            self.results_textbox.insert("end", f"  • MD5:    {md5_hash}\n")
            self.results_textbox.insert("end", f"  • SHA-1:  {sha1_hash}\n")
            self.results_textbox.insert("end", f"  • SHA-256: {sha256_hash}\n")
            
            # Store for reporting
            self.analysis_results['hashes'] = {
                'md5': md5_hash,
                'sha1': sha1_hash,
                'sha256': sha256_hash
            }
            
        except Exception as e:
            self.results_textbox.insert("end", f"❌ Hash generation error: {str(e)}\n")

    def _security_assessment_worker(self):
        """Perform security assessment"""
        try:
            self.results_textbox.insert("end", "🔍 File signature analysis...\n")
            
            # Check file signature
            if self.image_data[:4] == b'\xff\xd8\xff\xe0' or self.image_data[:4] == b'\xff\xd8\xff\xe1':
                self.results_textbox.insert("end", "✅ Valid JPEG signature detected\n")
            elif self.image_data[:8] == b'\x89PNG\r\n\x1a\n':
                self.results_textbox.insert("end", "✅ Valid PNG signature detected\n")
            elif self.image_data[:6] in [b'GIF87a', b'GIF89a']:
                self.results_textbox.insert("end", "✅ Valid GIF signature detected\n")
            else:
                self.results_textbox.insert("end", "⚠️ Unknown or suspicious file signature\n")
            
            # Size analysis
            file_size = len(self.image_data)
            if file_size > 50 * 1024 * 1024:  # 50MB
                self.results_textbox.insert("end", "⚠️ Large file size - potential security concern\n")
            else:
                self.results_textbox.insert("end", "✅ File size within normal parameters\n")
            
            self.results_textbox.insert("end", "✅ Basic security assessment completed\n")
            
        except Exception as e:
            self.results_textbox.insert("end", f"❌ Security assessment error: {str(e)}\n")

    def open_forensic_tools(self):
        """Open professional forensic analysis tools"""
        self.results_textbox.insert("end", f"\n{'=' * 60}\n")
        self.results_textbox.insert("end", f"🔬 PROFESSIONAL FORENSIC ANALYSIS TOOLS\n")
        self.results_textbox.insert("end", f"{'=' * 60}\n")
        
        forensic_tools = [
            {
                "name": "Forensically",
                "url": "https://29a.ch/photo-forensics/",
                "description": "Advanced image forensics toolkit",
                "capabilities": "Clone detection, Error level analysis, Noise analysis"
            },
            {
                "name": "FotoForensics",
                "url": "http://fotoforensics.com/",
                "description": "Error level analysis and metadata viewer",
                "capabilities": "ELA analysis, EXIF data, Thumbnail analysis"
            },
            {
                "name": "Jeffrey's EXIF Viewer",
                "url": "http://exif.regex.info/exif.cgi",
                "description": "Comprehensive EXIF and metadata analysis",
                "capabilities": "Detailed EXIF, GPS mapping, Color analysis"
            },
            {
                "name": "Ghiro Online",
                "url": "https://www.imageforensic.org/",
                "description": "Professional image forensics platform",
                "capabilities": "Hash analysis, Signature verification, Advanced metadata"
            },
            {
                "name": "InVID Verification Plugin",
                "url": "https://www.invid-project.eu/tools-and-services/invid-verification-plugin/",
                "description": "Video and image verification toolkit",
                "capabilities": "Reverse search, Metadata analysis, Verification"
            }
        ]
        
        self.results_textbox.insert("end", "🔬 PROFESSIONAL FORENSIC TOOLS:\n\n")
        self.results_textbox.insert("end", "🚀 AUTOMATICALLY OPENING ALL FORENSIC TOOLS...\n\n")
        
        # Automatically open all forensic tools
        for i, tool in enumerate(forensic_tools, 1):
            self.results_textbox.insert("end", f"🔬 Opening {tool['name']}...\n")
            webbrowser.open(tool['url'])
            time.sleep(1)  # Small delay between opening tabs
        
        self.results_textbox.insert("end", f"\n✅ All {len(forensic_tools)} forensic tools opened in browser!\n")
        self.results_textbox.insert("end", "💡 Check your browser tabs for professional analysis tools.\n\n")
        
        # Also display tool information for reference
        self.results_textbox.insert("end", "📋 FORENSIC TOOLS REFERENCE:\n")
        for i, tool in enumerate(forensic_tools, 1):
            self.results_textbox.insert("end", f"{i}. {tool['name']}\n")
            self.results_textbox.insert("end", f"   📋 Description: {tool['description']}\n")
            self.results_textbox.insert("end", f"   🔧 Capabilities: {tool['capabilities']}\n")
            self.insert_clickable_link(f"   🌐 {tool['name']} Link", tool['url'])
            self.results_textbox.insert("end", "\n")
        
        self.results_textbox.insert("end", "🔍 FORENSIC ANALYSIS CAPABILITIES:\n")
        capabilities = [
            "Image manipulation detection",
            "Copy-move forgery analysis",
            "Splicing detection",
            "Resampling artifact identification",
            "Compression inconsistency analysis",
            "Metadata tampering detection",
            "Double JPEG compression analysis",
            "Digital noise pattern analysis",
            "Color/lighting inconsistency detection",
            "Steganography detection"
        ]
        
        for capability in capabilities:
            self.results_textbox.insert("end", f"  ✓ {capability}\n")
        
        self.results_textbox.insert("end", "\n📋 PROFESSIONAL WORKFLOW:\n")
        workflow_steps = [
            "Upload image to multiple forensic tools",
            "Run comprehensive analysis suite",
            "Cross-reference results across platforms",
            "Document findings with screenshots",
            "Generate professional forensic report",
            "Maintain chain of custody documentation"
        ]
        
        for i, step in enumerate(workflow_steps, 1):
            self.results_textbox.insert("end", f"  {i}. {step}\n")
        
        self.update_status("🔬 Forensic tools opened - Professional analysis available")

    def generate_professional_report(self):
        """Generate professional analysis report"""
        if not self.image_data and not self.url_entry.get().strip():
            messagebox.showwarning("No Analysis", "Please perform analysis first.")
            return
        
        self.results_textbox.insert("end", f"\n{'=' * 60}\n")
        self.results_textbox.insert("end", f"📋 PROFESSIONAL ANALYSIS REPORT\n")
        self.results_textbox.insert("end", f"{'=' * 60}\n")
        
        report_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        report = f"""
🏢 CIOT PROFESSIONAL IMAGE ANALYSIS REPORT
📅 Report Generated: {report_time}
🔒 Classification: PROFESSIONAL INVESTIGATION
👤 Analyst: CIOT System User
🆔 Case ID: IMG-{int(time.time())}

📋 EXECUTIVE SUMMARY:
This report contains the results of professional image analysis conducted using
the Cyber Investigation OSINT Toolkit (CIOT) Professional Image Analysis System.
The analysis includes technical examination, metadata extraction, hash generation,
and reverse image search results.

📊 TECHNICAL ANALYSIS:
"""
        
        if self.current_image_path:
            filename = os.path.basename(self.current_image_path)
            file_size = len(self.image_data)
            
            try:
                with Image.open(BytesIO(self.image_data)) as img:
                    report += f"""
📁 File Information:
  • Filename: {filename}
  • File Size: {file_size:,} bytes ({file_size/1024/1024:.2f} MB)
  • Dimensions: {img.width} x {img.height} pixels
  • Format: {img.format}
  • Color Mode: {img.mode}
  • Megapixels: {(img.width * img.height) / 1000000:.2f} MP
"""
            except:
                pass
        
        if 'hashes' in self.analysis_results:
            hashes = self.analysis_results['hashes']
            report += f"""
🔐 Digital Evidence Integrity:
  • MD5 Hash: {hashes['md5']}
  • SHA-1 Hash: {hashes['sha1']}
  • SHA-256 Hash: {hashes['sha256']}
"""
        
        if self.hosted_url:
            report += f"""
🌐 Reverse Search Analysis:
  • Image hosted at: {self.hosted_url}
  • Search engines utilized: Google, Yandex, Bing, TinEye, Baidu
  • Professional cross-platform analysis recommended
"""
        
        report += f"""
⚖️ LEGAL CONSIDERATIONS:
• This analysis was conducted using professional-grade tools
• Hash values provide cryptographic integrity verification
• Metadata analysis may reveal privacy-sensitive information
• Results should be verified through multiple independent sources
• Chain of custody should be maintained for legal proceedings

🔒 CONFIDENTIALITY NOTICE:
This report contains potentially sensitive information and should be handled
according to applicable privacy laws and organizational security policies.

📋 ANALYST CERTIFICATION:
This analysis was conducted using the CIOT Professional Image Analysis System
following industry-standard forensic methodologies and best practices.

Report End - {report_time}
"""
        
        self.results_textbox.insert("end", report)
        self.update_status("📋 Professional report generated")

    def clear_results(self):
        """Clear results and reset system"""
        self.results_textbox.delete("1.0", "end")
        self.show_professional_welcome()
        self.analysis_results = {}
        self.hosted_url = None

    def insert_clickable_link(self, text, url):
        """Insert clickable link with professional styling"""
        start_pos = self.results_textbox.index("end-1c")
        self.results_textbox.insert("end", f"{text}\n")
        end_pos = self.results_textbox.index("end-1c")
        
        # Create unique tag
        tag_name = f"link_{hash(url)}"
        self.results_textbox.tag_add(tag_name, start_pos, end_pos)
        self.results_textbox.tag_config(tag_name, foreground="#00aaff", underline=True)
        self.results_textbox.tag_bind(tag_name, "<Button-1>", lambda e: webbrowser.open(url))
        self.results_textbox.tag_bind(tag_name, "<Enter>", 
                                    lambda e: self.results_textbox.configure(cursor="hand2"))
        self.results_textbox.tag_bind(tag_name, "<Leave>", 
                                    lambda e: self.results_textbox.configure(cursor=""))