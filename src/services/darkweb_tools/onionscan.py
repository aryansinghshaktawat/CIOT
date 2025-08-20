from __future__ import annotations
import time, re, json, shutil, subprocess
from typing import Dict, Any, Generator

ONION_RE = re.compile(r'^(?:https?://)?(?=.{62,64}$)([a-z2-7]{56})\.onion(?::\d{2,5})?(?:/.*)?$')

def run(target: str, config: Dict[str, Any]) -> Generator[Dict[str, Any], None, Dict[str, Any]]:
    """Invoke the onionscan binary and capture output.

    Behavior:
      * Validates onion v3 format.
      * If onionscan binary missing -> log notice and finish gracefully.
      * Runs: onionscan --json <onion> (if supported) else plain.
      * Captures stdout (and stderr merged) up to safety cap.
      * Attempts JSON parsing; raw text preserved under findings['raw']['onionscan'].
    """
    start = time.time()
    log: list[str] = []
    findings: Dict[str, Any] = {"links": [], "emails": [], "btc": [], "raw": {}}

    def emit(msg: str):
        ts = time.strftime('%H:%M:%S')
        line = f"[{ts}] {msg}"
        log.append(line)
        return {"event": "log", "line": line}

    # Validate
    if not ONION_RE.match(target):
        yield emit("Invalid onion address - aborting OnionScan")
        end = time.time()
        yield {"event": "complete", "result": {
            "tool": "OnionScan",
            "target": target,
            "started_at": time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(start)),
            "finished_at": time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(end)),
            "log": log,
            "findings": findings
        }}
        return

    yield emit("Starting OnionScan analysis")

    binary = shutil.which("onionscan")
    if not binary:
        yield emit("OnionScan not installed (binary 'onionscan' not found in PATH)")
        yield emit("Install: go install github.com/s-rah/onionscan@latest OR download release")
        end = time.time()
        yield {"event": "complete", "result": {
            "tool": "OnionScan",
            "target": target,
            "started_at": time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(start)),
            "finished_at": time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(end)),
            "log": log,
            "findings": findings
        }}
        return

    # Build command; many builds support --json flag, fallback if it fails.
    commands = [[binary, "--json", target], [binary, target]]
    captured = None
    for cmd in commands:
        try:
            yield emit(f"Executing: {' '.join(cmd)}")
            proc = subprocess.run(cmd, capture_output=True, text=True, timeout=180)
            out = (proc.stdout or "") + (proc.stderr or "")
            captured = out.strip()
            if proc.returncode == 0 or captured:
                break
        except subprocess.TimeoutExpired:
            yield emit("OnionScan timed out")
            captured = None
            break
        except Exception as e:
            yield emit(f"Execution error: {e}")
            captured = None
            break

    if captured is None:
        yield emit("No output captured from OnionScan")
    else:
        # Cap extremely large output
        if len(captured) > 200_000:
            captured = captured[:200_000] + "\n...[truncated]"
        parsed_json = None
        # Try JSON parsing (some versions print multiple lines JSON + logs)
        try:
            # Find first JSON object in output
            first_brace = captured.find('{')
            if first_brace != -1:
                json_candidate = captured[first_brace:]
                parsed_json = json.loads(json_candidate)
                yield emit("Parsed JSON output from OnionScan")
        except Exception:
            parsed_json = None
            yield emit("JSON parse failed; storing raw text")
        findings['raw']['onionscan'] = parsed_json if parsed_json is not None else captured

    # Minimal heuristic extraction (if JSON present) - e.g., related services or identified addresses
    try:
        if isinstance(findings['raw']['onionscan'], dict):
            data = findings['raw']['onionscan']
            # Example keys: 'hiddenService', 'related_onion_services', 'pgpKeys'
            rel = data.get('related_onion_services') or data.get('relatedOnionServices') or []
            for svc in rel:
                if isinstance(svc, str) and svc.endswith('.onion') and svc not in findings['links']:
                    findings['links'].append(svc)
            # Simple email extraction from raw JSON string form
            raw_text = json.dumps(data)
            for e in set(re.findall(r'[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\\.[A-Za-z]{2,10}', raw_text)):
                if e not in findings['emails']:
                    findings['emails'].append(e)
    except Exception:
        pass

    yield emit("OnionScan analysis complete")
    end = time.time()
    yield {"event": "complete", "result": {
        "tool": "OnionScan",
        "target": target,
        "started_at": time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(start)),
        "finished_at": time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(end)),
        "log": log,
        "findings": findings
    }}
