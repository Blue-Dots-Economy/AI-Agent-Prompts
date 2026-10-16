#!/usr/bin/env python3
"""apply_outcomes.py - runtime (Tier-3) check on what actually happened on real calls.

The static suite (static_regression.py) reads the 20 prompt files and never places or reads a
call, so it is blind to anything that only shows up at runtime: an apply rejected by the
backend, a tool 4xx, or a caller being told something untrue about why something failed.
That gap is exactly how 2026-08-25's "the API is still failing" report survived a week of
green daily digests. This script closes it by reading `call_output` off real calls.

What it reports
  * apply attempts, successes and failures per bot, grouped by the backend's failure reason
  * for every ACTION_LIMIT_REACHED (duplicate application) failure, WHICH caller-facing line
    the bot actually spoke: the truthful "already applied" line, or the misleading
    "technical problem" line (analyser D47). A technical line on a duplicate is a FAILURE.

Exit code is 1 if any D47 violation is found, so a scheduled run surfaces it.

Usage:
  python3 raya/regression/apply_outcomes.py [--since YYYY-MM-DD[THH:MM:SS]] [--min-dur 20]
"""
import argparse, json, os, sys, time, urllib.request, collections
from concurrent.futures import ThreadPoolExecutor

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
_env = {}
for _l in open(os.path.join(REPO, "raya/.env")):
    _l = _l.strip()
    if "=" in _l and not _l.startswith("#"):
        k, v = _l.split("=", 1)
        _env[k.strip()] = v.strip().strip('"').strip("'")
BASE = _env["RAYA_BASE_URL"].rstrip("/")
KEY = _env["RAYA_API_TOKEN"]

# The two spoken lines that matter for D47. Substrings, matched against the transcript.
DUP_OK = ["एप्लीकेशन पहले से लगी हुई है", "ಅಪ್ಲಿಕೇಶನ್ ಈಗಾಗಲೇ ಇದೆ"]
TECH_BAD = ["तकनीकी दिक्कत", "technical ತೊಂದರೆ"]
DUP_MARKERS = ["ACTION_LIMIT_REACHED", "action limit", "already exists"]


def get(path, tries=5):
    for i in range(tries):
        try:
            r = urllib.request.Request(BASE + path, headers={
                "X-API-Key": KEY, "User-Agent": "Mozilla/5.0", "Accept": "application/json"})
            with urllib.request.urlopen(r, timeout=120) as resp:
                return json.loads(resp.read())
        except Exception:
            if i == tries - 1:
                raise
            time.sleep(1.5 * (i + 1))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--since", default=None, help="ISO date/time; default = last 24h")
    ap.add_argument("--min-dur", type=int, default=20, help="ignore calls shorter than this")
    ap.add_argument("--workers", type=int, default=4)
    a = ap.parse_args()
    since = a.since or time.strftime("%Y-%m-%d", time.gmtime(time.time() - 86400))

    targets = [t for t in json.load(open(os.path.join(REPO, "raya/agents.json")))["targets"]
               if t.get("kind") == "conversation" and t["raya_agent_id"].get("prod")]

    work = []
    for t in targets:
        off = 0
        while True:
            d = get(f"/api/call?agent_id={t['raya_agent_id']['prod']}&limit=100&offset={off}")
            cs = d.get("calls") or []
            if not cs:
                break
            older = False
            for c in cs:
                ts = str(c.get("created_at"))[:19]
                if ts < since:
                    older = True
                    continue
                if (c.get("call_duration") or 0) >= a.min_dur:
                    work.append((t["id"], c["uuid"]))
            if older or len(cs) < 100:
                break
            off += 100

    print(f"apply-outcome check | since {since} | {len(work)} calls to inspect", flush=True)

    def fetch(item):
        bot, u = item
        try:
            return bot, u, get("/api/call/" + u), None
        except Exception as e:
            return bot, u, None, str(e)[:80]

    ok = collections.Counter(); fail = collections.Counter()
    reasons = collections.Counter(); errors = 0
    violations = []; good_dup = []
    with ThreadPoolExecutor(max_workers=a.workers) as ex:
        for bot, u, d, err in ex.map(fetch, work):
            if err:
                errors += 1
                continue
            co = d.get("call_output") or {}
            ja = co.get("jobs_applied") or []
            jf = co.get("jobs_failed_to_apply") or []
            ok[bot] += len(ja); fail[bot] += len(jf)
            if not jf:
                continue
            spoken = " ".join(str(m.get("content") or "")
                              for m in (d.get("call_transcript") or [])
                              if m.get("role") == "assistant")
            toolblob = " ".join(str(m.get("content") or "")
                                for m in (d.get("call_transcript") or [])
                                if m.get("role") == "tool")
            for f in jf:
                reason = str(f.get("failure_reason") or "unknown")
                reasons[reason] += 1
                is_dup = any(m.lower() in (reason + " " + toolblob).lower() for m in DUP_MARKERS)
                if not is_dup:
                    continue
                said_ok = any(s in spoken for s in DUP_OK)
                said_bad = any(s in spoken for s in TECH_BAD)
                rec = (bot, u, str(d.get("created_at"))[:19], reason)
                if said_ok and not said_bad:
                    good_dup.append(rec)
                else:
                    violations.append(rec + ("said_truthful_line" if said_ok else "no_truthful_line",
                                             "said_technical_line" if said_bad else "-"))

    print(f"fetch errors: {errors}")
    print("\n-- apply outcomes by bot --")
    for b in sorted(set(list(ok) + list(fail))):
        if ok[b] or fail[b]:
            print(f"  {b:24} succeeded={ok[b]:4}  failed={fail[b]:4}")
    print(f"  TOTAL succeeded={sum(ok.values())} failed={sum(fail.values())}")

    if reasons:
        print("\n-- failure reasons --")
        for r, n in reasons.most_common():
            print(f"  {n:4}  {r}")

    print(f"\n-- D47 duplicate-apply wording --")
    print(f"  correct (truthful 'already applied' line): {len(good_dup)}")
    for r in good_dup[:10]:
        print(f"     OK  {r[2]}  {r[0]:20} {r[1]}")
    print(f"  VIOLATIONS (duplicate spoken as a technical fault): {len(violations)}")
    for r in violations[:10]:
        print(f"     BAD {r[2]}  {r[0]:20} {r[1]}  [{r[4]}, {r[5]}]")

    return 1 if violations else 0


if __name__ == "__main__":
    sys.exit(main())
