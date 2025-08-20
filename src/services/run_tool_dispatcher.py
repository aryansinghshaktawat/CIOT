"""Unified dark web tool dispatcher producing streaming progress events."""
from __future__ import annotations
import importlib
import time
from typing import Dict, Any, Generator

_TOOL_MODULES = {
    "TorBot": "src.services.darkweb_tools.torbot",
    "OnionScan": "src.services.darkweb_tools.onionscan",
    "Dark Scrape": "src.services.darkweb_tools.darkscrape",
    # Placeholder / stub implementations (graceful 'not installed' outcome)
    # Prefer real h8mail integration; fallback stub handled dynamically if import fails
    "h8mail": "src.services.darkweb_tools.h8mail",
    "Final Recon": "src.services.darkweb_tools.finalrecon_stub",
    "OSINT-SPY": "src.services.darkweb_tools.osint_spy_stub",
    "Fresh Onions": "src.services.darkweb_tools.fresh_onions_stub",
    "Breach Hunt": "src.services.darkweb_tools.breach_hunt_stub",
    "Bitcoin Analysis": "src.services.darkweb_tools.bitcoin_analysis_stub",
}

def run_tool(tool_name: str, target: str, config: Dict[str, Any] | None = None) -> Generator[Dict[str, Any], None, Dict[str, Any]]:
    """Dynamically run a tool module's run() generator.

    Yields dict events: {event: 'log', line: str} or {event: 'complete', result: dict}
    """
    config = config or {}
    started = time.time()
    if tool_name not in _TOOL_MODULES:
        # Should not occur unless UI list mismatches dispatcher; still handle gracefully.
        yield {"event": "log", "line": f"[!] Tool '{tool_name}' is not available in this build."}
        yield {"event": "complete", "result": {
            "tool": tool_name,
            "target": target,
            "started_at": time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(started)),
            "finished_at": time.strftime('%Y-%m-%d %H:%M:%S'),
            "log": ["Tool not available"],
            "findings": {"links": [], "emails": [], "btc": []}
        }}
        return

    module_path = _TOOL_MODULES[tool_name]
    try:
        mod = importlib.import_module(module_path)
    except Exception:  # noqa: BLE001
        # Fallback to stub if real module missing or has import error
        if tool_name == "h8mail":
            fallback = "src.services.darkweb_tools.h8mail_stub"
            mod = importlib.import_module(fallback)
            yield {"event": "log", "line": "[i] Real h8mail module unavailable; using stub."}
        else:
            raise
    if not hasattr(mod, 'run'):
        yield {"event": "log", "line": f"[!] Tool module missing run()"}
        return
    for event in mod.run(target, config):
        yield event
