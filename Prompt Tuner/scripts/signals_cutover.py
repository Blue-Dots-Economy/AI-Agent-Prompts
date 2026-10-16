#!/usr/bin/env python3
"""signals_cutover.py — repoint the Signals bots at the region-split production instances.

Ghaziabad instance serves the HINDI bots; Dharwad serves the KANNADA bots. Credentials live in
the git-ignored secrets/signals-prod/creds.json and are never printed.

Beyond the base URL + headers, the new instances tightened validation, so this also fixes the
payloads/schemas that would otherwise 400 (all verified against the live API):
  * item_state.age  must be an INTEGER  -> declare the `age` tool param as integer
  * item_state.positions must be an INTEGER -> declare `positions` as integer
  * job_posting_1.0 rejects `title`     -> drop it from create_job/update_job payload templates
  * educationCategory enum changed      -> 'ITI / Other Vocational Trainings' is now 'ITI',
                                           'Polytechnic / Diploma' is now 'Diploma'

Usage:
  python3 scripts/signals_cutover.py plan            # show what would change, write nothing
  python3 scripts/signals_cutover.py apply [target]  # PATCH live agents (verifies read-back)
  python3 scripts/signals_cutover.py verify          # read live config back and check it
"""
import copy, json, os, sys, time, urllib.request, urllib.error

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# scheme-qualified on purpose: the bare host is a SUBSTRING of the new hosts
# (gzb-signals.bluedotseconomy.org), so a bare match is neither correct nor idempotent.
OLD_HOST = "https://signals.bluedotseconomy.org"

AGENTS = {  # target -> (raya agent uuid, instance)
    "kkb-hi-signals":     ("115b38a5-42ef-4082-be69-84a871bb226a", "ghaziabad"),
    "kkb-hi-in-signals":  ("3f521174-574d-43ca-a9be-081849373c18", "ghaziabad"),
    "maya-hi-signals":    ("904f333f-1919-4523-a51d-b22ba382dd22", "ghaziabad"),
    "maya-hi-in-signals": ("1c24feda-a584-4012-a865-fa8f950089df", "ghaziabad"),
    "dkb-hi-signals":     ("fabda71d-af75-4ddd-8cf1-fa35c827f753", "ghaziabad"),
    "trrain-hi-out":      ("cf39a59a-3b24-4842-ba03-4248ec245aa1", "ghaziabad"),
    "kkb-kn-signals":     ("33037201-78ce-405d-b509-a3b6934e20f1", "dharwad"),
    "kkb-kn-in-signals":  ("f38da775-c572-4a50-9340-fe1f42c43901", "dharwad"),
    "dkb-kn-signals":     ("847a85e2-c5c8-4727-9918-f1db9efad05d", "dharwad"),
    "trrain-kn-out":      ("dfeda883-3d2d-4a74-a0b5-1a47fdde2282", "dharwad"),
}

EDU_FIX = [("ITI / Other Vocational Trainings", "ITI"), ("Polytechnic / Diploma", "Diploma")]

# otherHelpNeeded changed enum entirely on the new instances (verified against live data +
# rejected/accepted probes on 2026-08-28). Old: Training|Accommodation|Travel|Other.
OTHER_HELP_DESC = ("Other help the caller needs to get work. Send as a JSON ARRAY. EXACT enum only: "
                   "'Skilling & Vocational Training' | 'Other Support (Accommodation / Travel)'. "
                   "OMIT entirely if they need none (there is no 'None' value).")

# The new instances validate types strictly. Raya does whole-value typed substitution -- a
# placeholder whose PARAM is declared integer/array is substituted as a real number/array -- so
# the fix is the declared param type, not the template text. Verified live on 2026-08-28:
# declaring `age` integer moved the API error from "must be integer" to "must be array".
ARRAY_PARAMS = ("otherHelpNeeded", "languageSpoken", "natureOfJobsInterestedIn")
# item_state entries hardcoded in the template that must be JSON arrays, not bare strings
ARRAY_LITERALS = ("natureOfJobsInterestedIn", "languageSpoken", "otherHelpNeeded")

