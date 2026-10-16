#!/usr/bin/env python3
"""nojobs_integrity.py — did the bot tell a caller there are no jobs on a call that WAS sent jobs?

The bug (D66, 2026-09-04). The Input Variables section declared `${recommendations}` with an alias —
"as job_recommendations" — and 65 references across six prompts used the alias, including the
Pre-check that decides whether any jobs were supplied: *"check `job_recommendations`. If it is empty
... trigger No-Match Fallback immediately."* There is no input by that name, so that condition read
as empty on every call. On a clean call the model reads the populated `${recommendations}` elsewhere
and never consults the pre-check; on a call with poor ASR or a confused caller, the pre-check is the
first and simplest rule in the section and it wins.

Measured before the fix, over 561 calls that were all sent jobs: 11 spoke the missing-job-data line
and **5 of those had presented nothing at all** — sent 3, 22, 28, 29 and 29 jobs. Three were real
production callers (`a7aa424e`, `fef540e9`, `d93b034a`), told there was nothing for them while 28-29
jobs sat in their arguments. That is the worst thing this bot can say to a job-seeker short of a fake
application.

FLAGS (hard): the call's `recommendations` argument held at least one job, the bot spoke the
missing-job-data line, and **no job was ever presented**. Presentation is detected by a salary figure
in a spoken turn, which the presentation template always carries.

REPORTS (info, never a failure): the same line spoken on a call where jobs WERE presented. That is
the legitimate exhausted-list / wrong-role case and it must not be counted — conflating the two is
how a real 0.9% gets buried inside a noisy 2%.

Usage: python3 raya/regression/nojobs_integrity.py [--since YYYY-MM-DD[THH:MM:SS]] [--agent <id>]
       python3 raya/regression/nojobs_integrity.py --call <uuid>
Times are UTC. Exit 1 if any hard finding is present.
"""
import argparse, json, os, re, sys, time, urllib.error, urllib.request
from concurrent.futures import ThreadPoolExecutor

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
_env = {}
for _l in open(os.path.join(REPO, "raya/.env")):
    _l = _l.strip()
    if "=" in _l and not _l.startswith("#"):
        _k, _v = _l.split("=", 1); _env[_k.strip()] = _v.strip().strip('"').strip("'")
BASE = _env["RAYA_BASE_URL"].rstrip("/"); TOKEN = _env["RAYA_API_TOKEN"]

# The missing-job-data callback line, both languages. Kept narrow on purpose: this is the line that
# means "no jobs were supplied to this call", not the wrong-role No-Match wording.
NOJOBS = re.compile(u"जॉब्स नहीं मिल रहीं|ಜಾಬ್‌ಗಳು ಸಿಗ್ತಾ ಇಲ್ಲ|ಜಾಬ್‌ಗಳು ಸಿಕ್ಕಿಲ್ಲ|ಜಾಬ್ ಸಿಗ್ತಾ ಇಲ್ಲ")
PRESENTED = re.compile(u"सैलरी|ಸ್ಯಾಲರಿ")


def get(path, tries=8):
    for i in range(tries):
        try:
            req = urllib.request.Request(BASE + path, headers={"X-API-Key": TOKEN, "User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=90) as r:
                return json.load(r)
        except urllib.error.HTTPError as e:
            if e.code in (429, 502, 503) and i < tries - 1:
                time.sleep(3 * (i + 1)); continue
            raise
        except Exception:
            if i < tries - 1:
                time.sleep(2 * (i + 1)); continue
            raise
    raise RuntimeError("giving up on " + path)


def seeker_targets():
    """Every seeker conversation target with a prod uuid. Only these receive `recommendations`."""
    man = json.load(open(os.path.join(REPO, "raya/agents.json"), encoding="utf-8"))
    out = []
    for t in man["targets"]:
        if t.get("kind") != "conversation":
            continue
        if (t.get("agent") or "").upper() not in ("KKB", "MAYA"):
            continue
        uuid = (t.get("raya_agent_id") or {}).get("prod")
        if uuid:
            out.append((t["id"], uuid))
    return out


def n_jobs(args):
    recs = (args or {}).get("recommendations")
    if not recs:
        return 0
    try:
        v = json.loads(recs) if isinstance(recs, str) else recs
        return len(v) if isinstance(v, list) else 0
    except Exception:
        return -1                       # unparseable: the fallback IS correct here, so not a finding


def check(bot, uuid):
    c = get("/api/call/" + uuid)
    turns = c.get("call_transcript") or []
    njobs = n_jobs(c.get("agent_args"))
    if njobs <= 0:
        return []
    spoke = [t for t in turns if t.get("role") == "assistant" and t.get("content") and NOJOBS.search(str(t["content"]))]
    if not spoke:
        return []
    presented = any(t.get("role") == "assistant" and t.get("content") and PRESENTED.search(str(t["content"]))
                    for t in turns)
    at = str(c.get("created_at"))[:19]
    if presented:
        return [dict(bot=bot, call=uuid, at=at, sev="info", kind="NO-JOBS LINE AFTER PRESENTING (info)",
                     detail="%d job(s) supplied, jobs were presented, then the missing-job-data line — "
                            "legitimate exhausted-list/wrong-role case" % njobs)]
    return [dict(bot=bot, call=uuid, at=at, sev="blocking", kind="NO JOBS CLAIMED WITH JOBS SUPPLIED",
                 detail="%d job(s) were in `recommendations` and NOT ONE was presented before the bot "
                        "said it could not find any" % njobs)]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--since", default=time.strftime("%Y-%m-%d", time.gmtime()))
    ap.add_argument("--agent", default="")
    ap.add_argument("--call", default="")
    a = ap.parse_args()

    if a.call:
        fs = check("(--call)", a.call)
        for f in fs:
            print("  %-38s %s  %s\n        %s" % (f["kind"], f["at"], f["call"][:8], f["detail"]))
        if not fs:
            print("  (no finding)")
        sys.exit(1 if any(f["sev"] == "blocking" for f in fs) else 0)

    targets = seeker_targets()
    if a.agent:
        targets = [t for t in targets if t[0] == a.agent or t[1] == a.agent]
    jobs, seen = [], 0
    for bot, uuid in targets:
        off = 0
        while off < 1200:
            d = get("/api/call?agent_id=%s&limit=100&offset=%d" % (uuid, off))
            calls = d.get("calls") or d.get("data") or []
            if not calls:
                break
            for c in calls:
                if c["created_at"] >= a.since and (c.get("call_duration") or 0) >= 20:
                    jobs.append((bot, c["uuid"]))
            if calls[-1]["created_at"] < a.since:
                break
            off += 100
        time.sleep(0.2)
    findings, errs = [], 0
    with ThreadPoolExecutor(max_workers=6) as ex:
        futs = {ex.submit(check, b, u): (b, u) for b, u in jobs}
        for fu in futs:
            try:
                findings += fu.result(); seen += 1
            except Exception:
                errs += 1
    print("no-jobs integrity check | since %s | %d calls | fetch errors: %d" % (a.since, seen, errs))
    hard = [f for f in findings if f["sev"] == "blocking"]
    for f in sorted(findings, key=lambda f: (f["sev"] != "blocking", f["at"]), reverse=False):
        print("  %-38s %-19s %-20s %s" % (f["kind"], f["at"], f["bot"], f["call"][:8]))
        print("        %s" % f["detail"])
    if not findings:
        print("  clean")
    sys.exit(1 if hard else 0)


if __name__ == "__main__":
    main()
