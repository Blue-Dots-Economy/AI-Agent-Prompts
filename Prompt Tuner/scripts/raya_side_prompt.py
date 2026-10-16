#!/usr/bin/env python3
"""raya_side_prompt.py — deploy an agent's MEMORY or OUTPUT prompt.

Memory and output prompts are not separate Raya agents: every conversation agent carries its
own `memory_instructions` / `output_instructions`. raya/agents.json's kkb-memory / kkb-output
rows therefore have no uuid of their own, and `raya_deploy.py` cannot push them. This script
does: it PATCHes the one field on a named CONVERSATION target's agent and verifies the change
against BOTH the PATCH response and a fresh GET.

Usage:
  python3 scripts/raya_side_prompt.py <mode:memory|output> <conversation-target> <file> [--yes]

e.g.  python3 scripts/raya_side_prompt.py output kkb-hi-signals "KKB/KKB Output.md" --yes
"""
import hashlib, json, os, sys, urllib.error, urllib.request

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_env = {}
for _l in open(os.path.join(REPO, "raya/.env")):
    _l = _l.strip()
    if "=" in _l and not _l.startswith("#"):
        k, v = _l.split("=", 1)
        _env[k.strip()] = v.strip().strip('"').strip("'")
BASE = _env["RAYA_BASE_URL"].rstrip("/"); KEY = _env["RAYA_API_TOKEN"]
ENV = _env.get("RAYA_ENV", "prod")
FIELD = {"memory": "memory_instructions", "output": "output_instructions"}


def raya(path, method="GET", body=None):
    h = {"X-API-Key": KEY, "User-Agent": "Mozilla/5.0", "Accept": "application/json"}
    data = json.dumps(body).encode() if body is not None else None
    if data is not None:
        h["Content-Type"] = "application/json"
    req = urllib.request.Request(BASE + path, data=data, headers=h, method=method)
    try:
        with urllib.request.urlopen(req, timeout=120) as r:
            return r.status, json.loads(r.read() or b"{}")
    except urllib.error.HTTPError as e:
        return e.code, e.read()[:400].decode("utf8", "replace")


def main():
    mode, target, path = sys.argv[1], sys.argv[2], sys.argv[3]
    yes = "--yes" in sys.argv
    field = FIELD[mode]
    targets = json.load(open(os.path.join(REPO, "raya/agents.json")))["targets"]
    row = next((t for t in targets if t["id"] == target), None)
    if not row:
        sys.exit(f"unknown target {target!r}")
    uuid = (row.get("raya_agent_id") or {}).get(ENV, "")
    if not uuid:
        sys.exit(f"{target}: no {ENV} uuid")
    text = open(os.path.join(REPO, path), encoding="utf-8").read()
    s, live = raya("/api/agent/" + uuid)
    if s != 200:
        sys.exit(f"GET failed {s}: {live}")
    live = live.get("data", live)
    cur = live.get(field) or ""
    name = live.get("name")
    for tok in row.get("expected_name_contains") or []:
        if tok.lower() not in (name or "").lower():
            sys.exit(f"WRONG TARGET GUARD: live agent name {name!r} lacks {tok!r}")
    sh = lambda x: hashlib.sha256(x.encode()).hexdigest()[:8]
    print(f"{target} ({name})  {field}: live {len(cur)}B sha {sh(cur)}  ->  local {len(text)}B sha {sh(text)}")
    if cur.strip() == text.strip():
        print("already identical — nothing to do"); return
    if not yes:
        print("(dry run — pass --yes to push)"); return
    s2, r2 = raya("/api/agent/" + uuid, "PATCH", {field: text, **({"memory_enabled": True} if mode == "memory" else {})})
    if s2 != 200:
        sys.exit(f"PATCH failed {s2}: {r2}")
    echoed = (r2.get("data", r2) or {}).get(field) or ""
    s3, d3 = raya("/api/agent/" + uuid)
    got = ((d3.get("data", d3) or {}).get(field) or "") if s3 == 200 else ""
    print(f"PATCH=200  patch_echo_matches={echoed.strip() == text.strip()}  get_readback_matches={got.strip() == text.strip()}")
    if echoed.strip() != text.strip() and got.strip() != text.strip():
        sys.exit("NEITHER the PATCH echo NOR the GET matched — treat as NOT deployed")
    print(f"DEPLOYED {field} -> {target}")


if __name__ == "__main__":
    main()
