"""Real h8mail integration with graceful fallback.

If `h8mail` binary is absent, behaves like previous stub (guidance only).
When present, runs a JSON-enabled scan and parses breach entries.
"""
from __future__ import annotations
import json
import shutil
import subprocess
import time
from typing import Dict, Any, Generator, List


def _emit(log: List[str], message: str) -> Dict[str, Any]:
    line = f"[{time.strftime('%H:%M:%S')}] {message}"
    log.append(line)
    return {"event": "log", "line": line}


def run(target: str, config: Dict[str, Any] | None = None) -> Generator[Dict[str, Any], None, Dict[str, Any]]:
    config = config or {}
    start_ts = time.time()
    log: List[str] = []

    if "@" not in target:
        yield _emit(log, f"Target '{target}' is not a valid email for h8mail.")
        end_ts = time.time()
        yield {"event": "complete", "result": {
            "tool": "h8mail",
            "target": target,
            "started_at": time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(start_ts)),
            "finished_at": time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(end_ts)),
            "log": log,
            "findings": {"breaches": [], "emails": [], "raw": {"error": "invalid_email"}}
        }}
        return

    binary = shutil.which("h8mail")
    if not binary:
        yield _emit(log, "h8mail is not installed – providing graceful placeholder output.")
        yield _emit(log, "Install h8mail for breach enumeration: pip install h8mail")
        end_ts = time.time()
        yield {"event": "complete", "result": {
            "tool": "h8mail",
            "target": target,
            "started_at": time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(start_ts)),
            "finished_at": time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(end_ts)),
            "log": log,
            "findings": {"breaches": [], "emails": [target], "raw": {"installed": False}}
        }}
        return

    cmd = [binary, "-t", target, "--json"]
    yield _emit(log, f"Executing: {' '.join(cmd)}")
    try:
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=int(config.get("timeout", 300)))
    except subprocess.TimeoutExpired:
        yield _emit(log, "Timeout while running h8mail")
        end_ts = time.time()
        yield {"event": "complete", "result": {
            "tool": "h8mail",
            "target": target,
            "started_at": time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(start_ts)),
            "finished_at": time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(end_ts)),
            "log": log,
            "findings": {"breaches": [], "emails": [target], "raw": {"error": "timeout"}}
        }}
        return
    except Exception as e:  # noqa: BLE001
        yield _emit(log, f"Execution failure: {e}")
        end_ts = time.time()
        yield {"event": "complete", "result": {
            "tool": "h8mail",
            "target": target,
            "started_at": time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(start_ts)),
            "finished_at": time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(end_ts)),
            "log": log,
            "findings": {"breaches": [], "emails": [target], "raw": {"error": "execution_failure"}}
        }}
        return

    stdout = proc.stdout.strip()
    stderr = proc.stderr.strip()
    if stderr:
        yield _emit(log, f"stderr: {stderr[:200]}{'...' if len(stderr) > 200 else ''}")

    breaches: List[Dict[str, Any]] = []
    raw_json = None
    if stdout:
        try:
            raw_json = json.loads(stdout)
            yield _emit(log, "Parsed JSON output.")
            if isinstance(raw_json, list):
                for entry in raw_json:
                    if isinstance(entry, dict):
                        breaches.append(entry)
            elif isinstance(raw_json, dict):
                if 'breaches' in raw_json and isinstance(raw_json['breaches'], list):
                    breaches.extend(raw_json['breaches'])
                else:
                    breaches.append(raw_json)
        except json.JSONDecodeError:
            raw_json = {"raw_text": stdout[:5000]}
            yield _emit(log, "Non-JSON output captured.")
    else:
        yield _emit(log, "No output from h8mail")

    yield _emit(log, f"Breach entries: {len(breaches)}")

    end_ts = time.time()
    yield {"event": "complete", "result": {
        "tool": "h8mail",
        "target": target,
        "started_at": time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(start_ts)),
        "finished_at": time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(end_ts)),
        "log": log,
        "findings": {"breaches": breaches, "emails": [target], "raw": raw_json or {}}
    }}
