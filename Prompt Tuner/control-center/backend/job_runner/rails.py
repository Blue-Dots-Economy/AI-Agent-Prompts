"""Map a Claude Code tool invocation onto the canonical /bug-fix + /voice-test stage rail.
Pure functions — no I/O. Used by both the live stream parser and the hook."""
from __future__ import annotations
import re

# Ordered canonical rails (what the Job Console renders as the progress track).
BUGFIX_RAIL = ["Find", "Root-cause", "Classify", "Fix", "Verify", "Deploy", "Sheet", "Done"]
VOICETEST_RAIL = ["Topology", "Persona", "Language", "Fire+dump", "Grade", "Done"]

_RULES = [
    # (regex on a normalized "tool signature", stage)
    (r"gsheets\.py\s+(get|meta)", "Find"),
    (r"gsheets\.py\s+update", "Sheet"),
    (r"raya_call\.py|/api/call", "Root-cause"),
    (r"raya_deploy\.py\s+deploy", "Deploy"),
    (r"raya_deploy\.py\s+(diff|verify|status|reconcile|pull)", "Verify"),
    (r"prompt-version\.sh\s+save", "Fix"),
    (r"prompt-version\.sh\s+restore", "Verify"),
    (r"raya_testcall\.py\s+persona", "Persona"),
    (r"raya_testcall\.py\s+lang", "Language"),
    (r"raya_testrun\.py|raya_testcall\.py\s+call", "Fire+dump"),
    (r"sync-check|prompt-analyser", "Verify"),
]

_EDIT_PATH = re.compile(r"(KKB|DKB|Maya)[/ ].*\.md", re.I)


def stage_for_tool(tool_name: str, tool_input: dict) -> str | None:
    """Return the rail stage for a tool_use, or None if it doesn't map."""
    name = (tool_name or "")
    inp = tool_input or {}
    if name == "Bash":
        cmd = inp.get("command", "")
        for pat, stage in _RULES:
            if re.search(pat, cmd):
                return stage
        return None
    if name in ("Edit", "Write", "MultiEdit", "Update"):
        path = inp.get("file_path") or inp.get("path") or ""
        if _EDIT_PATH.search(path):
            return "Fix"
        if "verdict.json" in path or "proposed-change" in path or "repro" in path:
            return "Classify"
        return None
    if name in ("Read", "Grep", "Glob") and "verdict" not in str(inp):
        return None
    return None


def signature(tool_name: str, tool_input: dict) -> str:
    """Short human label for a tool call, secret-free (caller still scrubs)."""
    inp = tool_input or {}
    if tool_name == "Bash":
        return (inp.get("command", "") or "").split("&&")[0].strip()[:90]
    if tool_name in ("Edit", "Write", "MultiEdit"):
        return f"{tool_name} {inp.get('file_path', '')}"
    return tool_name
