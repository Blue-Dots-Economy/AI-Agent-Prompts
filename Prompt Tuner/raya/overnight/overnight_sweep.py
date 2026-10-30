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
      [--coverage-first] [--no-phase-b] [--outdir DIR]
  (the nightly GitHub Actions job runs: --hours 3 --passes 1 --coverage-first --no-phase-b, then
   raya/regression/run_runtime_checks.sh and raya/regression/live_results.py; see regression.yml)
  python3 raya/overnight/overnight_sweep.py --dry-run        # print the queue, make no calls
Output:
  raya/overnight/sweep-<date>/calls.tsv        one row per case attempt
  raya/overnight/sweep-<date>/pass-<n>.txt     detector output for that pass
  raya/overnight/sweep-<date>/REPORT.md        rolling summary, rewritten after every pass
"""
import argparse, json, os, re, socket, subprocess, sys, time, urllib.request

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
TESTER_UUID = "f60e0899-aa3a-4be7-9b4f-0296bd28ef48"
# The DID is READ from the tester agent at start (DIDs get rebound: 7946350285 now belongs to a Purple
# Dots bot). This is only the fallback when the read fails; it is the tester's in_did as of 2026-10-14.
TESTER_DID_FALLBACK = "1204404272"
TESTER_DID = TESTER_DID_FALLBACK
ARGS_DIR = "raya/testcases/args/r3"   # a fixture name with a "/" is taken relative to raya/testcases/args


def _raya_env():
    """RAYA_BASE_URL / RAYA_API_TOKEN from the process env (GitHub Actions), else raya/.env."""
    e = {}
    p = os.path.join(REPO, "raya/.env")
    if os.path.exists(p):
        for l in open(p):
            l = l.strip()
            if "=" in l and not l.startswith("#"):
                k, v = l.split("=", 1); e[k.strip()] = v.strip()
    for k in ("RAYA_BASE_URL", "RAYA_API_TOKEN"):
        if os.environ.get(k):
            e[k] = os.environ[k].strip()
    return e


def raya_get(path):
    e = _raya_env()
    r = urllib.request.Request(e["RAYA_BASE_URL"].rstrip("/") + path,
                               headers={"X-API-Key": e["RAYA_API_TOKEN"], "User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(r, timeout=30) as resp:
        d = json.loads(resp.read().decode() or "{}")
    return (d or {}).get("data", d) or {}


def resolve_tester_did():
    try:
        did = str(raya_get("/api/agent/" + TESTER_UUID).get("in_did") or "")
        if len(did) >= 10:
            return did[-10:]
    except Exception as ex:
        print("tester DID lookup failed (%s); using fallback" % str(ex)[:80], flush=True)
    return TESTER_DID_FALLBACK
PERSONA_DIR = "raya/personas"

# (bot_id, language, persona, args fixture, what this case is for)
# Every conversation target in raya/agents.json that has a prod uuid. The fixture/persona pair is
# chosen to walk the part of the flow that has actually broken before, not a happy path.
# ORDER MATTERS. The queue is front-loaded with the cases that verify a fix shipped tonight and not
# yet confirmed by a call, because a sweep that is interrupted should have settled those first. The
# broader coverage follows.
QUEUE = [
    # KKB Slim: the bots that carry the live Ghaziabad / Dharwad seeker traffic since 2026-10-05, so they go first.
    ("kkb-hi-signals-slim","hi","hi-oct12-new-anything",        "oct12/hi-s1",                "KKB Slim Hindi: new caller, consent saved at once, trade asked, no invented PIN"),
    ("kkb-kn-signals-slim","kn","kn-oct12-new-anything",        "oct12/kn-s1",                "KKB Slim Kannada: new caller, consent saved at once, trade asked, no invented PIN"),
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
    ("dkb-hi-signals",    "hi", "hi-oct26-dkb-inbound-new",     "oct26/dkb-inbound-new",      "DKB both directions: a new employer calls in, no campaign arguments"),
    ("dkb-kn-signals",    "kn", "kn-oct26-dkb-inbound-new",     "oct26/dkb-kn-inbound-new",   "DKB Kannada both directions: a new employer calls in"),
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


def coverage_first(queue):
    """Every bot's FIRST case, in queue order, then the rest. A run that hits its deadline mid-pass
    has then still called every bot once instead of calling the first few bots twice."""
    seen, first, rest = set(), [], []
    for c in queue:
        (rest if c[0] in seen else first).append(c)
        seen.add(c[0])
    return first + rest

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


def target_for(bot_id):
    man = json.load(open(os.path.join(REPO, "raya/agents.json"), encoding="utf-8"))
    for t in man["targets"]:
        if t["id"] == bot_id:
            return t
    return {}


def uuid_for(bot_id):
    t = target_for(bot_id)
    if t.get("deploy") is False:
        return ""
    return (t.get("raya_agent_id") or {}).get("prod") or ""


def fixture_path(argsf):
    if "/" in argsf:
        return os.path.join("raya/testcases/args", argsf + ".json")
    return os.path.join(ARGS_DIR, argsf + ".json")


def wait_tester_idle(max_wait=900):
    """The tester is shared with people testing by hand. Never dial while its latest call is still
    live: wait (up to max_wait seconds) until it has ended, then go ahead."""
    t0 = time.time()
    while time.time() - t0 < max_wait:
        try:
            d = raya_get("/api/call?agent_id=%s&limit=1" % TESTER_UUID)
            calls = d.get("calls") if isinstance(d, dict) else None
            last = (calls or [{}])[0]
            if str(last.get("outcome") or "Completed") not in ("Pending", "In Progress", "Ongoing", "Ringing"):
                return True
            # a call older than 20 minutes is past the tester's 15-minute cap: a stale status, not a live call
            import calendar
            ts = str(last.get("created_at") or "")[:19]
            if ts and time.time() - calendar.timegm(time.strptime(ts, "%Y-%m-%dT%H:%M:%S")) > 1200:
                return True
            print("  tester busy (call %s %s); waiting" % (str(last.get("uuid"))[:8], last.get("outcome")), flush=True)
        except Exception:
            return True
        time.sleep(60)
    return False


def backend_down(uuid):
    """The hosts this bot's tools call, if NONE of them accepts a connection; else ''. A bot whose backend
    is gone can only fail every case (the older Dhiway/ONEST hosts stopped answering in Oct 2026 and the
    bots on them invented successes after timeouts), so it is reported as skipped, not as a failing bot.
    The probe runs every night: if the backend comes back, the bot is called again."""
    try:
        tools = (raya_get("/api/agent/" + uuid).get("tools") or {}).get("llm_tools") or []
    except Exception:
        return ""
    hosts = sorted({(t.get("api_details") or {}).get("url", "").split("/")[2] for t in tools
                    if "://" in (t.get("api_details") or {}).get("url", "")})
    for h in hosts:
        try:
            socket.create_connection((h, 443), timeout=8).close()
            return ""
        except OSError:
            continue
    return ", ".join(hosts)


def run_case(case, outdir, tsv):
    bot_id, lang, persona, argsf, why = case
    uuid = uuid_for(bot_id)
    if not uuid:
        row = [bot_id, lang, persona, argsf, "SKIP", "no prod uuid", ""]
        tsv.write("\t".join(row) + "\n"); tsv.flush(); return
    pfile = os.path.join(PERSONA_DIR, persona + ".md")
    afile = fixture_path(argsf)
    for f in (pfile, afile):
        if not os.path.exists(os.path.join(REPO, f)):
            row = [bot_id, lang, persona, argsf, "SKIP", "missing " + f, why]
            tsv.write("\t".join(row) + "\n"); tsv.flush(); return "SKIP"
    # An inbound agent can only be made to dial out when it has an integer out_did (else the POST
    # 500s). Setting one is an agent config change, which this sweep never makes, so say so and move on.
    if target_for(bot_id).get("direction") == "inbound":
        try:
            if not raya_get("/api/agent/" + uuid).get("out_did"):
                row = [bot_id, lang, persona, argsf, "SKIP", "inbound agent has no out_did, cannot dial", why]
                tsv.write("\t".join(row) + "\n"); tsv.flush(); return "SKIP"
        except Exception:
            pass
    down = backend_down(uuid)
    if down:
        row = [bot_id, lang, persona, argsf, "SKIP", "backend unreachable: " + down, why]
        tsv.write("\t".join(row) + "\n"); tsv.flush(); return "SKIP"
    wait_tester_idle()
    # The tester is ONE agent: its persona and language are per-call state, so they must be set
    # immediately before each dial and never assumed to have survived the previous case.
    sh(["python3", "scripts/raya_testcall.py", "persona", TESTER_UUID, pfile], timeout=180)
    sh(["python3", "scripts/raya_testcall.py", "lang", TESTER_UUID, lang], timeout=180)
    label = "%s-%s" % (bot_id, persona)
    rc, out = sh(["python3", "scripts/raya_testrun.py", uuid, TESTER_DID, afile, TESTER_UUID, label],
                 timeout=1500)
    # the bridged call is the "BOT <uuid> outcome=" line; without one, the LAST dial attempt
    m = re.search(r"\bBOT ([0-9a-f-]{36}) outcome=", out)
    if not m:
        ms = re.findall(r'"uuid": "([0-9a-f-]{36})"', out)
        bot_call = ms[-1] if ms else ""
    else:
        bot_call = m.group(1)
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
    ap.add_argument("--coverage-first", action="store_true",
                    help="call every bot once before any bot's second case")
    ap.add_argument("--no-phase-b", action="store_true",
                    help="dial only; the caller grades (the nightly CI job runs the detectors itself)")
    ap.add_argument("--max-cases", type=int, default=0, help="stop after this many cases (0 = no cap)")
    ap.add_argument("--outdir", default="", help="output directory (default raya/overnight/sweep-<utc>)")
    a = ap.parse_args()
    queue = QUEUE
    if a.only:
        want = set(x.strip() for x in a.only.split(","))
        queue = [c for c in QUEUE if c[0] in want]
    if a.coverage_first:
        queue = coverage_first(queue)
    if a.max_cases:
        queue = queue[:a.max_cases]
    if a.dry_run:
        for c in queue:
            print("%-22s %s  persona=%-30s args=%-26s %s" % (c[0], c[1], c[2], c[3], c[4]))
        print("\n%d cases; uuids:" % len(queue))
        for b in dict.fromkeys(c[0] for c in queue):
            print("  %-22s %s" % (b, uuid_for(b) or "MISSING"))
        return
    global TESTER_DID
    TESTER_DID = resolve_tester_did()
    since = a.since or time.strftime("%Y-%m-%dT%H:%M:%S", time.gmtime())
    outdir = a.outdir or os.path.join(REPO, "raya/overnight", "sweep-" + time.strftime("%Y-%m-%d_%H%M", time.gmtime()))
    os.makedirs(outdir, exist_ok=True)
    deadline = time.time() + a.hours * 3600
    tsv = open(os.path.join(outdir, "calls.tsv"), "a", encoding="utf-8")
    passes = []
    n = 0
    print("sweep -> %s | since %s | deadline in %.1fh | %d cases/pass | tester DID ...%s"
          % (outdir, since, a.hours, len(queue), TESTER_DID[-4:]), flush=True)
    json.dump({"since": since, "tester_did_last4": TESTER_DID[-4:], "hours": a.hours,
               "queue": [list(c) for c in queue]},
              open(os.path.join(outdir, "meta.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
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
        if not a.no_phase_b:
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
