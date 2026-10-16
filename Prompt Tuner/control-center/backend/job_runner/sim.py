"""Simulation driver — replays a realistic Claude-Code job stream when no host
`claude` CLI is available, so the full pipeline (stream -> stages -> risk-gate ->
approve -> deploy -> sheet) is demonstrable. Emits the SAME event dicts the live
stream parser emits, and writes a real verdict.json the policy engine decides on."""
from __future__ import annotations
import asyncio
import json
import re
import time
from pathlib import Path

_TICK = 0.7  # seconds between simulated steps


def _classify(scope: dict) -> dict:
    """Pick a realistic verdict from the issue text (backend/runtime -> pause; else clean auto)."""
    i = scope.get("issue") or {}
    blob = f"{i.get('title','')} {i.get('type','')} {i.get('description','')}".lower()
    dpat = i.get("d_pattern")
    if re.search(r"\b404|backend|endpoint|invalid or missing|5\d\d|api\b", blob):
        return {"classification": "backend", "confidence": "high",
                "risk_flags": ["backend"], "repro_call_uuid": "7e5e1173",
                "target_ids": [scope.get("target_id")], "sibling_ports": [], "diff_stats": {"files": 0},
                "summary": "Tool returns 4xx with a well-formed payload — backend issue, not prompt-fixable. Flag the tracker, do not deploy."}
    if re.search(r"get_profile|tool.?adherence|ignore|not firing|runtime", blob):
        return {"classification": "runtime", "confidence": "medium",
                "risk_flags": ["runtime", "low-confidence"], "repro_call_uuid": "fa530906",
                "target_ids": [scope.get("target_id")], "sibling_ports": [], "diff_stats": {"files": 0},
                "summary": "Model ignores an instruction the prompt already states — runtime tool-adherence, needs a platform backstop, not more prose."}
    return {"classification": "prompt-fixable", "confidence": "high", "risk_flags": [],
            "repro_call_uuid": "b83e86de", "target_ids": [scope.get("target_id")],
            "sibling_ports": [], "diff_stats": {"files": 2, "additions": 6, "deletions": 2},
            "summary": f"Genuine prompt gap grounded in a real transcript; surgical additive fix on {scope.get('target_id')} + Kannada twin. Snapshotted, sync-checked, no contradiction."}


async def simulate(kind: str, scope: dict, artifacts_dir: Path):
    yield {"kind": "init", "session_id": f"sim-{int(time.time())}", "mode": "sim"}
    await asyncio.sleep(0.2)

    if kind in ("diagnose", "propose"):
        steps = [
            ("Find", "gsheets.py get 'All Issues'", "Pulled the open issue from the tracker."),
            ("Root-cause", "raya_call.py <agent_uuid> 20", "Pulled the real Raya transcript and read the offending turns."),
            ("Classify", "analysing tool_calls vs prompt", "Classifying against the transcript…"),
        ]
        v = _classify(scope)
        if v["classification"] == "prompt-fixable":
            steps += [
                ("Fix", "prompt-version.sh save (snapshot)", "Snapshotted the pre-fix prompt for rollback."),
                ("Fix", f"Edit KKB/…{scope.get('target_id','')}.md", "Applied the surgical fix (Hindi source) + mirrored to Kannada."),
                ("Verify", "raya_deploy.py diff <target>", "Reconciled vs live — in sync; ran sync-check parity + regression scan."),
            ]
        for stage, sig, text in steps:
            await asyncio.sleep(_TICK)
            yield {"kind": "tool", "tool": "Bash", "signature": sig, "stage": stage, "is_error": False}
            yield {"kind": "text", "text": text}
        artifacts_dir.mkdir(parents=True, exist_ok=True)
        (artifacts_dir / "verdict.json").write_text(json.dumps(v, indent=2))
        (artifacts_dir / "proposed-change.md").write_text(
            f"# Proposed change — {scope.get('target_id')}\n\n**Classification:** {v['classification']} "
            f"({v['confidence']} confidence)\n\n{v['summary']}\n\n"
            f"Grounded in Raya call `{v['repro_call_uuid']}`.\n")
        (artifacts_dir / "repro.txt").write_text(
            f"[simulated repro turns for call {v['repro_call_uuid']}]\n"
            "[assistant->TOOL] the offending tool call…\n[tool] the error/return that proves the bug…\n")
        (artifacts_dir / "diff.patch").write_text(
            "" if v["classification"] != "prompt-fixable"
            else "--- a/KKB/…\n+++ b/KKB/…\n@@\n+ (surgical additive rule)\n")
        await asyncio.sleep(_TICK)
        yield {"kind": "result", "is_error": False,
               "summary": f"Diagnose complete: {v['classification']} / {v['confidence']}. Verdict written."}

    elif kind == "deploy":
        for stage, sig, text in [
            ("Verify", "raya_deploy.py diff <target>", "Re-reconciled vs live — still in sync."),
            ("Deploy", "raya_deploy.py deploy <target> --yes", "Deployed (snapshot → name-guard → read-back verified)."),
            ("Verify", "raya_testrun.py (post-deploy verify)", "Fired a post-deploy verify call."),
            ("Sheet", "gsheets.py update 'All Issues'!B<row>", "Set the tracker status → Fixed for UAT."),
        ]:
            await asyncio.sleep(_TICK)
            yield {"kind": "tool", "tool": "Bash", "signature": sig, "stage": stage, "is_error": False}
            yield {"kind": "text", "text": text}
        await asyncio.sleep(_TICK)
        yield {"kind": "result", "is_error": False,
               "summary": "Deployed + tracker set to Fixed for UAT (≠ confirmed until a post-deploy call shows the fix)."}

    elif kind == "voice-test":
        for stage, sig, text in [
            ("Topology", "raya_testcall.py whoami", "Resolved tester + bot topology."),
            ("Persona", "raya_testcall.py persona …", "Loaded the persona onto the tester."),
            ("Language", "raya_testcall.py lang hi", "Matched tester language/voice."),
            ("Fire+dump", "raya_testrun.py …", "Fired the call, polled, dumped both legs."),
            ("Grade", "grading vs checklists", "Graded against generic + bot-specific checklists."),
        ]:
            await asyncio.sleep(_TICK)
            yield {"kind": "tool", "tool": "Bash", "signature": sig, "stage": stage, "is_error": False}
            yield {"kind": "text", "text": text}
        await asyncio.sleep(_TICK)
        yield {"kind": "result", "is_error": False, "summary": "Voice-test graded (simulated)."}
