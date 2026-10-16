#!/usr/bin/env python3
"""raya_tooldesc.py — patch a Raya tool's FUNCTION DESCRIPTION, and nothing else.

Why this exists: a constraint the model keeps dropping out of a 1900-line prompt is far
stickier when it lives in the tool's own description, which is read at the moment of use
(root CLAUDE.md -> "Move the decision out of prose", ladder step 4). This script is the
sanctioned way to do that: it GETs the agent, edits ONE description string inside
tools.llm_tools[], PATCHes {"tools": ...} back, and re-GETs to prove the live object equals
what we sent. Everything else in the tool object -- api_details, headers, payload_template,
parameter schemas -- is deep-copied through untouched.

NEVER write the fetched tools object to disk: Raya tool snapshots embed live API keys and
this repo is public (see memory: secret-leak-e2e-snapshots).

Usage:
  python3 scripts/raya_tooldesc.py plan  <target> <tool_name> <suffix-file>
  python3 scripts/raya_tooldesc.py apply <target> <tool_name> <suffix-file>

The suffix file holds the text to APPEND to the existing description. Idempotent: if the
description already ends with that text, nothing is sent.
"""
import copy, json, os, sys, urllib.error, urllib.request

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_env = {}
for _l in open(os.path.join(REPO, "raya/.env")):
    _l = _l.strip()
    if "=" in _l and not _l.startswith("#"):
        k, v = _l.split("=", 1)
        _env[k.strip()] = v.strip().strip('"').strip("'")
RAYA = _env["RAYA_BASE_URL"].rstrip("/")
RTOK = _env["RAYA_API_TOKEN"]
AGENTS = json.load(open(os.path.join(REPO, "raya/agents.json")))["targets"]
ENV = _env.get("RAYA_ENV", "prod")


def uuid_for(target):
    for t in AGENTS:
        if t["id"] == target:
            u = (t.get("raya_agent_id") or {}).get(ENV, "")
            if not u:
                sys.exit(f"{target}: no {ENV} uuid in raya/agents.json")
            return u
    sys.exit(f"unknown target {target!r}")


def raya(path, method="GET", body=None):
    h = {"X-API-Key": RTOK, "User-Agent": "Mozilla/5.0", "Accept": "application/json"}
    data = None
    if body is not None:
        data = json.dumps(body).encode()
        h["Content-Type"] = "application/json"
    req = urllib.request.Request(RAYA + path, data=data, headers=h, method=method)
    try:
        with urllib.request.urlopen(req, timeout=120) as r:
            return r.status, json.loads(r.read() or b"{}")
    except urllib.error.HTTPError as e:
        return e.code, e.read()[:400].decode("utf8", "replace")


def main():
    mode, target, tool_name, suffix_file = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4]
    suffix = open(os.path.join(REPO, suffix_file), encoding="utf-8").read().strip()
    uuid = uuid_for(target)
    s, d = raya("/api/agent/" + uuid)
    if s != 200:
        sys.exit(f"GET failed {s}: {d}")
    d = d.get("data", d)
    tools = d.get("tools") or {}
    new = copy.deepcopy(tools)
    hit = None
    for tool in new.get("llm_tools") or []:
        fn = tool.get("function") or {}
        if fn.get("name") != tool_name:
            continue
        cur = fn.get("description") or ""
        if suffix in cur:
            print(f"{target}/{tool_name}: description already carries the suffix — nothing to do")
            return
        fn["description"] = (cur.rstrip() + " " + suffix).strip()
        hit = (cur, fn["description"])
    if not hit:
        sys.exit(f"{target}: tool {tool_name!r} not found")
    print(f"=== {target} / {tool_name}\n--- OLD ---\n{hit[0]}\n--- NEW ---\n{hit[1]}\n")
    if mode != "apply":
        print("(plan only — nothing sent)")
        return
    s2, r2 = raya("/api/agent/" + uuid, "PATCH", {"tools": new})
    s3, d3 = raya("/api/agent/" + uuid)
    d3 = d3.get("data", d3)
    match = json.dumps(d3.get("tools"), sort_keys=True) == json.dumps(new, sort_keys=True)
    print(f"PATCH={s2}  readback_matches={match}")
    if s2 != 200 or not match:
        sys.exit(1)
    print(f"OK — {target}/{tool_name} description updated")


if __name__ == "__main__":
    main()
