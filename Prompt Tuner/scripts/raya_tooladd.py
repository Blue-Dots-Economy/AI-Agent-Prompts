#!/usr/bin/env python3
"""raya_tooladd.py — add (or re-sync) ONE whole tool on a Raya agent.

Why this exists. `raya_tooldesc.py` patches a description and `raya_toolparam.py` patches a
parameter, but a genuinely new capability needs a new entry in `tools.llm_tools` — and doing that by
hand in the console is exactly the kind of unrecorded change `/raya-reconcile` exists to catch.

The api_details (url + auth headers) are **cloned from an existing tool on the SAME agent**, named by
`clone_api_from` in the spec. That is deliberate: the spec file carries no url and no key, so it is
safe to commit, and the new tool is guaranteed to hit the same backend as its siblings.

Everything already on the agent is deep-copied through untouched. NEVER write the fetched tools
object to disk: Raya tool snapshots embed live API keys and this repo is public
(see memory: secret-leak-e2e-snapshots).

Usage:
  python3 scripts/raya_tooladd.py plan  <target> <spec.json>
  python3 scripts/raya_tooladd.py apply <target> <spec.json>
  python3 scripts/raya_tooladd.py remove <target> <spec.json>   # takes the spec's tool off the agent

<spec.json>:
  {
    "name": "record_consent",
    "description": "...",
    "clone_api_from": "update_profile",     # existing tool whose url+headers to reuse
    "method": "POST",
    "parameters": { ...JSON Schema... },
    "payload_template": { ... }
  }
Idempotent: re-running with an unchanged spec sends nothing.
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


def summarise(tool):
    """One-line, KEY-FREE summary of a tool object (never print api_details.header)."""
    fn, ap = tool.get("function") or {}, tool.get("api_details") or {}
    return {
        "name": fn.get("name"),
        "required": (fn.get("parameters") or {}).get("required"),
        "properties": sorted(((fn.get("parameters") or {}).get("properties") or {}).keys()),
        "method": ap.get("method"),
        "url_host": (ap.get("url") or "").split("//")[-1].split("/")[0],
        "payload_keys": sorted((ap.get("payload_template") or {}).keys()),
    }


def main():
    mode, target, spec_path = sys.argv[1], sys.argv[2], sys.argv[3]
    spec = json.load(open(os.path.join(REPO, spec_path), encoding="utf-8"))
    name = spec["name"]
    uuid, row = uuid_for(target)
    s, live = raya("/api/agent/" + uuid)
    if s != 200:
        sys.exit(f"GET failed {s}: {live}")
    live = live.get("data", live)
    for tok in row.get("expected_name_contains") or []:
        if tok.lower() not in (live.get("name") or "").lower():
            sys.exit(f"WRONG TARGET GUARD: live name {live.get('name')!r} lacks {tok!r}")
    tools = copy.deepcopy(live.get("tools") or {})
    llm = tools.setdefault("llm_tools", [])

    if mode == "remove":                      # take ONE tool off the agent; everything else untouched
        keep = [t for t in llm if (t.get("function") or {}).get("name") != name]
        if len(keep) == len(llm):
            print(f"{target}: tool {name!r} not present — nothing to remove"); return
        tools["llm_tools"] = keep
        s2, r2 = raya("/api/agent/" + uuid, "PATCH", {"tools": tools})
        s3, d3 = raya("/api/agent/" + uuid)
        d3 = d3.get("data", d3)
        match = json.dumps(d3.get("tools"), sort_keys=True) == json.dumps(tools, sort_keys=True)
        print(f"PATCH={s2}  readback_matches={match}  tools now: {[(t.get('function') or {}).get('name') for t in keep]}")
        if s2 != 200 or not match:
            sys.exit(1)
        return

    donor = next((t for t in llm if (t.get("function") or {}).get("name") == spec["clone_api_from"]), None)
    if donor is None:
        sys.exit(f"{target}: clone_api_from tool {spec['clone_api_from']!r} not found — cannot clone url/headers")
    api = copy.deepcopy(donor["api_details"])
    api["method"] = spec.get("method", api.get("method", "POST"))
    api["payload_template"] = copy.deepcopy(spec["payload_template"])
    # `path_override` keeps the donor's scheme+host+auth headers but swaps the path -- needed for a
    # tool on a DIFFERENT service of the same instance (e.g. /signals-search/v1/search vs
    # /api/v1/...). The key still never touches the repo: it is cloned from the live donor tool.
    if spec.get("path_override"):
        from urllib.parse import urlsplit
        u = urlsplit(api["url"])
        api["url"] = f"{u.scheme}://{u.netloc}{spec['path_override']}"
    for k in spec.get("drop_headers") or []:
        (api.get("header") or {}).pop(k, None)

    new_tool = {
        "type": donor.get("type", "function"),
        "function": {"name": name, "description": spec["description"], "parameters": spec["parameters"]},
        "api_details": api,
    }

    existing = next((i for i, t in enumerate(llm) if (t.get("function") or {}).get("name") == name), None)
    if existing is None:
        llm.append(new_tool)
        print(f"=== {target}: ADD tool {name!r} (api cloned from {spec['clone_api_from']!r})")
    else:
        print(f"=== {target}: RE-SYNC existing tool {name!r}")
        print("  was:", json.dumps(summarise(llm[existing])))
        llm[existing] = new_tool
    print("  now:", json.dumps(summarise(new_tool)))
    print("  tools on agent:", [(t.get("function") or {}).get("name") for t in llm])

    if json.dumps(tools, sort_keys=True) == json.dumps(live.get("tools"), sort_keys=True):
        print("no change — already current")
        return
    if mode != "apply":
        print("(plan only — nothing sent)")
        return
    s2, r2 = raya("/api/agent/" + uuid, "PATCH", {"tools": tools})
    s3, d3 = raya("/api/agent/" + uuid)
    d3 = d3.get("data", d3)
    match = json.dumps(d3.get("tools"), sort_keys=True) == json.dumps(tools, sort_keys=True)
    print(f"PATCH={s2}  readback_matches={match}")
    if s2 != 200 or not match:
        print("  response:", r2 if isinstance(r2, str) else json.dumps(r2)[:300])
        sys.exit(1)
    print(f"OK — {target}: tool {name!r} live")


if __name__ == "__main__":
    main()
