#!/usr/bin/env python3
"""overnight_sweep.py — generate live traffic on EVERY testable bot, then let the detectors grade it.

Why this shape. The Tier-3 standing check has been static-only, so every behaviour regression this
week (the inbound location ask, the already-applied branch, the fabricated apply) was found by hand
instead of by the suite. A behaviour check needs behaviour, and behaviour needs calls. So this does
the one thing no detector can do for itself: it makes the calls.

  Phase A (per pass)  for each case in the queue: PATCH the tester's persona + language, trigger the
                      bot to dial the tester, wait for the call to land, record the bot-leg uuid.
  Phase B (per pass)  run the static suite + every runtime detector with --since <sweep start>, and
                      fleet_report. The detectors read the traffic phase A just produced.
  Loop                repeat until the deadline. Later passes re-test the same bots, which is how an
                      intermittent fault shows up as a rate rather than as one lucky clean call.

One tester DID means phase A is strictly serial and slow (~3-5 min per case, ~19-60% bridge rate
depending on how long the line has been idle — see raya_testrun.CONNECT_BACKOFF). That is exactly
what an overnight window is for. Nothing here grades a call by itself: the graders are the detectors
in raya/regression/, so a rule only has to be written once.

Usage:
  python3 raya/overnight/overnight_sweep.py --hours 6 [--passes N] [--only <bot_id,...>]
  python3 raya/overnight/overnight_sweep.py --dry-run        # print the queue, make no calls
Output:
  raya/overnight/sweep-<date>/calls.tsv        one row per case attempt
  raya/overnight/sweep-<date>/pass-<n>.txt     detector output for that pass
  raya/overnight/sweep-<date>/REPORT.md        rolling summary, rewritten after every pass
"""
import argparse, json, os, re, subprocess, sys, time

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
TESTER_UUID = "f60e0899-aa3a-4be7-9b4f-0296bd28ef48"
TESTER_DID = "7946350285"
ARGS_DIR = "raya/testcases/args/r3"
PERSONA_DIR = "raya/personas"

# (bot_id, language, persona, args fixture, what this case is for)
# Every conversation target in raya/agents.json that has a prod uuid. The fixture/persona pair is
# chosen to walk the part of the flow that has actually broken before, not a happy path.
# ORDER MATTERS. The queue is front-loaded with the cases that verify a fix shipped tonight and not
# yet confirmed by a call, because a sweep that is interrupted should have settled those first. The
# broader coverage follows.
QUEUE = [
    ("maya-hi-signals",   "hi", "hi-student-cooperative",       "gzb-validated-12",           "Maya opener branch B: no college_name supplied -> name NO institution, never read the token (718aa8ab)"),
    ("maya-hi-signals",   "hi", "hi-force-apply",               "maya-college-gzb",           "Maya opener branch A: college_name supplied -> speak the college, not the token"),
    ("maya-hi-in-signals","hi", "hi-loc-confirm-then-landmark", "inbound-probe",              "Maya inbound: confirm the profile location (closed-set fix, 0baf8765)"),
    ("trrain-kn-out",     "kn", "kn-trrain-accept-then-asks",   "trrain-kn",                  "TRRAIN Kannada: names TRRAIN Trust, ported from Hindi tonight"),
    ("kkb-hi-signals",    "hi", "hi-asks-for-all-jobs",         "morejobs-22",                "the job_recommendations alias fix: 22 jobs must NOT produce the no-jobs line (8d3453b1)"),
    ("kkb-kn-signals",    "kn", "kn-asks-for-all-jobs",         "morejobs-kn",                "same on Kannada"),
    ("maya-hi-out",       "hi", "hi-force-apply",               "maya-college-gzb",           "Maya legacy outbound: opener branch A"),
    ("kkb-hi-signals",    "hi", "hi-force-apply",              "already-applied-muradnagar", "apply on a job already applied to -> row1/row2 wording"),
    ("kkb-hi-signals",    "hi", "hi-loc-confirm-then-landmark", "loc-reconfirm-gzb",          "supplied location is confirmed, not re-asked"),
    ("kkb-kn-signals",    "kn", "kn-force-apply",               "dharwad-validated-12",       "Kannada apply path end to end"),
    ("kkb-kn-signals",    "kn", "kn-seeker-cooperative",        "kn-signals-repro",           "Kannada location + free-service detail on request"),
    ("kkb-hi-in-signals", "hi", "hi-loc-confirm-then-landmark", "inbound-probe",              "inbound: confirm the profile location (Case B)"),
    ("kkb-hi-in-signals", "hi", "hi-force-apply",               "inbound-probe",              "inbound: consent before apply, no fabricated success"),
    ("kkb-kn-in-signals", "kn", "kn-seeker-cooperative",        "inbound-probe",              "Kannada inbound: location + acting_as_user_id"),
    ("kkb-kn-in-signals", "kn", "kn-force-apply",               "inbound-probe",              "Kannada inbound: apply path"),
    ("maya-hi-in-signals","hi", "hi-force-apply",               "inbound-probe",              "Maya inbound: apply + MPL"),
    ("dkb-hi-signals",    "hi", "hi-employer-cooperative",      "dkb-new-provider",           "DKB new provider: no expiry claim, nothing invented"),
    ("dkb-hi-signals",    "hi", "hi-employer-probe",            "dkb-new-provider",           "DKB: identity probing, never government"),
    ("dkb-kn-signals",    "kn", "kn-employer-cooperative",      "dkb-kn-new-provider",        "DKB Kannada new provider"),
    ("trrain-hi-out",     "hi", "hi-trrain-accepts",            "trrain-hi",                  "TRRAIN Hindi on Signals get_profile"),
    ("trrain-hi-out",     "hi", "hi-trrain-wrong-person",       "trrain-hi",                  "TRRAIN Hindi: no offer to the wrong person"),
    ("kkb-hi-out",        "hi", "hi-force-apply",               "gzb-validated-12",           "legacy Hindi outbound still healthy"),
    ("kkb-kn-out",        "kn", "kn-force-apply",               "dharwad-validated-12",       "legacy Kannada outbound still healthy"),
    ("kkb-hi-in",         "hi", "hi-loc-confirm-then-landmark", "inbound-probe",              "legacy Hindi inbound location"),
    ("kkb-kn-in",         "kn", "kn-seeker-cooperative",        "inbound-probe",              "legacy Kannada inbound"),
    ("maya-hi-in",        "hi", "hi-loc-confirm-then-landmark", "inbound-probe",              "Maya legacy inbound location"),
    ("dkb-hi-out",        "hi", "hi-employer-cooperative",      "dkb-new-provider",           "DKB legacy Hindi"),
    ("dkb-kn-out",        "kn", "kn-employer-cooperative",      "dkb-kn-new-provider",        "DKB legacy Kannada"),
]

