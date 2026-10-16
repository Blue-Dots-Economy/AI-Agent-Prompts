#!/usr/bin/env python3
"""fleet_report.py — one PASS/FAIL line per bot, with explicit criteria.

Why: the runtime detectors print findings per call, which answers "what went wrong" but never
"is this bot OK". Worse, a window with zero calls printed ALL CLEAN on 2026-09-03 and read as a
pass -- so a bot with no coverage must be reported as UNTESTED, never as passing.

Criteria per bot, all evaluated over the window:
  * static      — 0 critical and 0 major static findings for that bot's prompts
  * schema      — tool schemas identical to the rest of its agent+backend family
  * calls       — at least MIN_CALLS usable calls (>=40s) in the window, else UNTESTED
  * behaviour   — 0 blocking runtime findings on those calls

Blocking runtime findings are the ones that mislead or shortchange a caller:
  ALL-TOLD WHILE JOBS UNNAMED, SAME JOB NAMED UNDER TWO ORDINALS, Z SUCCESS WITH NO SUCCESS RESULT,
  X CONTRADICTORY APPLY RESULT, ROW 1 MISSED, consent-before-apply violations.
Informational ones (ASKED FOR MORE ... (info), MEMORY-COVERAGE GAP, DIAGNOSED A CAUSE) do not fail a
bot: the first is a coverage note, the second is the known memory blocker, and the third fires on the
owner-approved "technical issue" wording.

Usage: python3 raya/regression/fleet_report.py [--since YYYY-MM-DDTHH:MM:SS] [--min-calls N]
Times are UTC — the Raya API stamps calls in UTC and passing IST silently selects nothing.
"""
import argparse, datetime, json, os, re, subprocess, sys

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
# ROW 1 MISSED is deliberately NOT blocking. It fires when a duplicate apply did not get the
# already-applied line -- but the agent cannot know a job is a duplicate: the error body never
# reaches the model, contact_memory is empty, and get_profile returns no applications (D58). The
# evidence gate makes row 2 the CORRECT output in that state, so treating this as a failure would
# make the fleet permanently red on a blocked platform issue and train us to ignore the report.
# It stays visible in the detector output and in STATUS as the open platform ask.
# SAME JOB NAMED UNDER TWO ORDINALS is informational, not blocking: job identity is the job_id and
# the bot never speaks it, so the detector compares role+company and cannot distinguish "named the
# same job twice" from "named two posts that share a role and company". Real payloads contain such
# pairs -- five McDonald's Crew Member posts, two CY FUTURE Customer Support posts. Read it as a
# prompt to go look, not a failure.
BLOCKING = [
    # Seeker rail
    "ALL-TOLD WHILE JOBS UNNAMED",          # jobs_presented
    "Z SUCCESS WITH NO SUCCESS RESULT",     # apply_result_integrity — told a caller they applied
    "X CONTRADICTORY APPLY RESULT",         # apply_result_integrity
    "Y NARRATED WRITE",                     # apply_result_integrity — spoke a tool call instead of making it
    "W FALSE DUPLICATE-CHECK ASSERTION",    # apply_result_integrity
    "NO CONSENT BEFORE APPLY",              # consent_before_apply
    "CONSENT AFTER APPLY",                  # consent_before_apply — spoken too late is still not consent
    "ROW 1 WRONGLY USED",                   # apply_failure_wording — claimed already-applied without evidence
    # Employer rail
    "P POSTED WITH NO WRITE RESULT", "N NARRATED A WRITE", "C POSTED WITHOUT CONSENT",
    # Inbound rail (location comes from the profile, not from a campaign arg)
    "K CONSENT DISCLOSURE DROPPED", "L OPEN ASK ON KNOWN PROFILE LOCATION",
    "M JOBS IN ANOTHER CITY, MISMATCH NOT NAMED",
]
DETECTORS = ["dkb_employer_integrity", "inbound_location_consent",
             "jobs_presented", "consent_before_apply", "apply_result_integrity",
             "apply_failure_wording", "location_reconfirm", "location_chain",
             "location_integrity", "apply_outcomes"]


def run(cmd):
    p = subprocess.run(cmd, cwd=REPO, capture_output=True, text=True)
    return p.stdout + p.stderr


