"""Clean minimal Dark Web OSINT tab.

Implements only agreed acceptance criteria:
 - Default tool TorBot
 - Onion v3 validation for TorBot / OnionScan / Dark Scrape
 - Start Scan disabled until valid (or non-empty for non-onion tools)
 - Status lifecycle Ready -> Running... -> Complete
 - Initial results text 'No scan started'
 - Export buttons disabled until completion
 - Simulated threaded runners
 - PDF / JSON export after completion
"""
from __future__ import annotations
import re, json, threading
import customtkinter as ctk
from fpdf import FPDF

class DarkWebTab(ctk.CTkFrame):
    ONION_V3_PATTERN = re.compile(r'^(?:https?://)?(?=.{62,64}$)([a-z2-7]{56})\.onion(?::\d{2,5})?(?:/.*)?$')
    TOOLS = [
        "TorBot", "h8mail", "OnionScan", "Final Recon", "OSINT-SPY",
        "Dark Scrape", "Fresh Onions", "Breach Hunt", "Bitcoin Analysis"
    ]

    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.grid_rowconfigure(2, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self._build_controls()
        self._build_results()
        self._change_tool_type()
        # Add tor service button below controls
        self._add_tor_service_button()
        # Result store list for accumulating completed scans
        self.result_store = []

    def _build_controls(self):
        bar = ctk.CTkFrame(self)
        bar.grid(row=0, column=0, padx=10, pady=6, sticky="ew")
        bar.grid_columnconfigure(1, weight=1)
        ctk.CTkLabel(bar, text="Dark Web OSINT Tool:", font=ctk.CTkFont(size=14, weight="bold")).grid(row=0, column=0, padx=6, pady=4, sticky="w")
        self.tool_var = ctk.StringVar(value="TorBot")
        ctk.CTkOptionMenu(bar, variable=self.tool_var, values=self.TOOLS, command=lambda _v: self._change_tool_type()).grid(row=0, column=1, padx=6, pady=4, sticky="ew")
        # Save Results toggle
        self.save_results_var = ctk.BooleanVar(value=True)
        self.save_toggle = ctk.CTkCheckBox(bar, text="Save Results", variable=self.save_results_var)
        self.save_toggle.grid(row=0, column=2, padx=6, pady=4)
        # Extract Emails toggle
        self.extract_emails_var = ctk.BooleanVar(value=True)
        self.extract_toggle = ctk.CTkCheckBox(bar, text="Extract Emails", variable=self.extract_emails_var)
        self.extract_toggle.grid(row=0, column=3, padx=6, pady=4)
        # Live Status (HEAD reachability) toggle
        self.live_status_var = ctk.BooleanVar(value=True)
        self.live_status_toggle = ctk.CTkCheckBox(bar, text="Check Live Status", variable=self.live_status_var)
        self.live_status_toggle.grid(row=0, column=4, padx=6, pady=4)

        row = ctk.CTkFrame(self)
        row.grid(row=1, column=0, padx=10, pady=4, sticky="ew")
        row.grid_columnconfigure(1, weight=1)
        self.input_label = ctk.CTkLabel(row, text="Enter .onion URL:")
        self.input_label.grid(row=0, column=0, padx=6, pady=4, sticky="w")
        self.input_var = ctk.StringVar()
        self.input_entry = ctk.CTkEntry(row, textvariable=self.input_var, placeholder_text="Enter .onion URL", height=40)
        self.input_entry.grid(row=0, column=1, padx=6, pady=4, sticky="ew")
        self.input_entry.bind("<KeyRelease>", lambda _e: self._validate_input())
        self.scan_btn = ctk.CTkButton(row, text="Start Scan", command=self._do_scan, height=40, state="disabled")
        self.scan_btn.grid(row=0, column=2, padx=6, pady=4)
        self.error_label = ctk.CTkLabel(row, text="", text_color="#ff5555", font=ctk.CTkFont(size=10))
        self.error_label.grid(row=1, column=0, columnspan=3, padx=6, pady=(0,4), sticky="w")

    def _build_results(self):
        wrap = ctk.CTkFrame(self)
        wrap.grid(row=2, column=0, padx=12, pady=(4,10), sticky="nsew")
        wrap.grid_rowconfigure(1, weight=1)
        wrap.grid_columnconfigure(0, weight=1)
        head = ctk.CTkFrame(wrap, fg_color="transparent")
        head.grid(row=0, column=0, sticky="ew", padx=4, pady=(6,4))
        head.grid_columnconfigure(1, weight=1)
        ctk.CTkLabel(head, text="📊", font=ctk.CTkFont(size=16)).grid(row=0, column=0, sticky="w")
        ctk.CTkLabel(head, text="Scan Results", font=ctk.CTkFont(size=16, weight="bold")).grid(row=0, column=1, sticky="w", padx=(4,0))
        self.status_label = ctk.CTkLabel(head, text="Ready", font=ctk.CTkFont(size=11), text_color=("#3b8ed0", "#3b8ed0"))
        self.status_label.grid(row=0, column=2, sticky="e")
        self.results = ctk.CTkTextbox(wrap, wrap="word", corner_radius=6, font=ctk.CTkFont(size=11))
        self.results.grid(row=1, column=0, sticky="nsew", padx=4, pady=(0,4))
        self.results.insert("end", "No scan started")

        exp = ctk.CTkFrame(self)
        exp.grid(row=3, column=0, padx=10, pady=(0,6), sticky="ew")
        self.export_pdf_btn = ctk.CTkButton(exp, text="Export PDF", command=self._export_pdf, state="disabled")
        self.export_pdf_btn.pack(side="left", padx=4, pady=4)
        self.export_json_btn = ctk.CTkButton(exp, text="Export JSON", command=self._export_json, state="disabled")
        self.export_json_btn.pack(side="left", padx=4, pady=4)

    def _add_tor_service_button(self):
        """Add a button to start Tor service and test connectivity."""
        if hasattr(self, 'tor_button_added'):
            return
        self.tor_button_added = True
        tor_frame = ctk.CTkFrame(self)
        tor_frame.grid(row=4, column=0, padx=10, pady=(0,6), sticky="ew")
        self.start_tor_btn = ctk.CTkButton(tor_frame, text="🧅 Start Tor Service", command=self._start_tor_service)
        self.start_tor_btn.pack(side="left", padx=4, pady=4)
        self.tor_status_label = ctk.CTkLabel(tor_frame, text="Tor: Unknown", font=ctk.CTkFont(size=11), text_color=("#888", "#888"))
        self.tor_status_label.pack(side="left", padx=6)

    def _change_tool_type(self):
        placeholders = {
            "TorBot": ("Enter .onion URL:", "Enter .onion URL"),
            "h8mail": ("Enter Email Address:", "e.g., user@example.com"),
            "OnionScan": ("Enter .onion URL:", "Enter .onion URL"),
            "Final Recon": ("Enter Domain/IP:", "e.g., example.com or 8.8.8.8"),
            "OSINT-SPY": ("Enter Target:", "Email, domain, IP, or Bitcoin"),
            "Dark Scrape": ("Enter .onion URL:", "Enter .onion URL"),
            "Fresh Onions": ("Search Keywords:", "e.g., marketplace, forum"),
            "Breach Hunt": ("Enter Email/Username:", "e.g., user@domain.com"),
            "Bitcoin Analysis": ("Enter Bitcoin Address:", "e.g., 1A1zP1... or bc1...")
        }
        tool = self.tool_var.get()
        label, ph = placeholders.get(tool, ("Enter Target:", "Target"))
        self.input_label.configure(text=label)
        self.input_entry.configure(placeholder_text=ph)
        self.results.delete("1.0", "end")
        self.results.insert("end", "No scan started")
        self.status_label.configure(text="Ready")
        self.export_pdf_btn.configure(state="disabled")
        self.export_json_btn.configure(state="disabled")
        self._validate_input()

    def _validate_input(self):
        tool = self.tool_var.get()
        val = self.input_var.get().strip()
        onion_tools = {"TorBot", "OnionScan", "Dark Scrape"}
        if tool in onion_tools:
            if not val:
                self.error_label.configure(text="")
                self.scan_btn.configure(state="disabled")
                return
            if self.ONION_V3_PATTERN.match(val):
                self.error_label.configure(text="")
                self.scan_btn.configure(state="normal")
            else:
                self.error_label.configure(text="Invalid v3 .onion address")
                self.scan_btn.configure(state="disabled")
        else:
            self.error_label.configure(text="")
            self.scan_btn.configure(state="normal" if val else "disabled")

    def _do_scan(self):
        target = self.input_var.get().strip()
        if not target:
            return
        # Concurrency guard: avoid overlapping scans
        if getattr(self, '_scan_active', False):
            self.results.insert('end', "\n⚠️ A scan is already running. Please wait for completion.\n")
            self.results.see('end')
            return
        tool = self.tool_var.get()
        self.results.delete("1.0", "end")
        self.results.insert("end", f"🚀 Starting {tool} scan on: {target}\n{'='*50}\n\n")
        self.status_label.configure(text="Running...")
        self.scan_btn.configure(state="disabled")
        self.export_pdf_btn.configure(state="disabled")
        self.export_json_btn.configure(state="disabled")
        self.current_result = None
        self._scan_active = True
        threading.Thread(target=self._run_streaming_tool, args=(tool, target), daemon=True).start()

    def _run_streaming_tool(self, tool: str, target: str):
        from src.services.run_tool_dispatcher import run_tool
        import os, json, time
        log_lines = []
        config = {
            "extract_emails": getattr(self, 'extract_emails_var', None) and self.extract_emails_var.get(),
            "check_live_status": getattr(self, 'live_status_var', None) and self.live_status_var.get(),
            "save_results": getattr(self, 'save_results_var', None) and self.save_results_var.get(),
        }
        def ui_append(line: str):
            # Thread-safe append using after
            self.after(0, lambda l=line: (self.results.insert('end', l + '\n'), self.results.see('end')))

        for event in run_tool(tool, target, config):
            if event.get('event') == 'log':
                line = event['line']
                log_lines.append(line)
                ui_append(line)
            elif event.get('event') == 'complete':
                self.current_result = event['result']
        # Completion handling
        def finalize():
            if self.current_result:
                self.results.insert('end', "\n✅ Scan complete.\n")
                self.status_label.configure(text="Complete")
                self.export_pdf_btn.configure(state="normal")
                self.export_json_btn.configure(state="normal")
                self.scan_btn.configure(state="normal")
            else:
                self.results.insert('end', "\n❌ Scan produced no result object.\n")
                self.status_label.configure(text="Error")
                self.scan_btn.configure(state="normal")
            self.results.see('end')
            self._scan_active = False
        # Append result store & auto-save outside UI freeze
        if self.current_result:
            # Append to result store
            try:
                self.result_store.append(self.current_result)
            except Exception:
                pass
            # Auto-save if toggle
            if getattr(self, 'save_results_var', None) and self.save_results_var.get():
                out_dir = os.path.join('outputs', 'darkweb')
                os.makedirs(out_dir, exist_ok=True)
                ts = time.strftime('%Y%m%d_%H%M%S')
                fname = f"{tool.lower().replace(' ', '_')}_{ts}.json"
                path = os.path.join(out_dir, fname)
                try:
                    with open(path, 'w', encoding='utf-8') as f:
                        json.dump(self.current_result, f, indent=2)
                    ui_append(f"💾 Saved results to {path}")
                except Exception as e:
                    ui_append(f"❌ Save error: {e}")
        self.after(0, finalize)

    def _export_json(self):
        try:
            if getattr(self, 'current_result', None):
                fname = f"CIOT_darkweb_{self.tool_var.get().lower()}_export.json"
                with open(fname, 'w', encoding='utf-8') as f:
                    json.dump(self.current_result, f, indent=2, ensure_ascii=False)
                self.results.insert("end", f"\n✅ Results exported to {fname}\n")
            else:
                super_export = False
                fname = f"CIOT_darkweb_{self.tool_var.get().lower()}_export.json"
                payload = {"tool": self.tool_var.get(), "target": self.input_var.get(), "results": self.results.get('1.0','end')}
                with open(fname, 'w', encoding='utf-8') as f:
                    json.dump(payload, f, indent=2, ensure_ascii=False)
                self.results.insert("end", f"\n⚠️ Structured result missing – exported raw log to {fname}\n")
        except Exception as e:
            self.results.insert("end", f"\n❌ JSON Export Error: {e}\n")
        self.results.see('end')

    def _export_pdf(self):
        content_result = getattr(self, 'current_result', None)
        if content_result:
            log_text = '\n'.join(content_result.get('log', []))
            findings = content_result.get('findings', {})
            composed = [
                "CIOT Dark Web OSINT Report",
                f"Tool: {content_result.get('tool')}",
                f"Target: {content_result.get('target')}",
                f"Started: {content_result.get('started_at')}",
                f"Finished: {content_result.get('finished_at')}",
                "",
                "=== Findings ===",
                f"Links: {len(findings.get('links', []))}",
                *findings.get('links', []),
                "",
                f"Emails: {len(findings.get('emails', []))}",
                *findings.get('emails', []),
                "",
                f"Bitcoin: {len(findings.get('btc', []))}",
                *findings.get('btc', []),
                "",
                "=== Log ===",
                log_text
            ]
            content = '\n'.join(composed)
        else:
            content = self.results.get('1.0','end')
        try:
            pdf = FPDF(); pdf.add_page(); pdf.set_font("Arial", size=10)
            for line in content.split('\n'):
                if not line:
                    pdf.ln(4); continue
                while len(line) > 95:
                    seg = line[:95]
                    pdf.cell(0, 5, txt=seg.encode('latin-1','replace').decode('latin-1'), ln=True)
                    line = line[95:]
                pdf.cell(0, 5, txt=line.encode('latin-1','replace').decode('latin-1'), ln=True)
            pdf.output("CIOT_darkweb_report.pdf")
            self.results.insert("end", "\n✅ Report exported to CIOT_darkweb_report.pdf\n")
        except Exception as e:
            self.results.insert("end", f"\n❌ PDF Export Error: {e}\n")
        self.results.see('end')

    def _start_tor_service(self):
        """Attempt to start Tor and run a connectivity test."""
        from src.services import tor_service
        self.results.insert("end", "\n🧅 Starting Tor Service...\n")
        self.results.see("end")
        try:
            if tor_service.is_running():
                self.results.insert("end", "Tor already running on port 9050.\n")
                status = tor_service.test_connectivity()
            else:
                self.results.insert("end", "Launching tor process...\n")
                info = tor_service.start_tor()
                self.results.insert("end", f"{info['message']}\n")
                if info.get('success'):
                    status = tor_service.test_connectivity()
                else:
                    status = {"success": False, "reachable": False, "message": "Tor launch failed"}
            # Log connectivity
            if status.get('reachable'):
                self.results.insert("end", "✅ Tor reachable (check.torproject.org)\n")
                self.tor_status_label.configure(text="Tor: Running", text_color=("#2eaa4f", "#2eaa4f"))
            else:
                self.results.insert("end", f"⚠️ {status.get('message')}\n")
                self.tor_status_label.configure(text="Tor: Issue", text_color=("#d98e00", "#d98e00"))
        except FileNotFoundError:
            self.results.insert("end", "❌ Tor binary not found. Install instructions:\n")
            self.results.insert("end", "  • macOS: brew install tor\n")
            self.results.insert("end", "  • Debian/Ubuntu: sudo apt update && sudo apt install tor\n")
            self.results.insert("end", "  • Fedora: sudo dnf install tor\n")
            self.results.insert("end", "  • Arch: sudo pacman -S tor\n")
            self.results.insert("end", "  • Windows: Install Tor Browser from torproject.org (runs its own instance)\n")
            self.tor_status_label.configure(text="Tor: Not Installed", text_color=("#ff4444", "#ff4444"))
        except Exception as e:
            self.results.insert("end", f"❌ Unexpected Tor error: {e}\n")
            self.tor_status_label.configure(text="Tor: Error", text_color=("#ff4444", "#ff4444"))
        self.results.see("end")

    # End of clean implementation (file intentionally ends here)

