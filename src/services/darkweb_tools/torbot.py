from __future__ import annotations
import time, re, os
from typing import Dict, Any, Generator, Set

# Basic regex patterns
ONION_RE = re.compile(r'^(?:https?://)?(?=.{62,64}$)([a-z2-7]{56})\.onion(?::\d{2,5})?(?:/.*)?$')
EMAIL_RE = re.compile(r'[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,10}')
BTC_RE = re.compile(r'\b(?:bc1|[13])[a-zA-HJ-NP-Z0-9]{25,39}\b')
HREF_RE = re.compile(r'href=["\']([^"\'# >]+)')


def _normalize_target(target: str) -> str:
    t = target.strip()
    if not t.startswith("http://") and not t.startswith("https://"):
        # Force http for onion
        t = "http://" + t
    return t.rstrip('/')


def run(target: str, config: Dict[str, Any]) -> Generator[Dict[str, Any], None, Dict[str, Any]]:
    """TorBot crawler with Tor session.
    Config flags:
      extract_emails (bool)
      check_live_status (bool)
      save_results (bool)  # handled by UI, just passed through
    """
    start = time.time()
    log = []
    findings = {"links": [], "emails": [], "btc": []}
    visited: Set[str] = set()
    max_pages = 5  # safety cap

    def emit(msg):
        ts = time.strftime('%H:%M:%S')
        line = f"[{ts}] {msg}"
        log.append(line)
        return {"event": "log", "line": line}

    # Validate onion
    if not ONION_RE.match(target):
        yield emit("Invalid v3 onion address – aborting")
        end = time.time()
        yield {"event": "complete", "result": {
            "tool": "TorBot",
            "target": target,
            "started_at": time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(start)),
            "finished_at": time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(end)),
            "log": log,
            "findings": findings
        }}
        return

    norm_target = _normalize_target(target)
    base_host = norm_target.split('//',1)[1].split('/',1)[0]

    yield emit("Initializing TorBot crawl via Tor session")

    # Acquire tor session
    try:
        from src.services.tor_service import tor_session, is_running
        if not is_running():
            yield emit("Tor not running on 9050 – attempting crawl anyway will fail")
        session = tor_session(timeout=20)
        session.headers.update({
            'User-Agent': 'CIOT-TorBot/1.0 (+OSINT)'
        })
    except Exception as e:
        yield emit(f"Failed to create Tor session: {e}")
        end = time.time()
        yield {"event": "complete", "result": {
            "tool": "TorBot",
            "target": target,
            "started_at": time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(start)),
            "finished_at": time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(end)),
            "log": log,
            "findings": findings
        }}
        return

    # Live status check (HEAD)
    if config.get('check_live_status'):
        try:
            resp = session.head(norm_target, timeout=15, allow_redirects=True)
            if resp.status_code < 400:
                yield emit(f"Live status: Reachable (HTTP {resp.status_code})")
            else:
                yield emit(f"Live status: Unreachable (HTTP {resp.status_code})")
        except Exception as e:
            yield emit(f"Live status: Unreachable ({e})")
        time.sleep(1)

    queue = [norm_target]

    while queue and len(visited) < max_pages:
        url = queue.pop(0)
        if url in visited:
            continue
        visited.add(url)
        try:
            yield emit(f"Fetching: {url}")
            resp = session.get(url, timeout=20)
            status = resp.status_code
            yield emit(f"Status {status} {url}")
            findings['links'].append(url)
            html = resp.text[:200000]  # cap

            # Extract links
            for m in HREF_RE.finditer(html):
                link = m.group(1)
                if link.startswith('#') or link.startswith('javascript:'):
                    continue
                if link.startswith('/'):
                    link = norm_target + link
                if base_host in link and link not in findings['links'] and link not in queue and ONION_RE.search(link):
                    queue.append(link.rstrip('/'))
            yield emit(f"Queue size: {len(queue)}")

            # Extract emails
            if config.get('extract_emails'):
                for e in set(EMAIL_RE.findall(html)):
                    if e not in findings['emails']:
                        findings['emails'].append(e)
                        yield emit(f"Email found: {e}")

            # Extract BTC addresses
            for b in set(BTC_RE.findall(html)):
                if b not in findings['btc']:
                    findings['btc'].append(b)
                    yield emit(f"BTC address: {b}")

        except Exception as e:
            yield emit(f"Fetch error: {e} ({url})")
        time.sleep(1)  # polite delay between requests

    yield emit("Crawl complete")

    end = time.time()
    yield {"event": "complete", "result": {
        "tool": "TorBot",
        "target": target,
        "started_at": time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(start)),
        "finished_at": time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(end)),
        "log": log,
        "findings": findings
    }}