_env = {}
for _l in open(os.path.join(REPO, "raya/.env")):
    _l = _l.strip()
    if "=" in _l and not _l.startswith("#"):
        k, v = _l.split("=", 1)
        _env[k.strip()] = v.strip().strip('"').strip("'")
RAYA = _env["RAYA_BASE_URL"].rstrip("/")
RTOK = _env["RAYA_API_TOKEN"]
CREDS = json.load(open(os.path.join(REPO, "secrets/signals-prod/creds.json")))["instances"]


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
        return e.code, e.read()[:300].decode("utf8", "replace")


def transform(tools, inst):
    """Return (new_tools, list_of_change_descriptions)."""
    c = CREDS[inst]
    new_host = c["baseUrl"].rstrip("/")
    t = copy.deepcopy(tools)
    changes = []
    for tool in t.get("llm_tools") or []:
        fn = tool.get("function") or {}
        name = fn.get("name")
        ad = tool.get("api_details") or {}
        # 1. base URL on the endpoint
        if isinstance(ad.get("url"), str) and OLD_HOST in ad["url"]:
            ad["url"] = ad["url"].replace(OLD_HOST, new_host)
            changes.append(f"{name}: url -> {new_host}")
        # 2. headers
        h = ad.get("header") or {}
        for hk in list(h):
            if hk.lower() == "x-api-key" and h[hk] != c["apiKey"]:
                h[hk] = c["apiKey"]; changes.append(f"{name}: x-api-key -> {inst}")
            elif hk.lower() == "x-acting-org-id" and h[hk] != c["orgId"]:
                h[hk] = c["orgId"]; changes.append(f"{name}: x-acting-org-id -> {inst}")
        # 3. any URL embedded in the payload template (apply_job item_instance_url)
        pt = ad.get("payload_template")
        def walk(o, path=""):
            if isinstance(o, dict):
                for k, v in list(o.items()):
                    if isinstance(v, str) and OLD_HOST in v:
                        o[k] = v.replace(OLD_HOST, new_host)
                        changes.append(f"{name}: payload{path}.{k} -> {new_host}")
                    else:
                        walk(v, f"{path}.{k}")
            elif isinstance(o, list):
                for i, v in enumerate(o):
                    walk(v, f"{path}[{i}]")
        if pt:
            walk(pt)
            # 4. job_posting_1.0 no longer allows `title`
            st = pt.get("item_state")
            if isinstance(st, dict) and pt.get("item_type") == "job_posting_1.0" and "title" in st:
                st.pop("title")
                changes.append(f"{name}: dropped item_state.title (rejected by new schema)")
            # hardcoded literals that must be arrays (e.g. natureOfJobsInterestedIn: 'Full-time')
            if isinstance(st, dict):
                for k in ARRAY_LITERALS:
                    v = st.get(k)
                    if isinstance(v, str) and not v.startswith("{{"):
                        st[k] = [v]
                        changes.append(f"{name}: item_state.{k} -> array literal")
        # 5/6. parameter types + enum text
        props = ((fn.get("parameters") or {}).get("properties") or {})
        # array-typed params: declare as array so Raya substitutes a real JSON array
        for pname in ARRAY_PARAMS:
            if pname in props and props[pname].get("type") != "array":
                props[pname]["type"] = "array"
                props[pname]["items"] = {"type": "string"}
                d = props[pname].get("description", "")
                props[pname]["description"] = (d + " Send as a JSON ARRAY of strings, e.g. [\"Training\"].").strip()
                changes.append(f"{name}: param {pname} -> array")
        for pname in ("age", "positions"):
            if pname in props and props[pname].get("type") != "integer":
                props[pname]["type"] = "integer"
                d = props[pname].get("description", "")
                props[pname]["description"] = (d + " Send as a NUMBER, not a string.").strip()
                changes.append(f"{name}: param {pname} -> integer")
        if "otherHelpNeeded" in props and props["otherHelpNeeded"].get("description") != OTHER_HELP_DESC:
            props["otherHelpNeeded"]["description"] = OTHER_HELP_DESC
            changes.append(f"{name}: param otherHelpNeeded enum replaced")
        for pname, p in props.items():
            if pname == "otherHelpNeeded":
                continue
            d = p.get("description")
            if isinstance(d, str):
                nd = d
                for a, b in EDU_FIX:
                    nd = nd.replace(f"'{a}'", f"'{b}'")
                if nd != d:
                    p["description"] = nd
                    changes.append(f"{name}: param {pname} enum text updated")
    return t, changes