DETECTORS = ["dkb_employer_integrity", "inbound_location_consent", "nojobs_integrity", "jobs_presented",
             "consent_before_apply", "location_chain", "location_reconfirm",
             "apply_result_integrity", "apply_failure_wording", "location_integrity",
             "apply_outcomes"]


def sh(cmd, timeout=1800):
    try:
        p = subprocess.run(cmd, cwd=REPO, capture_output=True, text=True, timeout=timeout)
        return p.returncode, p.stdout + p.stderr
    except subprocess.TimeoutExpired:
        return 124, "TIMEOUT after %ss: %s" % (timeout, " ".join(cmd))


def uuid_for(bot_id):
    man = json.load(open(os.path.join(REPO, "raya/agents.json"), encoding="utf-8"))
    for t in man["targets"]:
        if t["id"] == bot_id:
            return (t.get("raya_agent_id") or {}).get("prod") or ""
    return ""


def run_case(case, outdir, tsv):
    bot_id, lang, persona, argsf, why = case
    uuid = uuid_for(bot_id)
    if not uuid:
        row = [bot_id, lang, persona, argsf, "SKIP", "no prod uuid", ""]
        tsv.write("\t".join(row) + "\n"); tsv.flush(); return
    pfile = os.path.join(PERSONA_DIR, persona + ".md")
    afile = os.path.join(ARGS_DIR, argsf + ".json")
    for f in (pfile, afile):
        if not os.path.exists(os.path.join(REPO, f)):
            row = [bot_id, lang, persona, argsf, "SKIP", "missing " + f, ""]
            tsv.write("\t".join(row) + "\n"); tsv.flush(); return
    # The tester is ONE agent: its persona and language are per-call state, so they must be set
    # immediately before each dial and never assumed to have survived the previous case.
    sh(["python3", "scripts/raya_testcall.py", "persona", TESTER_UUID, pfile], timeout=180)
    sh(["python3", "scripts/raya_testcall.py", "lang", TESTER_UUID, lang], timeout=180)
    label = "%s-%s" % (bot_id, persona)
    rc, out = sh(["python3", "scripts/raya_testrun.py", uuid, TESTER_DID, afile, TESTER_UUID, label],
                 timeout=1500)
    m = re.search(r'"uuid": "([0-9a-f-]{36})"', out)
    bot_call = m.group(1) if m else ""
    landed = "CALL" if re.search(r"^\[assistant\]", out, re.M) else "NO-BRIDGE"
    open(os.path.join(outdir, "%s__%s.txt" % (bot_id, persona)), "a", encoding="utf-8").write(out)
    tsv.write("\t".join([bot_id, lang, persona, argsf, landed, bot_call, why]) + "\n"); tsv.flush()
    return landed


