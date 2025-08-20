import customtkinter as ctk
import tkinter as tk
import webbrowser
from datetime import datetime
from tkinter import filedialog, messagebox

class GoogleDorkingTab(ctk.CTkFrame):
    """Professional Google Dorking generation tab."""
    def __init__(self, master=None, **kwargs):
        super().__init__(master, **kwargs)
        self.configure(fg_color="#1a1a1a")
        self._build_ui()

    def _build_ui(self):
        # Header
        header = ctk.CTkLabel(self, text="🕵️ Google Dorking Toolkit", font=ctk.CTkFont(size=22, weight="bold"), text_color="#00d4ff")
        header.pack(pady=(20,5))

        sub = ctk.CTkLabel(self, text="Generate categorized professional Google dorks for OSINT investigations.", font=ctk.CTkFont(size=12))
        sub.pack(pady=(0,10))

        # Input frame
        input_frame = ctk.CTkFrame(self, corner_radius=10)
        input_frame.pack(fill="x", padx=20, pady=(0,10))

        self.target_type = tk.StringVar(value="Username")
        self.target_entry = ctk.CTkEntry(input_frame, width=300, placeholder_text="Enter target (username, name, email, phone)")
        self.target_entry.pack(side="left", padx=10, pady=15)

        type_menu = ctk.CTkOptionMenu(input_frame, values=["Username","Name","Email","Phone"], variable=self.target_type, width=130)
        type_menu.pack(side="left", padx=(0,10))

        self.site_specific = tk.BooleanVar(value=False)
        site_check = ctk.CTkCheckBox(input_frame, text="Enable site-specific", variable=self.site_specific)
        site_check.pack(side="left", padx=(0,20))

        self.custom_domains_entry = ctk.CTkEntry(input_frame, width=260, placeholder_text="Custom domains (comma, e.g. site:*.in, site:gov.in)")
        self.custom_domains_entry.pack(side="left", padx=(0,10))

        gen_btn = ctk.CTkButton(input_frame, text="Generate Dorks", command=self.generate_dorks, fg_color="#0077cc", hover_color="#005fa3")
        gen_btn.pack(side="left", padx=(0,10))

        copy_btn = ctk.CTkButton(input_frame, text="Copy All", command=self.copy_all)
        copy_btn.pack(side="left", padx=(0,10))

        save_btn = ctk.CTkButton(input_frame, text="Save", command=self.save_dorks)
        save_btn.pack(side="left")

        # Results frame
        results_frame = ctk.CTkFrame(self, corner_radius=12)
        results_frame.pack(fill="both", expand=True, padx=20, pady=10)

        results_header = ctk.CTkFrame(results_frame, fg_color="transparent")
        results_header.pack(fill="x", padx=10, pady=(10,5))

        self.status_label = ctk.CTkLabel(results_header, text="Ready", font=ctk.CTkFont(size=11), text_color="#00ff88")
        self.status_label.pack(side="right")

        self.results_text = ctk.CTkTextbox(results_frame, wrap="word")
        self.results_text.pack(fill="both", expand=True, padx=10, pady=(0,10))

        open_hint = ctk.CTkLabel(results_frame, text="Double-click a dork line to open in browser.", font=ctk.CTkFont(size=11), text_color="#888888")
        open_hint.pack(anchor="w", padx=12, pady=(0,8))

        # Bind double-click open
        self.results_text.bind("<Double-1>", self.open_selected_line)

    # Dork generation logic
    def generate_dorks(self):
        target = self.target_entry.get().strip()
        if not target:
            self._set_status("⚠️ Please enter a target value.")
            self.results_text.delete("1.0", tk.END)
            self.results_text.insert("1.0", "[WARNING] No input provided. Please enter a target above.")
            return
        ttype = self.target_type.get()
        base = self._sanitize(target)
        domains = []
        if self.site_specific.get():
            extra = self.custom_domains_entry.get().strip()
            if extra:
                domains = [d.strip() for d in extra.split(',') if d.strip()]
        sections = []
        if ttype == "Username":
            sections.append(("USERNAME DORKS", self._username_dorks(base, domains)))
        elif ttype == "Name":
            sections.append(("NAME DORKS", self._name_dorks(base, domains)))
        elif ttype == "Email":
            sections.append(("EMAIL DORKS", self._email_dorks(base, domains)))
        else:
            sections.append(("PHONE DORKS", self._phone_dorks(base, domains)))
        self._display_sections(sections)
        self._set_status(f"Generated {sum(len(s[1]) for s in sections)} dorks for {ttype}.")

    def _sanitize(self, val: str) -> str:
        if ' ' in val and not val.startswith('"'):
            return f'"{val}"'
        return val

    def _username_dorks(self, u: str, domains):
        d = [
            f"inurl:{u}", f"intitle:{u}", f"intext:{u}",
            f"{u} site:github.com", f"{u} site:reddit.com", f"{u} site:instagram.com",
            f"{u} site:twitter.com", f"{u} site:pastebin.com", f"{u} site:medium.com",
            f"{u} site:stackoverflow.com", f"{u} site:gitlab.com"
        ]
        for dom in domains:
            d.append(f"{u} {dom}")
        return d

    def _name_dorks(self, n: str, domains):
        d = [
            f"{n} site:linkedin.com", f"{n} site:facebook.com", f"{n} site:twitter.com",
            f"{n} site:instagram.com", f"{n} site:github.com", f"{n} resume",
            f"{n} CV", f"{n} filetype:pdf", f"{n} filetype:docx", f"{n} filetype:txt"
        ]
        for dom in domains:
            d.append(f"{n} {dom}")
        return d

    def _email_dorks(self, e: str, domains):
        user_part = e.split('@')[0]
        domain_part = e.split('@')[1] if '@' in e else ''
        d = [
            f"\"{e}\"", f"\"{e}\" filetype:txt", f"\"{e}\" filetype:log",
            f"\"{e}\" site:pastebin.com", f"\"{e}\" site:github.com", f"\"{e}\" site:gitlab.com",
            f"{user_part} site:github.com", f"{user_part} site:stackoverflow.com",
            f"{domain_part} filetype:pdf" if domain_part else "",
            f"{domain_part} (" + " OR ".join(["login","signin","authenticate"]) + ")" if domain_part else ""
        ]
        d = [x for x in d if x]
        for dom in domains:
            d.append(f"{e} {dom}")
        return d

    def _phone_dorks(self, p: str, domains):
        d = [
            f"\"{p}\" site:facebook.com", f"\"{p}\" site:linkedin.com", f"\"{p}\" site:twitter.com",
            f"\"{p}\" filetype:pdf", f"\"{p}\" filetype:docx", f"\"{p}\" filetype:txt",
            f"\"{p}\" resume", f"\"{p}\" directory"
        ]
        for dom in domains:
            d.append(f"{p} {dom}")
        return d

    def _display_sections(self, sections):
        self.results_text.configure(state="normal")
        self.results_text.delete("1.0", tk.END)
        for title, dorks in sections:
            self.results_text.insert(tk.END, f"=== {title} ===\n", ("heading",))
            for d in dorks:
                self.results_text.insert(tk.END, d + "\n")
            self.results_text.insert(tk.END, "\n")
        self.results_text.tag_config("heading", font=("Helvetica", 12, "bold"), foreground="#00d4ff")
        self.results_text.configure(state="normal")

    def copy_all(self):
        try:
            txt = self.results_text.get("1.0", tk.END).strip()
            if not txt:
                return
            self.clipboard_clear()
            self.clipboard_append(txt)
            self._set_status("Copied all dorks to clipboard.")
        except Exception:
            pass

    def save_dorks(self):
        content = self.results_text.get("1.0", tk.END).strip()
        if not content:
            self._set_status("Nothing to save.")
            return
        file_path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text Files","*.txt")])
        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(f"# Google Dorks Export - {datetime.now().isoformat()}\n\n")
                    f.write(content)
                self._set_status("Saved dorks to file.")
            except Exception:
                self._set_status("Error saving file.")

    def open_selected_line(self, event=None):
        try:
            index = self.results_text.index("@%s,%s" % (event.x, event.y))
            line_start = f"{index.split('.')[0]}.0"
            line_end = f"{index.split('.')[0]}.end"
            text = self.results_text.get(line_start, line_end).strip()
            if not text or text.startswith("==="):
                return
            url = f"https://www.google.com/search?q={text.replace(' ', '+')}"
            webbrowser.open(url)
        except Exception:
            pass

    def _set_status(self, msg: str):
        self.status_label.configure(text=msg)
