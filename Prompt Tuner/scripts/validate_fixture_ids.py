#!/usr/bin/env python3
"""validate_fixture_ids.py — check that every job_id in a test fixture is still live.

Why: on 2026-09-03 a live campaign payload carried five job_ids that no longer existed on the
Ghaziabad instance. Applying to any of them returns TARGET_ITEM_NOT_FOUND, the caller hears the
technical-issue line, and it reads as a bot bug. It was stale data: the same roles were present under
NEW ids. Five of ten sampled ids from that payload had stopped being live within hours.

The data team and the API were both right -- the jobs exist, the ids handed to the bot did not. So
any fixture (and ideally any campaign payload) should be validated against current inventory before
it is used, or a test will "find" a bug that is really a dead id.

Note: fetch_local ignores both item_ids and lifecycle_status filters and returns only live items, so
this compares against the full live listing and cannot distinguish "absent" from "present but not
live" -- ask the data team to check status for anything this reports.

Usage: python3 scripts/validate_fixture_ids.py raya/testcases/args/r3/gzb-validated-12.json [...]
Exit 1 if any id is not live.
"""
import json, os, sys, urllib.request, urllib.error

CREDS = os.path.expanduser("~/Downloads/Signals instance credentials (SECRET) (1).json")


def inventory(inst):
    d = json.load(open(CREDS))["instances"][inst]
    h = {"x-api-key": d["apiKey"], "x-acting-org-id": d["orgId"],
         "Content-Type": "application/json", "User-Agent": "Mozilla/5.0"}
    ids, off = set(), 0
    while True:
        body = {"item_network": "blue_dot", "item_domain": "provider",
                "item_type": "job_posting_1.0", "limit": 100, "offset": off}
        req = urllib.request.Request(d["baseUrl"] + "/api/v1/network/item/fetch_local",
                                     data=json.dumps(body).encode(), headers=h, method="POST")
        try:
            with urllib.request.urlopen(req, timeout=90) as r:
                b = json.loads(r.read())
        except urllib.error.HTTPError as e:
            print("  inventory fetch failed %s: %s" % (e.code, e.read()[:120].decode()))
            return ids
        items = b.get("items") or []
        ids.update(i.get("item_id") for i in items)
        if len(items) < 100:
            break
        off += 100
        if off > 5000:
            break
    return ids


def main():
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    inv = {}
    bad = 0
    for path in sys.argv[1:]:
        d = json.load(open(path))
        rec = d.get("recommendations")
        jobs = json.loads(rec) if isinstance(rec, str) else (rec or [])
        loc = (d.get("location") or "").lower()
        inst = "dharwad" if any(k in loc for k in ("hubballi", "hubli", "dharwad")) else "ghaziabad"
        if inst not in inv:
            inv[inst] = inventory(inst)
        pool = inv[inst]
        miss = [j for j in jobs if j.get("job_id") not in pool]
        print("%-46s %-10s %d jobs, %d not live" % (os.path.basename(path), inst, len(jobs), len(miss)))
        for j in miss:
            print("     NOT LIVE  %-38s %s" % (j.get("job_id"), j.get("role")))
        bad += len(miss)
    print("\n%s" % ("ALL FIXTURE IDS LIVE" if not bad else "%d DEAD IDS — refresh before testing" % bad))
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
