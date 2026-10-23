#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Turn one night's live test calls into raya/regression/live-report.json for the email digest.

Inputs
  --sweep-dir DIR       the overnight_sweep.py output (calls.tsv + meta.json)
  --detectors-log FILE  the output of run_runtime_checks.sh --since <sweep start> (optional)
  --cache DIR           where to save each graded call's full JSON (the CALLCACHE the cache-based
                        detectors read); optional
  --out FILE            default raya/regression/live-report.json

Per call it records: which bot, which scenario, whether the line connected, the call id, the Raya
recording link, every mechanical check from grade_call.py (PASS / FAIL / SKIP), and every line in the
detector log that names this call. Nothing here judges a call by itself: the rules live in
grade_call.py and the detectors, so a rule is still written once.

Usage (the nightly job runs it like this):
  python3 raya/regression/live_results.py --sweep-dir "$SWEEP" --detectors-log "$SWEEP/detectors.txt" \
      --cache "$CALLCACHE"
"""
import argparse, json, os, re, sys, time

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(REPO, "raya", "regression"))
import grade_call  # noqa: E402  (env-aware: RAYA_* from the environment, else raya/.env)

REC_FMT = "https://api.getraya.app/call_recording/?audiofile=/%s"
MIN_BOT_TURNS = 4      # below this the call is THIN (too short to judge), never PASS
MIN_SECONDS = 60

# Plain-English names for the mechanical checks, for a reader who has never seen the code.
CHECK_NAMES = {
    "jobs-from-array-only": "Only offered jobs it was given",
    "no-latin-in-speech": "Spoke the caller's language (no stray English words)",
    "no-bracket-markers": "Did not read a [placeholder] aloud",
    "no-field-labels": "Did not read a field label aloud",
    "numbers-in-words": "Said numbers as words",
    "no-literal-slash": "Did not say a slash aloud",
    "no-stage-directions": "Did not read an internal instruction aloud",
    "apply-claim-backed-by-tool": "Said 'applied' only when it really applied",
    "apply-announced-once-per-apply": "Announced each application once",
    "location-not-raw": "Said the place name naturally (no PIN read out)",
    "disclosure-before-apply": "Asked permission before sharing details",
    "failure-line-matches-error": "Told the caller the right reason when applying failed",
}

DETECTOR_NAMES = {
    "bracket_leak": "Placeholder read aloud",
    "spoken_form": "Stored value read out in its written form",
    "location_said": "Which place the bot named",
    "dkb_employer_integrity": "Employer told something was posted that was not",
    "inbound_location_consent": "Inbound: location and permission",
    "nojobs_integrity": "Said 'no jobs' when there were jobs",
    "jobs_presented": "Stopped offering jobs too early",
    "consent_before_apply": "Applied without asking permission",
    "location_chain": "Location questions in the right order",
    "location_reconfirm": "Confirmed the location it was given",
    "apply_result_integrity": "Application result told truthfully",
    "apply_failure_wording": "Right words when an application failed",
    "location_integrity": "Saved a place the caller never said",
    "apply_outcomes": "How applications ended",
    "already_applied_rate": "'Already applied' said correctly",
    "offarray_jobs": "Named companies it was not given",
    "toolschema_parity": "Tool set the same across sister bots",
    "fix_presence": "Earlier fixes still present in every bot",
    "input_coverage": "Bot uses what the campaign sends",
}

UUID_RE = re.compile(r"\b([0-9a-f]{8})(?:-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})?\b")
FINDING_RE = re.compile(r"^\s{2}([A-Z][A-Z0-9 /,'\-]+?(?:\(info\))?)\s+\d{4}-\d\d-\d\d")


def labels():
    try:
        fleet = json.load(open(os.path.join(REPO, "raya/regression/fleet.json"), encoding="utf-8"))
        return {b["bot_id"]: b["label"] for b in fleet.get("bots", [])}
    except Exception:
        return {}


def parse_detectors(path):
    """-> (sections: {name: [lines]}, findings: [(detector, label, uuid8, info)])"""
    sections, cur = {}, None
    if not path or not os.path.exists(path):
        return sections, []
    for line in open(path, encoding="utf-8", errors="replace"):
        line = line.rstrip("\n")
        m = re.match(r"^=+ (\S+)\s*$", line)
        if m:
            cur = m.group(1); sections[cur] = []; continue
        if cur:
            sections[cur].append(line)
    findings = []
    for name, lines in sections.items():
        for ln in lines:
            fm = FINDING_RE.match(ln)
            if not fm:
                continue
            um = UUID_RE.search(ln[fm.end():])
            if not um:
                continue
            lab = fm.group(1).strip()
            findings.append((name, lab.replace("(info)", "").strip(), um.group(1), "(info)" in lab))
    return sections, findings


def detector_summary(sections):
    out = []
    for name, lines in sections.items():
        body = [l for l in lines if l.strip()]
        n = sum(1 for l in body if FINDING_RE.match(l) and "(info)" not in l)
        clean = any(re.search(r"\bclean\b|^\s*none\b|SCHEMA PARITY CLEAN|ALL .*CLEAN", l) for l in body)
        status = "findings" if n else ("clean" if clean or not body else "ran")
        if name == "fix_presence":
            m = [l for l in body if l.startswith("FIX PRESENCE")]
            status = "findings" if m and "failure" in m[-1] else "clean"
            n = len([l for l in body if l.strip().startswith("FAIL ")])
        out.append({"detector": name, "title": DETECTOR_NAMES.get(name, name), "status": status,
                    "findings": n, "head": [l.strip() for l in body[:2]]})
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--sweep-dir", required=True)
    ap.add_argument("--detectors-log", default="")
    ap.add_argument("--cache", default="")
    ap.add_argument("--out", default=os.path.join(REPO, "raya/regression/live-report.json"))
    a = ap.parse_args()

    meta = {}
    try:
        meta = json.load(open(os.path.join(a.sweep_dir, "meta.json"), encoding="utf-8"))
    except Exception:
        pass
    rows = []
    tsv = os.path.join(a.sweep_dir, "calls.tsv")
    if os.path.exists(tsv):
        rows = [l.rstrip("\n").split("\t") for l in open(tsv, encoding="utf-8") if l.strip()]
    sections, dfind = parse_detectors(a.detectors_log)
    if a.cache:
        os.makedirs(a.cache, exist_ok=True)
    lab = labels()

    calls = []
    for r in rows:
        r += [""] * (7 - len(r))
        bot_id, lang, persona, argsf, landed, uuid, why = r[:7]
        c = {"bot_id": bot_id, "bot": lab.get(bot_id, bot_id), "language": lang, "persona": persona,
             "fixture": argsf, "scenario": why, "status": landed, "call_id": "", "recording": "",
             "duration": None, "checks": [], "detector_findings": [], "verdict": landed}
        if landed == "SKIP":
            c["skip_reason"] = uuid
            c["verdict"] = "NOT DIALLED"
            calls.append(c); continue
        if not re.fullmatch(r"[0-9a-f-]{36}", uuid or ""):
            c["verdict"] = "NO CALL ID"
            calls.append(c); continue
        c["call_id"] = uuid
        c["recording"] = REC_FMT % uuid
        if landed != "CALL":
            c["verdict"] = "DID NOT CONNECT"
            calls.append(c); continue
        try:
            full = grade_call.get("/api/call/" + uuid)
        except Exception as ex:
            c["verdict"] = "COULD NOT FETCH"; c["error"] = str(ex)[:120]
            calls.append(c); continue
        c["recording"] = full.get("call_recording_url") or c["recording"]
        c["duration"] = full.get("call_duration")
        c["outcome"] = full.get("outcome")
        c["turns"] = len(full.get("call_transcript") or [])
        if a.cache:
            full["_bot"] = bot_id
            json.dump(full, open(os.path.join(a.cache, uuid + ".json"), "w", encoding="utf-8"),
                      ensure_ascii=False)
        try:
            for name, st, detail in grade_call.grade(full):
                c["checks"].append({"check": name, "title": CHECK_NAMES.get(name, name),
                                    "result": st, "detail": detail})
        except Exception as ex:
            c["checks"].append({"check": "grader", "title": "Grader", "result": "ERROR",
                                "detail": str(ex)[:120]})
        for det, flabel, u8, info in dfind:
            if u8 == uuid[:8]:
                c["detector_findings"].append({"detector": det,
                                               "title": DETECTOR_NAMES.get(det, det),
                                               "finding": flabel.title(), "info": info})
        fails = [x for x in c["checks"] if x["result"] in ("FAIL", "ERROR")]
        dfails = [x for x in c["detector_findings"] if not x["info"]]
        passes = [x for x in c["checks"] if x["result"] == "PASS"]
        # A call that ends after a couple of turns checks nothing about the flow, however many
        # surface checks it "passes" (the first CI proof call, 09d3a1a5, was 37s and 2 bot turns
        # because the tester was busy with another run, and graded PASS on 6 trivial checks).
        bot_turns = sum(1 for t in (full.get("call_transcript") or [])
                        if t.get("role") == "assistant" and str(t.get("content") or "").strip())
        c["bot_turns"] = bot_turns
        short = bot_turns < MIN_BOT_TURNS or (c["duration"] or 0) < MIN_SECONDS
        if short:
            c["short_reason"] = ("The call ended after %d bot turn(s) and %ss, too short to check the flow."
                                 % (bot_turns, c["duration"]))
        if fails or dfails:
            c["verdict"] = "FAIL"
        elif short or len(passes) < 3:
            c["verdict"] = "THIN"
        else:
            c["verdict"] = "PASS"
        calls.append(c)

    bots = sorted(dict.fromkeys(c["bot_id"] for c in calls))
    dialled = [c for c in calls if c["verdict"] != "NOT DIALLED"]
    connected = [c for c in calls if c["status"] == "CALL"]
    rep = {
        "generated_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "since_utc": meta.get("since", ""),
        "hours_budget": meta.get("hours"),
        "queue_len": len(meta.get("queue") or []),
        "bots_in_queue": sorted(dict.fromkeys(q[0] for q in (meta.get("queue") or []))),
        "bots_called": bots,
        "attempts": len(dialled),
        "connected": len(connected),
        "passed": len([c for c in connected if c["verdict"] == "PASS"]),
        "failed": len([c for c in connected if c["verdict"] == "FAIL"]),
        "thin": len([c for c in connected if c["verdict"] == "THIN"]),
        "not_dialled": len([c for c in calls if c["verdict"] == "NOT DIALLED"]),
        "calls": calls,
        "detectors": detector_summary(sections),
        "run_url": os.environ.get("RUN_URL", ""),
    }
    json.dump(rep, open(a.out, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("live-report: %d attempt(s), %d connected, %d pass, %d fail, %d thin, %d not dialled -> %s"
          % (rep["attempts"], rep["connected"], rep["passed"], rep["failed"], rep["thin"],
             rep["not_dialled"], a.out))
    for c in calls:
        print("  %-22s %-16s %s %s" % (c["bot_id"], c["verdict"], (c["call_id"] or "")[:8],
                                        c.get("skip_reason", "")))
    return 0


if __name__ == "__main__":
    sys.exit(main())
