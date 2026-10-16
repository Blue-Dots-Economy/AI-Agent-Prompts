"""Parse `claude -p --output-format stream-json --verbose` stdout into the same
event dicts sim.py yields, so the manager treats live + simulated jobs identically."""
from __future__ import annotations
import json
from job_runner.rails import stage_for_tool, signature
from security import scrub


async def parse_stream(proc):
    """Async-iterate the child's stdout JSONL -> event dicts."""
    while True:
        line = await proc.stdout.readline()
        if not line:
            break
        line = line.decode(errors="replace").strip()
        if not line:
            continue
        try:
            ev = json.loads(line)
        except Exception:
            yield {"kind": "text", "text": scrub(line[:400])}
            continue
        t = ev.get("type")
        if t == "system" and ev.get("subtype") == "init":
            yield {"kind": "init", "session_id": ev.get("session_id"),
                   "model": ev.get("model"), "apiKeySource": ev.get("apiKeySource")}
        elif t == "assistant":
            for block in (ev.get("message", {}).get("content") or []):
                if block.get("type") == "text" and block.get("text"):
                    yield {"kind": "text", "text": scrub(block["text"])}
                elif block.get("type") == "tool_use":
                    name, inp = block.get("name"), block.get("input") or {}
                    yield {"kind": "tool", "tool": name,
                           "signature": scrub(signature(name, inp)),
                           "stage": stage_for_tool(name, inp), "is_error": False}
        elif t == "user":
            for block in (ev.get("message", {}).get("content") or []):
                if block.get("type") == "tool_result":
                    body = block.get("content")
                    txt = body if isinstance(body, str) else json.dumps(body)[:300]
                    yield {"kind": "tool_result", "is_error": bool(block.get("is_error")),
                           "text": scrub(txt[:300])}
        elif t == "result":
            yield {"kind": "result", "is_error": bool(ev.get("is_error")),
                   "summary": scrub((ev.get("result") or "")[:600]),
                   "subtype": ev.get("subtype"), "session_id": ev.get("session_id")}
