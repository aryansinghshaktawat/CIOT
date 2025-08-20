"""Tor service management utilities.

Functions:
 - is_running(): Check if Tor SOCKS proxy on 127.0.0.1:9050 is accepting connections.
 - start_tor(timeout=30): Start a local Tor process if not already running.
 - tor_session(): Return a requests.Session configured to route through Tor (SOCKS5h).
 - test_connectivity(): Quick GET to check.torproject.org via Tor to verify routing.

Design notes:
 - Non-blocking port wait loop with timeout.
 - Uses a temporary DataDirectory unique per launch to avoid permission issues.
 - Graceful handling when tor binary is missing (FileNotFoundError).
 - Safe to call start_tor() multiple times; it will not spawn duplicates if port already up.
"""
from __future__ import annotations
import socket
import subprocess
import tempfile
import time
import shutil
import os
from typing import Optional, Dict

_TOR_PROCESS: Optional[subprocess.Popen] = None
_TOR_PORT = 9050
_TOR_HOST = "127.0.0.1"


def is_running(port: int = _TOR_PORT) -> bool:
    """Return True if something (presumably Tor) is listening on the given port."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(0.5)
        try:
            return s.connect_ex((_TOR_HOST, port)) == 0
        except OSError:
            return False


def start_tor(timeout: int = 30) -> Dict:
    """Start Tor locally if not already running.

    Returns a dict with keys:
      success (bool), started (bool), already_running (bool), message (str)
    Raises FileNotFoundError if tor binary not found.
    """
    global _TOR_PROCESS

    if is_running():
        return {
            "success": True,
            "started": False,
            "already_running": True,
            "message": "Tor already running on port 9050"
        }

    tor_path = shutil.which("tor")
    if not tor_path:
        raise FileNotFoundError(
            "Tor binary not found in PATH. Install Tor (brew install tor, apt install tor, or download Tor Browser)."
        )

    data_dir = tempfile.mkdtemp(prefix="ciot_tor_datadir_")

    cmd = [
        tor_path,
        "--SOCKSPort", str(_TOR_PORT),
        "--DataDirectory", data_dir,
        "--Log", "notice stdout",
    ]

    try:
        _TOR_PROCESS = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
        )
    except Exception as e:
        return {
            "success": False,
            "started": False,
            "already_running": False,
            "message": f"Failed to launch Tor: {e}"
        }

    # Wait for port
    start_time = time.time()
    while time.time() - start_time < timeout:
        if is_running():
            return {
                "success": True,
                "started": True,
                "already_running": False,
                "message": "Tor started successfully"
            }
        # Check if process exited early
        if _TOR_PROCESS.poll() is not None:
            output = _TOR_PROCESS.stdout.read() if _TOR_PROCESS.stdout else ""
            return {
                "success": False,
                "started": False,
                "already_running": False,
                "message": f"Tor process exited prematurely. Output: {output[:500]}"
            }
        time.sleep(0.5)

    return {
        "success": False,
        "started": False,
        "already_running": False,
        "message": "Timed out waiting for Tor to open port 9050"
    }


def tor_session(timeout: int = 15):
    """Return a requests.Session configured to route traffic through Tor.
    Requires PySocks (install via 'pip install requests[socks]' or 'pip install PySocks').
    """
    import requests  # local import
    try:
        # Ensure socks support is present; requests raises if invalid scheme
        session = requests.Session()
        session.proxies.update({
            'http': 'socks5h://127.0.0.1:9050',
            'https': 'socks5h://127.0.0.1:9050'
        })
        session.timeout = timeout  # attribute for reference (not used automatically)
        return session
    except Exception as e:
        raise RuntimeError(f"Failed to create Tor session: {e}")


def test_connectivity(timeout: int = 10) -> Dict:
    """Test Tor connectivity by requesting check.torproject.org.
    Returns dict with success, reachable, message.
    """
    import requests

    if not is_running():
        return {"success": False, "reachable": False, "message": "Tor not running"}

    try:
        session = tor_session(timeout=timeout)
        resp = session.get("http://check.torproject.org", timeout=timeout)
        text = resp.text.lower()
        if resp.status_code == 200 and ("congratulations" in text or "tor" in text):
            return {"success": True, "reachable": True, "message": "Tor reachable"}
        return {"success": True, "reachable": False, "message": f"Unexpected response (status {resp.status_code})"}
    except Exception as e:
        return {"success": False, "reachable": False, "message": f"Connectivity error: {e}"}
