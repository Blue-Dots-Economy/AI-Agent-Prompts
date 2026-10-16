"""Risk-gate policy: read Job A's verdict.json and decide whether to auto-deploy
(Job B) or pause for human approval. 'Full autonomous unless there are risks.'"""
from __future__ import annotations
import json
from pathlib import Path

# any of these flags -> pause (awaiting-approval) instead of auto-deploy
PAUSE_FLAGS = {
    "reconcile-drift", "regression", "broad-propagation", "large-diff",
    "irreversible-config", "no-repro", "low-confidence",
}


def decide(verdict_path: Path) -> dict:
    """Returns {auto: bool, reason: str, flags: [...], classification, verdict}."""
    if not Path(verdict_path).exists():
        return {"auto": False, "reason": "no verdict produced by the diagnose job", "flags": ["no-verdict"], "verdict": None}
    try:
        v = json.loads(Path(verdict_path).read_text())
    except Exception as e:
        return {"auto": False, "reason": f"unreadable verdict ({e})", "flags": ["bad-verdict"], "verdict": None}

    cls = (v.get("classification") or "").lower()
    conf = (v.get("confidence") or "").lower()
    flags = list(v.get("risk_flags") or [])

    # not prompt-fixable -> never deploy; the diagnose job should have flagged the sheet class
    if cls and cls != "prompt-fixable":
        return {"auto": False, "reason": f"classified {cls} — not a prompt fix (flag the tracker, do not deploy)",
                "flags": flags or [cls], "classification": cls, "verdict": v}
    if conf == "low":
        flags.append("low-confidence")
    if v.get("sibling_ports"):
        # routine same-bug KKB<->Maya ports are standard; only pause if the diagnose job itself flagged broad-propagation
        pass
    hit = sorted(set(flags) & PAUSE_FLAGS)
    if hit:
        return {"auto": False, "reason": "risk tripwire(s): " + ", ".join(hit),
                "flags": flags, "classification": cls, "verdict": v}
    return {"auto": True, "reason": "clean prompt-fix, no tripwire — auto-deploy",
            "flags": flags, "classification": cls, "verdict": v}
