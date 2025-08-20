"""Additional CIOT Tools Tab (Clean Rebuild)

Provides ONLY these tool categories:
  - Network: Port Scanner, DNS Lookup, Traceroute
  - Social: Username Search
  - Crypto: Blockchain Explorer, Wallet Analyzer, Transaction Tracker

All Sherlock / Social Analyzer legacy code removed.
"""
from __future__ import annotations

import customtkinter as ctk
import socket
import threading
import time
import webbrowser
import requests
import platform
import subprocess
from typing import Optional


class AdditionalToolsTab(ctk.CTkFrame):
    def __init__(self, master, **kwargs):  # pragma: no cover - GUI container
        super().__init__(master, **kwargs)
        self._traceroute_process: Optional[subprocess.Popen] = None
        self._traceroute_stop_flag = False
        self._build_ui()

    # ================= UI =================
    def _build_ui(self):  # pragma: no cover - layout
        ctk.CTkLabel(self, text="⚙️ Additional CIOT Tools", font=ctk.CTkFont(size=24, weight="bold")).pack(pady=20)
        row = ctk.CTkFrame(self)
        row.pack(fill="both", expand=True, padx=20, pady=20)

        # Network
        net = ctk.CTkFrame(row)
        net.pack(side="left", fill="both", expand=True, padx=10, pady=10)
        ctk.CTkLabel(net, text="🌐 Network", font=ctk.CTkFont(size=16, weight="bold")).pack(pady=8)
        ctk.CTkButton(net, text="Port Scanner", command=self.port_scanner, height=40).pack(fill="x", padx=6, pady=4)
        ctk.CTkButton(net, text="DNS Lookup", command=self.dns_lookup, height=40).pack(fill="x", padx=6, pady=4)
        ctk.CTkButton(net, text="Traceroute", command=self.traceroute, height=40).pack(fill="x", padx=6, pady=4)

        # Social
        soc = ctk.CTkFrame(row)
        soc.pack(side="left", fill="both", expand=True, padx=10, pady=10)
        ctk.CTkLabel(soc, text="📱 Social", font=ctk.CTkFont(size=16, weight="bold")).pack(pady=8)
        ctk.CTkButton(soc, text="Username Search", command=self.username_search, height=40).pack(fill="x", padx=6, pady=4)

        # Crypto
        cry = ctk.CTkFrame(row)
        cry.pack(side="left", fill="both", expand=True, padx=10, pady=10)
        ctk.CTkLabel(cry, text="₿ Crypto", font=ctk.CTkFont(size=16, weight="bold")).pack(pady=8)
        ctk.CTkButton(cry, text="Blockchain Explorer", command=self.blockchain_explorer, height=40).pack(fill="x", padx=6, pady=4)
        ctk.CTkButton(cry, text="Wallet Analyzer", command=self.wallet_analyzer, height=40).pack(fill="x", padx=6, pady=4)
        ctk.CTkButton(cry, text="Transaction Tracker", command=self.transaction_tracker, height=40).pack(fill="x", padx=6, pady=4)

        # Results area
        wrap = ctk.CTkFrame(self, corner_radius=12)
        wrap.pack(fill="both", expand=True, padx=20, pady=(10, 20))
        head = ctk.CTkFrame(wrap, fg_color="transparent")
        head.pack(fill="x", padx=10, pady=(10, 6))
        ctk.CTkLabel(head, text="📊", font=ctk.CTkFont(size=16)).pack(side="left")
        ctk.CTkLabel(head, text="Results", font=ctk.CTkFont(size=16, weight="bold")).pack(side="left", padx=(6, 0))
        self.status_label = ctk.CTkLabel(head, text="Ready", font=ctk.CTkFont(size=11), text_color="#4a9eff")
        self.status_label.pack(side="right")
        self.out = ctk.CTkTextbox(wrap, wrap="word", font=ctk.CTkFont(size=11))
        self.out.pack(fill="both", expand=True, padx=8, pady=(0, 8))
        self.out.insert("end", "🛠️ Ready. Use the buttons above.\n")

    def _ask(self, title: str, prompt: str, default: str = ""):
        dlg = ctk.CTkInputDialog(title=title, text=prompt)
        return dlg.get_input()

    # =============== Network ===============
    def port_scanner(self):
        target = self._ask("Port Scanner", "Target host/IP:", "example.com")
        if not target:
            return
        self.out.delete("1.0", "end")
        self.out.insert("end", f"🔍 Port Scan: {target}\n{'='*50}\n")
        threading.Thread(target=self._scan_ports, args=(target,), daemon=True).start()

    def _scan_ports(self, target: str):
        ports = [21, 22, 23, 25, 53, 80, 110, 143, 443, 993, 995, 3306, 3389, 5432, 8080, 8443]
        open_ports = []
        for i, p in enumerate(ports):
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.settimeout(1)
                if s.connect_ex((target, p)) == 0:
                    open_ports.append(p)
                    self.out.insert("end", f"✅ {p} open\n")
                s.close()
            except Exception:
                pass
            if (i + 1) % 5 == 0:
                self.out.insert("end", f"Progress {(i+1)/len(ports)*100:.0f}%\n")
        self.out.insert("end", "\nSummary:\n")
        self.out.insert("end", f"Open: {', '.join(map(str, open_ports)) if open_ports else 'None'}\n")
        self.out.insert("end", "Done.\n")

    def dns_lookup(self):
        domain = self._ask("DNS Lookup", "Domain:", "google.com")
        if not domain:
            return
        self.out.delete("1.0", "end")
        self.out.insert("end", f"🌐 DNS Lookup: {domain}\n{'='*50}\n")
        try:
            ip = socket.gethostbyname(domain)
            self.out.insert("end", f"IPv4: {ip}\n")
            try:
                rev = socket.gethostbyaddr(ip)[0]
            except Exception:
                rev = "(reverse unavailable)"
            self.out.insert("end", f"Reverse: {rev}\n")
        except Exception as e:
            self.out.insert("end", f"Error: {e}\n")

    def traceroute(self):  # pragma: no cover - launches window
        win = ctk.CTkToplevel(self)
        win.title("Traceroute")
        win.geometry("720x520")
        win.grab_set()
        head = ctk.CTkFrame(win)
        head.pack(fill="x", padx=10, pady=10)
        ctk.CTkLabel(head, text="🛤️ Traceroute", font=ctk.CTkFont(size=20, weight="bold")).pack(side="left")
        status = ctk.CTkLabel(head, text="Ready", font=ctk.CTkFont(size=11), text_color="#4caf50")
        status.pack(side="right")
        bar = ctk.CTkFrame(win)
        bar.pack(fill="x", padx=10, pady=(0, 10))
        ctk.CTkLabel(bar, text="Target:").pack(side="left", padx=(4, 4))
        target_var = ctk.StringVar(value="8.8.8.8")
        entry = ctk.CTkEntry(bar, textvariable=target_var, width=220)
        entry.pack(side="left")
        start_btn = ctk.CTkButton(bar, text="Start")
        start_btn.pack(side="left", padx=(10, 0))
        stop_btn = ctk.CTkButton(bar, text="Stop", state="disabled", fg_color="#ff4444")
        stop_btn.pack(side="left", padx=(10, 0))
        out_box = ctk.CTkTextbox(win, wrap="word", font=ctk.CTkFont(size=11))
        out_box.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        out_box.insert("end", "Enter a target and press Start.\n")

        def start():
            tgt = target_var.get().strip()
            if not tgt:
                status.configure(text="Enter target", text_color="#ff4444")
                return
            out_box.delete("1.0", "end")
            out_box.insert("end", f"Traceroute to {tgt}\n{'-'*40}\n")
            start_btn.configure(state="disabled")
            stop_btn.configure(state="normal")
            status.configure(text="Running...", text_color="#ff9500")
            self._traceroute_stop_flag = False
            threading.Thread(target=self._run_traceroute, args=(tgt, out_box, status, start_btn, stop_btn), daemon=True).start()

        def stop():
            self._traceroute_stop_flag = True
            status.configure(text="Stopping...", text_color="#ff9500")
            if self._traceroute_process and self._traceroute_process.poll() is None:
                try:
                    self._traceroute_process.terminate()
                except Exception:
                    pass

        start_btn.configure(command=start)
        stop_btn.configure(command=stop)
        entry.bind("<Return>", lambda _ : start_btn.invoke())

    def _run_traceroute(self, target, out_box, status_label, start_btn, stop_btn):
        if platform.system().lower().startswith("win"):
            cmd = ["tracert", target]
        else:
            cmd = ["traceroute", target] if subprocess.getoutput("which traceroute 2>/dev/null") else ["ping", "-c", "4", target]
        try:
            self._traceroute_process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
            while True:
                if self._traceroute_stop_flag:
                    out_box.insert("end", "\n⏹️ Stopped by user.\n")
                    break
                line = self._traceroute_process.stdout.readline()
                if not line:
                    if self._traceroute_process.poll() is not None:
                        break
                    time.sleep(0.05)
                    continue
                out_box.insert("end", line.rstrip() + "\n")
                out_box.see("end")
            rc = self._traceroute_process.wait()
            status_label.configure(text=("Complete" if rc == 0 else f"Exit {rc}"), text_color="#4caf50" if rc == 0 else "#ff4444")
        except Exception as e:
            out_box.insert("end", f"\nError: {e}\n")
            status_label.configure(text="Error", text_color="#ff4444")
        finally:
            start_btn.configure(state="normal")
            stop_btn.configure(state="disabled")

    # =============== Social ===============
    def username_search(self):
        user = self._ask("Username Search", "Username:", "exampleuser")
        if not user:
            return
        user = user.strip()
        self.out.delete("1.0", "end")
        self.out.insert("end", f"📱 Username Search: {user}\n{'='*50}\n")
        platforms = [
            ("Twitter", f"https://twitter.com/{user}"),
            ("Instagram", f"https://instagram.com/{user}"),
            ("GitHub", f"https://github.com/{user}"),
            ("Reddit", f"https://reddit.com/user/{user}"),
            ("YouTube", f"https://youtube.com/@{user}"),
            ("TikTok", f"https://tiktok.com/@{user}"),
            ("LinkedIn", f"https://linkedin.com/in/{user}"),
        ]
        for i, (name, url) in enumerate(platforms, 1):
            self.out.insert("end", f"{i}. {name}: {url}\n")
        self.out.insert("end", "\nOpening first 4...\n")
        for _, url in platforms[:4]:
            webbrowser.open(url)
            time.sleep(0.35)
        self.out.insert("end", "\nTips:\n- Compare bios/images\n- Check activity timing\n- Capture evidence early\n")

    # =============== Crypto ===============
    def blockchain_explorer(self):
        addr = self._ask("Blockchain Explorer", "Bitcoin address:", "1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa")
        if not addr:
            return
        self.out.delete("1.0", "end")
        self.out.insert("end", f"₿ Address Explorer: {addr}\n{'='*50}\n")
        explorers = [
            ("Blockchain.com", f"https://www.blockchain.com/btc/address/{addr}"),
            ("Blockstream", f"https://blockstream.info/address/{addr}"),
            ("BitRef", f"https://bitref.com/{addr}"),
            ("OXT", f"https://oxt.me/address/{addr}"),
            ("BlockCypher", f"https://live.blockcypher.com/btc/address/{addr}/"),
        ]
        for i, (name, url) in enumerate(explorers, 1):
            self.out.insert("end", f"{i}. {name}\n   {url}\n")
            webbrowser.open(url)
            time.sleep(0.3)
        if addr == "1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa":
            self.out.insert("end", "\nGenesis (historic) address.\n")
        self.out.insert("end", "\nReview: balance, tx count, frequency, clustering.\n")

    def wallet_analyzer(self):
        addr = self._ask("Wallet Analyzer", "Bitcoin address:", "1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa")
        if not addr:
            return
        self.out.delete("1.0", "end")
        self.out.insert("end", "🔍 Wallet Analyzer\n" + "=" * 50 + "\n")
        threading.Thread(target=self._wallet_analysis, args=(addr,), daemon=True).start()

    def _wallet_analysis(self, addr: str):
        try:
            self.out.insert("end", "Querying Blockstream API...\n")
            r = requests.get(f"https://blockstream.info/api/address/{addr}", timeout=15)
            if r.status_code != 200:
                self.out.insert("end", f"API status {r.status_code}\n")
                return
            data = r.json()
            cs = data.get('chain_stats', {})
            funded = cs.get('funded_txo_sum', 0) / 1e8
            spent = cs.get('spent_txo_sum', 0) / 1e8
            balance = funded - spent
            txc = cs.get('tx_count', 0)
            self.out.insert("end", f"Balance: {balance:.8f} BTC\nReceived: {funded:.8f} BTC\nSpent: {spent:.8f} BTC\nTx Count: {txc}\n")
            self.out.insert("end", f"Status: {'Active' if balance > 0 else 'Empty'}\n")
            if txc > 1000:
                self.out.insert("end", "Activity: High volume\n")
            elif txc > 100:
                self.out.insert("end", "Activity: Moderate\n")
            else:
                self.out.insert("end", "Activity: Low\n")
            if funded > 1000:
                self.out.insert("end", "Category: Whale (>1000 BTC)\n")
            elif funded > 100:
                self.out.insert("end", "Category: Large Holder (>100 BTC)\n")
            if addr == "1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa":
                self.out.insert("end", "Historic: Genesis address.\n")
            self.out.insert("end", "Done.\n")
        except Exception as e:
            self.out.insert("end", f"Error: {e}\n")

    def transaction_tracker(self):
        txid = self._ask("Transaction Tracker", "Transaction hash:")
        if not txid:
            return
        self.out.delete("1.0", "end")
        self.out.insert("end", "🔄 Transaction Tracker\n" + "=" * 50 + "\n")
        explorers = [
            ("Blockchain.com", f"https://www.blockchain.com/btc/tx/{txid}"),
            ("Blockstream", f"https://blockstream.info/tx/{txid}"),
            ("BlockCypher", f"https://live.blockcypher.com/btc/tx/{txid}"),
            ("OXT", f"https://oxt.me/transaction/{txid}"),
        ]
        for i, (name, url) in enumerate(explorers, 1):
            self.out.insert("end", f"{i}. {name}\n   {url}\n")
            webbrowser.open(url)
            time.sleep(0.25)
        if len(txid) == 64:
            self.out.insert("end", "\nAttempting API lookup...\n")
            threading.Thread(target=self._tx_api, args=(txid,), daemon=True).start()
        else:
            self.out.insert("end", "\nInvalid hash length (need 64).\n")

    def _tx_api(self, txid: str):
        try:
            r = requests.get(f"https://blockstream.info/api/tx/{txid}", timeout=10)
            if r.status_code != 200:
                self.out.insert("end", f"API status {r.status_code}\n")
                return
            data = r.json()
            st = data.get('status', {})
            self.out.insert("end", "\nReal-Time Data:\n")
            self.out.insert("end", f"Confirmed: {st.get('confirmed', False)}\nBlock: {st.get('block_height', 'Pending')}\n")
            self.out.insert("end", f"Size: {data.get('size', 0)} bytes\nFee: {data.get('fee', 0)} sats\n")
            self.out.insert("end", f"Inputs: {len(data.get('vin', []))}\nOutputs: {len(data.get('vout', []))}\n")
        except Exception as e:
            self.out.insert("end", f"API error: {e}\n")


__all__ = ["AdditionalToolsTab"]