def phase_b(since, outdir, n):
    path = os.path.join(outdir, "pass-%d.txt" % n)
    with open(path, "w", encoding="utf-8") as fh:
        for name, cmd in [("static_regression", ["python3", "raya/regression/static_regression.py"]),
                          ("fix_presence", ["python3", "raya/regression/fix_presence.py"]),
                          ("input_coverage", ["python3", "raya/regression/input_coverage.py"]),
                          ("toolschema_parity", ["python3", "scripts/toolschema_parity.py"])]:
            rc, out = sh(cmd, timeout=900)
            fh.write("\n==== %s (rc=%d)\n%s" % (name, rc, out)); fh.flush()
        for d in DETECTORS:
            rc, out = sh(["python3", "raya/regression/%s.py" % d, "--since", since], timeout=2400)
            fh.write("\n==== %s (rc=%d)\n%s" % (d, rc, out)); fh.flush()
        rc, out = sh(["python3", "raya/regression/fab_rate.py", "--since", since, "--append"], timeout=2400)
        fh.write("\n==== fab_rate (rc=%d)\n%s" % (rc, out))
    return path


def write_report(outdir, since, passes, queue_len):
    lines = ["# Overnight sweep — started %s UTC" % since, "",
             "Traffic generated on every testable bot, then graded by the standing detectors.",
             "Queue: %d cases per pass. Passes completed: %d." % (queue_len, len(passes)), ""]
    tsvp = os.path.join(outdir, "calls.tsv")
    if os.path.exists(tsvp):
        rows = [l.rstrip("\n").split("\t") for l in open(tsvp, encoding="utf-8") if l.strip()]
        landed = sum(1 for r in rows if len(r) > 4 and r[4] == "CALL")
        lines += ["## Calls", "", "| bot | persona | landed | bot call |", "|---|---|---|---|"]
        for r in rows:
            if len(r) > 5:
                lines.append("| %s | %s | %s | `%s` |" % (r[0], r[2], r[4], (r[5] or "")[:8]))
        lines += ["", "%d of %d attempts bridged." % (landed, len(rows)), ""]
    for i, p in enumerate(passes, 1):
        txt = open(p, encoding="utf-8").read()
        crit = re.findall(r"^\s{2}([A-Z][0-9]? [A-Z][A-Z ,\-]+)", txt, re.M)
        lines += ["## Pass %d findings" % i, ""]
        if crit:
            from collections import Counter
            for k, v in Counter(x.strip() for x in crit).most_common():
                lines.append("- %s x%d" % (k, v))
        else:
            lines.append("- no detector findings")
        lines.append("")
    open(os.path.join(outdir, "REPORT.md"), "w", encoding="utf-8").write("\n".join(lines) + "\n")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--hours", type=float, default=6.0)
    ap.add_argument("--passes", type=int, default=99)
    ap.add_argument("--only", default="")
    ap.add_argument("--since", default="",
                    help="UTC ISO start for phase B's --since. Defaults to this run's start; pass an\n"
                         "earlier value to keep continuity across a restart, so traffic the previous\n"
                         "run already generated is still graded.")
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()
    queue = QUEUE
    if a.only:
        want = set(x.strip() for x in a.only.split(","))
        queue = [c for c in QUEUE if c[0] in want]
    if a.dry_run:
        for c in queue:
            print("%-22s %s  persona=%-30s args=%-26s %s" % (c[0], c[1], c[2], c[3], c[4]))
        print("\n%d cases; uuids:" % len(queue))
        for b in dict.fromkeys(c[0] for c in queue):
            print("  %-22s %s" % (b, uuid_for(b) or "MISSING"))
        return
    since = a.since or time.strftime("%Y-%m-%dT%H:%M:%S", time.gmtime())
    outdir = os.path.join(REPO, "raya/overnight", "sweep-" + time.strftime("%Y-%m-%d_%H%M", time.gmtime()))
    os.makedirs(outdir, exist_ok=True)
    deadline = time.time() + a.hours * 3600
    tsv = open(os.path.join(outdir, "calls.tsv"), "a", encoding="utf-8")
    passes = []
    n = 0
    print("sweep -> %s | since %s | deadline in %.1fh | %d cases/pass" % (outdir, since, a.hours, len(queue)), flush=True)
    while time.time() < deadline and n < a.passes:
        n += 1
        print("\n=== PASS %d ===" % n, flush=True)
        for case in queue:
            if time.time() > deadline:
                print("deadline reached mid-pass; stopping phase A", flush=True); break
            try:
                r = run_case(case, outdir, tsv)
                print("  %-22s %-30s %s" % (case[0], case[2], r), flush=True)
            except Exception as e:                      # one bad case must never end the night
                print("  %-22s %-30s ERROR %s" % (case[0], case[2], e), flush=True)
        try:
            passes.append(phase_b(since, outdir, n))
        except Exception as e:
            print("phase B error: %s" % e, flush=True)
        try:
            write_report(outdir, since, passes, len(queue))
        except Exception as e:
            print("report error: %s" % e, flush=True)
        print("pass %d done; report at %s/REPORT.md" % (n, outdir), flush=True)
    print("\nSWEEP COMPLETE — %d pass(es). %s/REPORT.md" % (n, outdir), flush=True)


if __name__ == "__main__":
    main()
