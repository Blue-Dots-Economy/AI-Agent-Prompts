#!/usr/bin/env python3
"""toolschema_parity.py — audit TOOL SCHEMAS across a sync family, not just prompt text.

Why this exists: on 2026-09-03 two separate live bugs came from a fix that lived in a tool
schema being applied to one bot and mirrored nowhere.

  * `duplicate_check` — the parameter the whole three-outcome apply logic keys on — existed on
    kkb-hi-signals ONLY. The other eleven bots' prompts instructed the model to send a parameter
    their tool schema did not define, so the logic could never run and every duplicate was
    reported as a technical fault.
  * The `ACTION_LIMIT_REACHED` -> already-applied mapping in the apply_job DESCRIPTION existed on
    kkb-hi-signals only, on 1 of 6 Signals bots.

`/sync-check` compares prompt text and would pass both of those days-long. A prompt and its tool
schema are one contract; auditing half of it is how this happened twice in one day.

Reports, per tool name, across the bots of a family: which bots define it, parameter sets,
`required` sets, enum values, and description digests -- and flags any bot that differs from the
family's majority. Read-only.

Usage:
  python3 scripts/toolschema_parity.py                 # every conversation bot, grouped by agent
  python3 scripts/toolschema_parity.py --family KKB    # one agent's bots
  python3 scripts/toolschema_parity.py --signals-only
Exit 1 if any parameter/required/enum difference is found (description drift is reported as info).
"""
import argparse, hashlib, json, os, sys, urllib.request
from concurrent.futures import ThreadPoolExecutor

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_env = {}
for _l in open(os.path.join(REPO, "raya/.env")):
    _l = _l.strip()
    if "=" in _l and not _l.startswith("#"):
        k, v = _l.split("=", 1); _env[k.strip()] = v.strip().strip('"').strip("'")
BASE = _env["RAYA_BASE_URL"].rstrip("/"); TOKEN = _env["RAYA_API_TOKEN"]


def agent(uuid):
    req = urllib.request.Request(BASE + "/api/agent/" + uuid,
                                 headers={"X-API-Key": TOKEN, "User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=90) as r:
        d = json.loads(r.read() or b"{}")
    return d.get("data", d)


def tools_of(d):
    out = {}
    for t in (d.get("tools") or {}).get("llm_tools") or []:
        fn = (t or {}).get("function") or {}
        n = fn.get("name")
        if not n:
            continue
        p = fn.get("parameters") or {}
        props = p.get("properties") or {}
        out[n] = {
            "params": sorted(props.keys()),
            "required": sorted(p.get("required") or []),
            "enums": {k: sorted(v.get("enum")) for k, v in props.items() if isinstance(v, dict) and v.get("enum")},
            "desc_sha": hashlib.sha256((fn.get("description") or "").encode()).hexdigest()[:8],
            "desc_len": len(fn.get("description") or ""),
        }
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--family", default=None, help="agent name, e.g. KKB")
    ap.add_argument("--signals-only", action="store_true")
    a = ap.parse_args()
    targets = [t for t in json.load(open(os.path.join(REPO, "raya/agents.json")))["targets"]
               if t.get("kind") == "conversation" and (t.get("raya_agent_id") or {}).get("prod")]
    if a.family:
        targets = [t for t in targets if (t.get("agent") or "").upper() == a.family.upper()]
    if a.signals_only:
        targets = [t for t in targets if (t.get("signals") or "signals" in t["id"])]

    def fetch(t):
        try:
            return t, tools_of(agent(t["raya_agent_id"]["prod"])), None
        except Exception as e:
            return t, {}, str(e)[:80]

    with ThreadPoolExecutor(max_workers=4) as ex:
        rows = list(ex.map(fetch, targets))

    errs = [(t["id"], e) for t, _, e in rows if e]
    for i, e in errs:
        print("  fetch failed: %-22s %s" % (i, e))

    fams = {}
    for t, tl, e in rows:
        if e:
            continue
        # Group by agent AND backend: Signals and legacy legitimately differ (phone_number vs
        # phoneNumber, acting_as_user_id, different profile field sets). Comparing across them
        # reports architecture as drift and buries the real thing.
        # Derive the backend the SAME way static_regression/build_fleet_manifest do: the
        # manifest's explicit `signals` flag first, the id substring only as a fallback. TRRAIN's
        # ids carry no "signals" token, so the substring test alone put a bot whose tools point at
        # gzb-signals into the "legacy" family and out of --signals-only entirely (2026-09-04).
        backend = "signals" if (t.get("signals") or "signals" in t["id"]) else "legacy"
        fams.setdefault("%s / %s" % (t.get("agent") or "?", backend), []).append((t["id"], tl))

    findings = 0
    for fam, bots in sorted(fams.items()):
        print("\n=== %s — %d bots" % (fam, len(bots)))
        names = sorted({n for _, tl in bots for n in tl})
        for n in names:
            have = [(i, tl[n]) for i, tl in bots if n in tl]
            missing = [i for i, tl in bots if n not in tl]
            sigs = {}
            for i, s in have:
                key = json.dumps([s["params"], s["required"], s["enums"]], sort_keys=True)
                sigs.setdefault(key, []).append(i)
            print("  %-18s on %d/%d bots%s" % (n, len(have), len(bots),
                  ("   (absent: " + ", ".join(missing) + ")") if missing else ""))
            if len(sigs) > 1:
                findings += 1
                print("     *** SCHEMA DIFFERS across the family:")
                for key, ids in sorted(sigs.items(), key=lambda kv: -len(kv[1])):
                    params, req, enums = json.loads(key)
                    print("       %-46s params=%s" % (",".join(ids)[:46], params))
                    print("       %-46s required=%s enums=%s" % ("", req, enums or "-"))
            descs = {}
            for i, s in have:
                descs.setdefault(s["desc_sha"], []).append((i, s["desc_len"]))
            if len(descs) > 1:
                print("     description drift (info): " + " | ".join(
                    "%s=%s" % (sha, ",".join("%s(%d)" % x for x in v)) for sha, v in descs.items()))
    print("\n%s" % ("SCHEMA PARITY CLEAN" if not findings else "SCHEMA PARITY FINDINGS: %d" % findings))
    sys.exit(1 if findings else 0)


if __name__ == "__main__":
    main()
