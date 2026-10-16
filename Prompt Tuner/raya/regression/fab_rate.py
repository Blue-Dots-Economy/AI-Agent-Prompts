#!/usr/bin/env python3
"""fab_rate.py — track the fabricated-apply RATE over time, because single batches cannot settle it.

The bug: the bot tells a caller their application succeeded when `apply_job` never returned success.
Measured at roughly 4 in 35 success-claiming calls (~11%) on 2026-09-04. At that rate a six-call
batch expects 0.3 fabrications, so a clean batch is not evidence of a fix and a single bad call is
not evidence of a regression. Three prompt fixes have already been called "verified" off small clean
samples and each was later contradicted.

So this does not give a verdict. It appends one row per run to raya/regression/fab-rate.tsv —
date, window, success-claiming calls, fabricated, and the call ids — so the denominator accumulates
and a real change in rate becomes visible across days instead of being re-argued each time.

A call counts in the DENOMINATOR only if it claimed success at all; claiming nothing is not a pass.

Usage: python3 raya/regression/fab_rate.py [--since YYYY-MM-DDTHH:MM:SS] [--append]
Times are UTC. Exit 0 always — this is a measurement, not a gate (fleet_report gates on Z).
"""
import argparse, json, os, re, sys, time, urllib.request
from concurrent.futures import ThreadPoolExecutor

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
_env = {}
for _l in open(os.path.join(REPO, "raya/.env")):
    _l = _l.strip()
    if "=" in _l and not _l.startswith("#"):
        k, v = _l.split("=", 1); _env[k.strip()] = v.strip().strip('"').strip("'")
BASE = _env["RAYA_BASE_URL"].rstrip("/"); TOKEN = _env["RAYA_API_TOKEN"]
TSV = os.path.join(REPO, "raya/regression/fab-rate.tsv")
CLAIM = re.compile(u"अप्लाई हो गया|ಅಪ್ಲೈ ಆಗಿದೆ")


def get(path):
    req = urllib.request.Request(BASE + path, headers={"X-API-Key": TOKEN, "User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=90) as r:
        return json.loads(r.read() or b"{}")


def grade(bot, uuid):
    d = get("/api/call/" + uuid)
    tr = d.get("call_transcript") or []
    said = " ".join(str(t.get("content") or "") for t in tr if t.get("role") == "assistant")
    if not CLAIM.search(said):
        return None                                  # never claimed success — not in the denominator
    ok = sum(1 for t in tr if t.get("role") == "tool" and "action_id" in str(t.get("content") or ""))
    return (bot, uuid, ok == 0)                      # True = fabricated


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--since", default=time.strftime("%Y-%m-%dT00:00:00", time.gmtime(time.time() - 86400)))
    ap.add_argument("--append", action="store_true", help="record this run in fab-rate.tsv")
    ap.add_argument("--workers", type=int, default=4)
    a = ap.parse_args()
    targets = [t for t in json.load(open(os.path.join(REPO, "raya/agents.json")))["targets"]
               if t.get("kind") == "conversation" and (t.get("raya_agent_id") or {}).get("prod")]
    work = []
    for t in targets:
        for c in (get("/api/call?agent_id=%s&limit=100" % t["raya_agent_id"]["prod"]).get("calls") or []):
            if str(c.get("created_at"))[:19] < a.since:
                continue
            if (c.get("call_duration") or 0) >= 40:
                work.append((t["id"], c["uuid"]))
    rows = []
    with ThreadPoolExecutor(max_workers=a.workers) as ex:
        for r in ex.map(lambda w: grade(*w), work):
            if r:
                rows.append(r)
    fab = [r for r in rows if r[2]]
    print("fabricated-apply rate | since %s | %d calls scanned" % (a.since, len(work)))
    print("  success-claiming calls : %d" % len(rows))
    print("  fabricated             : %d" % len(fab))
    if rows:
        print("  rate                   : %.1f%%" % (100.0 * len(fab) / len(rows)))
    for bot, uuid, _ in fab:
        print("    FABRICATED %-20s %s" % (bot, uuid))
    if not rows:
        print("  no success-claiming calls in this window — nothing to measure, NOT a pass")
    if a.append:
        new = not os.path.exists(TSV)
        with open(TSV, "a") as fh:
            if new:
                fh.write("date\twindow_since\tclaimed\tfabricated\tfabricated_call_ids\n")
            fh.write("%s\t%s\t%d\t%d\t%s\n" % (time.strftime("%Y-%m-%d"), a.since, len(rows), len(fab),
                                               ",".join(u[:8] for _, u, _ in fab) or "-"))
        print("  appended to %s" % os.path.relpath(TSV, REPO))
        tot_c = tot_f = 0
        for i, line in enumerate(open(TSV)):
            if i == 0:
                continue
            p = line.rstrip("\n").split("\t")
            if len(p) >= 4:
                tot_c += int(p[2]); tot_f += int(p[3])
        if tot_c:
            print("  cumulative: %d fabricated of %d success-claiming calls (%.1f%%)"
                  % (tot_f, tot_c, 100.0 * tot_f / tot_c))
    sys.exit(0)


if __name__ == "__main__":
    main()
