#!/usr/bin/env python3
"""raya_toolparam.py — add or update ONE parameter on a Raya tool's function schema.

Why this exists. A decision the model keeps dropping out of a 1900-line prompt becomes far stickier
when it is a **required tool argument**: the model cannot emit the call without filling it in, so the
check happens at the moment of use instead of being recalled from prose (root CLAUDE.md → escalation
ladder step 4, "a constraint expressible in the tool schema belongs in the tool schema"). It also
leaves a machine-readable audit trail — the value shows up in `tool_calls[].function.arguments`, so a
regression detector can compare what the model ASSERTED against what the API then returned.

A parameter that is NOT referenced by `api_details.payload_template` is collected but never sent —
`hold_message` already works exactly this way, so declaring one is safe.

Everything else in the tool object (api_details, headers, payload_template, the other parameters) is
deep-copied through untouched. NEVER write the fetched tools object to disk: Raya tool snapshots
embed live API keys and this repo is public.

Usage:
  python3 scripts/raya_toolparam.py plan  <target> <tool_name> <param.json>
  python3 scripts/raya_toolparam.py apply <target> <tool_name> <param.json>

<param.json> is {"name": "...", "required": true|false, "schema": {...}} where `schema` is the JSON
Schema fragment for the parameter (type / enum / description).
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
ENV = _env.get("RAYA_ENV", "prod")
AGENTS = json.load(open(os.path.join(REPO, "raya/agents.json")))["targets"]


def uuid_for(target):
    for t in AGENTS:
        if t["id"] == target:
            u = (t.get("raya_agent_id") or {}).get(ENV, "")
            if not u:
                sys.exit(f"{target}: no {ENV} uuid in raya/agents.json")
            return u, t
    sys.exit(f"unknown target {target!r}")


def raya(path, method="GET", body=None):
    h = {"X-API-Key": RTOK, "User-Agent": "Mozilla/5.0", "Accept": "application/json"}
    data = json.dumps(body).encode() if body is not None else None
    if data is not None:
        h["Content-Type"] = "application/json"
    req = urllib.request.Request(RAYA + path, data=data, headers=h, method=method)
    try:
        with urllib.request.urlopen(req, timeout=120) as r:
            return r.status, json.loads(r.read() or b"{}")
    except urllib.error.HTTPError as e:
        return e.code, e.read()[:400].decode("utf8", "replace")


def main():
    mode, target, tool_name, spec_path = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4]
    spec = json.load(open(os.path.join(REPO, spec_path), encoding="utf-8"))
    pname, pschema, preq = spec["name"], spec["schema"], bool(spec.get("required"))
    uuid, row = uuid_for(target)
    s, live = raya("/api/agent/" + uuid)
    if s != 200:
        sys.exit(f"GET failed {s}: {live}")
    live = live.get("data", live)
    for tok in row.get("expected_name_contains") or []:
        if tok.lower() not in (live.get("name") or "").lower():
            sys.exit(f"WRONG TARGET GUARD: live name {live.get('name')!r} lacks {tok!r}")
    new = copy.deepcopy(live.get("tools") or {})
    hit = False
    for tool in new.get("llm_tools") or []:
        fn = tool.get("function") or {}
        if fn.get("name") != tool_name:
            continue
        params = fn.setdefault("parameters", {"type": "object"})
        props = params.setdefault("properties", {})
        req = params.setdefault("required", [])
        before = json.dumps(props.get(pname), sort_keys=True)
        props[pname] = pschema
        if preq and pname not in req:
            req.append(pname)
        if not preq and pname in req:
            req.remove(pname)
        after = json.dumps(props[pname], sort_keys=True)
        hit = True
        print(f"=== {target} / {tool_name} / {pname}")
        print(f"  was: {before}")
        print(f"  now: {after}")
        print(f"  required: {pname in req}   (all required: {req})")
    if not hit:
        sys.exit(f"{target}: tool {tool_name!r} not found")
    if json.dumps(new, sort_keys=True) == json.dumps(live.get("tools"), sort_keys=True):
        print("no change — already current")
        return
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
    print(f"OK — {target}/{tool_name} parameter {pname!r} updated")


if __name__ == "__main__":
    main()
