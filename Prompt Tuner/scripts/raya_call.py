#!/usr/bin/env python3
"""Dump recent Raya calls for an agent uuid, INCLUDING tool-call arguments.

Usage: python3 scripts/raya_call.py <agent_uuid> [limit] [offset]

Prints, per call: created_at, caller_no/to_number, agent_args (new_seeker/contact_phone),
call_output flags, and the full transcript — CRUCIALLY the tool CALLS
(function name + arguments the model sent) and the linked tool RESULTS/errors.

Why this exists: a call_transcript turn that MAKES a tool call has content=null and the
real payload in `tool_calls[].function.arguments`. A reader that prints only `content`
misses every payload bug (e.g. apply_job sent profile_id="5051", the numeric id, instead
of the profileId UUID). See .claude/skills/bug-fix/SKILL.md "Read the transcript PROPERLY".
"""
import json, sys, os, urllib.request

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
env = {}
for line in open(os.path.join(REPO, "raya/.env")):
    line = line.strip()
    if "=" in line and not line.startswith("#"):
        k, v = line.split("=", 1); env[k.strip()] = v.strip()
BASE = env.get("RAYA_BASE_URL", "").rstrip("/"); KEY = env.get("RAYA_API_TOKEN", "")


def get(path):
    req = urllib.request.Request(BASE + path, headers={"X-API-Key": KEY, "User-Agent": "Mozilla/5.0"})
    return json.load(urllib.request.urlopen(req, timeout=30))


def main():
    if len(sys.argv) < 2 or sys.argv[1].startswith("-"):
        sys.exit(__doc__)
    uuid = sys.argv[1]
    limit = int(sys.argv[2]) if len(sys.argv) > 2 else 6
    offset = int(sys.argv[3]) if len(sys.argv) > 3 else 0
    d = get(f"/api/call?agent_id={uuid}&limit={limit}&offset={offset}")
    calls = d.get("calls") or d.get("data") or []
    print(f"### {len(calls)} calls for {uuid} (offset {offset})")
    for c0 in calls:
        c = get(f"/api/call/{c0['uuid']}")
        aa = c.get("agent_args") or {}
        co = c.get("call_output") or {}
        tr = c.get("call_transcript") or []
        print("\n" + "=" * 72)
        print(f"call {c0.get('uuid')} | {c.get('created_at')} | dur={c.get('call_duration')} "
              f"| caller={c.get('caller_no')} to={c.get('to_number')}")
        # Print the FULL agent_args and call_output, not a hand-picked few (2026-08-05). These were
        # hard-coded to three KKB-era keys (new_seeker / drop_reason / applied_to_job /
        # mpl_presented), so for any other bot the inputs and outputs read as absent. That matters:
        # the repo's own rule is to root-cause a report against BOTH the transcript AND the call's
        # input args before touching a prompt — you cannot do that if the args are not shown, and a
        # real bug was once mis-filed as a bot fault when the jobs had been sent in the wrong field.
        # Long values are truncated per key so a big ${recommendations} list stays readable.
        def _brief(v, cap=220):
            s = json.dumps(v, ensure_ascii=False) if not isinstance(v, str) else v
            return s if len(s) <= cap else s[:cap] + f"… (+{len(s) - cap} chars)"
        print("agent_args:" + ("" if aa else " (none)"))
        for k in sorted(aa):
            print(f"    {k} = {_brief(aa[k])}")
        print("call_output:" + ("" if co else " (none)"))
        for k in sorted(co):
            print(f"    {k} = {_brief(co[k])}")
        for t in tr:
            role = t.get("role")
            for tc in (t.get("tool_calls") or []):
                fn = tc.get("function") or {}
                print(f"[{role} → TOOL_CALL] {fn.get('name')}({fn.get('arguments')})")
            content = t.get("content")
            if content:
                content = content if role == "tool" else str(content).replace("\n", " ")
                print(f"[{role}] {content[:400]}")


if __name__ == "__main__":
    main()