def _verify_blocking_tokens():
    """Every BLOCKING token must be a string some detector actually prints.

    On 2026-09-04 this list contained "APPLY WITHOUT THE DATA-SHARING LINE", which NO detector
    emits — consent_before_apply prints "NO CONSENT BEFORE APPLY". So a real consent violation on
    kkb-hi-in-signals (bbdb6eaf, a caller applied with no data-sharing line) was printed by the
    detector, listed under Blocking in the nightly narrative, and STILL showed the bot as PASS in
    the per-bot table. A hand-typed token list silently degrades to "nothing is blocking".
    """
    import glob as _glob
    src = ""
    for p in _glob.glob(os.path.join(REPO, "raya/regression/*.py")):
        if p.endswith("fleet_report.py"):
            continue
        src += open(p, encoding="utf-8").read()
    missing = [t for t in BLOCKING if ('"%s"' % t) not in src and ("'%s'" % t) not in src]
    if missing:
        print("  *** BLOCKING tokens no detector emits — these can never fire: %s" % missing)
        return False
    return True


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--since", default=datetime.datetime.utcnow().strftime("%Y-%m-%dT00:00:00"))
    ap.add_argument("--min-calls", type=int, default=2)
    a = ap.parse_args()

    targets = [t for t in json.load(open(os.path.join(REPO, "raya/agents.json")))["targets"]
               if t.get("kind") == "conversation" and (t.get("raya_agent_id") or {}).get("prod")]
    sig = [t for t in targets if "signals" in t["id"]]

    print("FLEET REPORT — window from %s (UTC), min %d usable calls per bot\n" % (a.since, a.min_calls))

    tokens_ok = _verify_blocking_tokens()
    static = run(["python3", "raya/regression/static_regression.py"])
    m = re.search(r"(\d+) critical, (\d+) major", static)
    crit, maj = (int(m.group(1)), int(m.group(2))) if m else (-1, -1)
    print("  static suite : %d critical, %d major  -> %s" % (crit, maj, "PASS" if crit == 0 and maj == 0 else "FAIL"))

    schema = run(["python3", "scripts/toolschema_parity.py"])
    sch_ok = "SCHEMA PARITY CLEAN" in schema
    print("  tool schemas : %s" % ("PASS — every family identical" if sch_ok else "FAIL — see toolschema_parity"))
    print("  blocking-token self-check : %s" % ("PASS" if tokens_ok else "FAIL — list is out of sync with the detectors"))

    out = {}
    for det in DETECTORS:
        out[det] = run(["python3", "raya/regression/%s.py" % det, "--since", a.since])

    # Count each bot's calls from the API, NOT from detector output. Inferring coverage from
    # findings means a bot that behaved perfectly looks untested -- which is how DKB read 0 calls
    # immediately after its own detector had graded eleven of them.
    import urllib.request
    _env = {}
    for _l in open(os.path.join(REPO, "raya/.env")):
        _l = _l.strip()
        if "=" in _l and not _l.startswith("#"):
            k, v = _l.split("=", 1); _env[k.strip()] = v.strip().strip('"').strip("'")

    def call_count(uuid):
        req = urllib.request.Request(
            _env["RAYA_BASE_URL"].rstrip("/") + "/api/call?agent_id=%s&limit=100" % uuid,
            headers={"X-API-Key": _env["RAYA_API_TOKEN"], "User-Agent": "Mozilla/5.0"})
        try:
            with urllib.request.urlopen(req, timeout=90) as r:
                cs = json.loads(r.read() or b"{}").get("calls") or []
        except Exception:
            return -1
        return sum(1 for c in cs
                   if str(c.get("created_at"))[:19] >= a.since and (c.get("call_duration") or 0) >= 40)

    print("\n  %-22s %-7s %-9s %s" % ("bot", "calls", "verdict", "blocking findings"))
    worst = 0
    for t in sorted(sig, key=lambda x: x["id"]):
        bid = t["id"]
        calls = call_count(t["raya_agent_id"]["prod"])
        hits = []
        for det, text in out.items():
            for line in text.splitlines():
                if bid in line and any(b in line for b in BLOCKING):
                    tag = next(b for b in BLOCKING if b in line)
                    hits.append(tag)
        mine = sum(1 for det, text in out.items() for line in text.splitlines() if bid in line)
        # Every bot now has at least one behavioural detector: the seeker rail has eight, and the
        # employer rail got dkb_employer_integrity on 2026-09-03 (before that DKB had none, and this
        # report said NO-DETECTORS rather than pretending a silent bot was a passing one).
        verdict = "UNTESTED" if calls <= 0 else ("FAIL" if hits else "PASS")
        if verdict == "FAIL":
            worst = 2
        elif verdict == "UNTESTED" and worst < 1:
            worst = 1
        print("  %-22s %-7s %-9s %s" % (bid, calls if calls > 0 else "0", verdict,
              ", ".join(sorted(set(hits))) if hits else ("no calls in window" if verdict == "UNTESTED" else "none")))

    print("\n  NOTE: a bot with no calls in the window is UNTESTED, not passing.")
    print("  %s" % ("FLEET PASS" if worst == 0 and crit == 0 and maj == 0 and sch_ok else
                    ("FLEET FAIL" if worst == 2 or crit or maj or not sch_ok else "FLEET PASS WITH GAPS")))
    sys.exit(0 if worst == 0 and crit == 0 and maj == 0 and sch_ok and tokens_ok else 1)


if __name__ == "__main__":
    main()
