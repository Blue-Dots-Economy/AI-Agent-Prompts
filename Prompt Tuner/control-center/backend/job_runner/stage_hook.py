"""PostToolUse hook — wired into a per-job settings.json via `claude --settings`.
Claude invokes this after each tool call; it maps the tool to a rail stage and
appends one structured line to runs/<job_id>/stage-events.jsonl (the authoritative
ordered rail, resilient to stream-json schema drift). Reads hook JSON on stdin."""
from __future__ import annotations
import json
import os
import sys
import time
from pathlib import Path

# make sibling imports work when invoked as a bare script by claude
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
try:
    from job_runner.rails import stage_for_tool, signature
except Exception:
    from rails import stage_for_tool, signature  # type: ignore


def main():
    try:
        data = json.load(sys.stdin)
    except Exception:
        return
    tool = data.get("tool_name") or data.get("toolName") or ""
    tinp = data.get("tool_input") or data.get("toolInput") or {}
    stage = stage_for_tool(tool, tinp)
    runs_dir = os.environ.get("CC_JOB_EVENTS")
    if not runs_dir:
        return
    ev = {
        "seq": int(time.time() * 1000),
        "ts": time.strftime("%H:%M:%S"),
        "tool": tool,
        "signature": signature(tool, tinp)[:120],
        "stage": stage,
        "is_error": bool(data.get("is_error")),
    }
    with open(runs_dir, "a") as f:
        f.write(json.dumps(ev) + "\n")


if __name__ == "__main__":
    main()


def write_settings(settings_path: Path, hook_script: Path, events_file: Path):
    """Write a per-job settings.json that fires this hook after every tool use."""
    settings = {
        "hooks": {
            "PostToolUse": [{
                "matcher": "*",
                "hooks": [{
                    "type": "command",
                    "command": f'CC_JOB_EVENTS="{events_file}" python3 "{hook_script}"',
                }],
            }],
        }
    }
    settings_path.write_text(json.dumps(settings, indent=2))