def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else "plan"
    only = sys.argv[2] if len(sys.argv) > 2 else None
    rc = 0
    for target, (uuid, inst) in AGENTS.items():
        if only and only != target:
            continue
        s, d = raya("/api/agent/" + uuid)
        if s != 200:
            print(f"{target}: GET failed {s}"); rc = 1; continue
        d = d.get("data", d)
        new, changes = transform(d.get("tools") or {}, inst)
        if mode == "plan":
            print(f"\n=== {target}  ({inst})  {len(changes)} changes")
            for c in changes:
                print("   ", c)
        elif mode == "apply":
            if not changes:
                print(f"{target}: already current"); continue
            s2, r2 = raya("/api/agent/" + uuid, "PATCH", {"tools": new})
            ok = s2 == 200
            s3, d3 = raya("/api/agent/" + uuid)
            d3 = d3.get("data", d3)
            live = json.dumps(d3.get("tools"), sort_keys=True)
            match = live == json.dumps(new, sort_keys=True)
            print(f"{target:20} PATCH={s2} readback_matches={match} changes={len(changes)}")
            if not (ok and match):
                rc = 1
            time.sleep(0.4)
        elif mode == "verify":
            host = CREDS[inst]["baseUrl"].rstrip("/")
            blob = json.dumps(d.get("tools"))
            bad = []
            if OLD_HOST + "/" in blob or f'"{OLD_HOST}"' in blob:
                bad.append("still references OLD host")
            if CREDS[inst]["apiKey"] not in blob:
                bad.append("new api key absent")
            if CREDS[inst]["orgId"] not in blob:
                bad.append("new org id absent")
            for tool in d["tools"].get("llm_tools") or []:
                fn = tool.get("function") or {}
                props = ((fn.get("parameters") or {}).get("properties") or {})
                for p in ("age", "positions"):
                    if p in props and props[p].get("type") != "integer":
                        bad.append(f"{fn.get('name')}.{p} not integer")
                for p in ARRAY_PARAMS:
                    if p in props and props[p].get("type") != "array":
                        bad.append(f"{fn.get('name')}.{p} not array")
                if "otherHelpNeeded" in props and props["otherHelpNeeded"].get("description") != OTHER_HELP_DESC:
                    bad.append(f"{fn.get('name')}.otherHelpNeeded stale enum")
                _st = ((tool.get("api_details") or {}).get("payload_template") or {}).get("item_state") or {}
                for p in ARRAY_LITERALS:
                    if isinstance(_st.get(p), str) and not _st[p].startswith("{{"):
                        bad.append(f"{fn.get('name')}.{p} literal not array")
                pt = (tool.get("api_details") or {}).get("payload_template") or {}
                if pt.get("item_type") == "job_posting_1.0" and "title" in (pt.get("item_state") or {}):
                    bad.append(f"{fn.get('name')} still sends title")
            print(f"{target:20} {inst:10} {'OK' if not bad else 'FAIL: ' + '; '.join(bad)}")
            if bad:
                rc = 1
    return rc


if __name__ == "__main__":
    sys.exit(main())
