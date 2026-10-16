#!/usr/bin/env python3
"""apply_result_integrity.py — the bot must not contradict itself about the apply, or narrate a write it never made.

Two failures, both found by testing rather than by a report (2026-09-01):

  X. CONTRADICTORY APPLY RESULT — the same call tells the caller both "अभी इस जॉब में अप्लाई पूरा नहीं
     हो पाया" and "अप्लाई हो गया है". Seen on call `14f90f64`: apply_job returned 422, the bot spoke the
     failure line, then two turns later — bridging out of the Need Capture answer — spoke the whole
     Apply Success block. The caller cannot know which is true, and the second one is false.

  Y. NARRATED WRITE — the bot says a field was updated/saved ("मैंने उम्र 26 साल अपडेट कर दी है") on a
     call with NO `update_profile` / `create_profile` tool call anywhere in the transcript. Seen on
     call `0decf61a`, where the caller corrected their age from 29 to 26 and the correction went
     nowhere. The record stays wrong and nobody finds out, because the caller was told it was fixed.

  Z. SUCCESS CLAIMED WITH NO SUCCESSFUL TOOL RESULT — "अप्लाई हो गया है" on a call where apply_job
     never returned success (already a hard failure in the prompt; asserted here on real traffic).

  W. DUPLICATE CHECK ASSERTED FALSELY — `apply_job` carries a REQUIRED `duplicate_check` parameter
     (see scripts/raya_toolparam.py): the model must send 'not-applied-before' or
     'caller-asked-again-anyway'. That is a machine-readable audit trail of a decision that used to be
     invisible. **A 'not-applied-before' followed by ACTION_LIMIT_REACHED has TWO very different
     causes and only one of them is a bot bug** — conflating them would make this detector cry wolf
     on ordinary traffic:
       W  (FAILED)   the call's own `contact_memory.jobs_applied` DID list that job (same role at the
                     same company) and the model still asserted 'not-applied-before'. The check was
                     available and was not run. This is the bug the parameter exists to catch.
       W? (INFO)     memory did NOT list it, so the model asserted correctly on what it could see and
                     the duplicate existed only in the backend. Nothing the prompt can fix: it is a
                     MEMORY-COVERAGE gap (an application made outside our calls, or before memory
                     was enabled). Reported, never failed — it is the standing argument for asking
                     the platform to surface the tool error body, which is the only way the bot could
                     have known.
     Absent parameter = the schema has not reached that agent yet (only kkb-hi-signals carries it as
     of 2026-09-01); reported, not failed.

Exit 1 on any finding.

Usage: python3 raya/regression/apply_result_integrity.py [--since YYYY-MM-DD] [--agent <id|uuid>]
"""
import argparse, json, os, re, sys, time, urllib.request
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

FAIL_LINE = re.compile(r"अप्लाई पूरा नहीं हो|apply complete नहीं|ಅಪ್ಲೈ ಇನ್ನೂ ಪೂರ್ತಿ ಆಗಿಲ್ಲ|apply complete ಆಗಿಲ್ಲ")
OK_LINE   = re.compile(r"अप्लाई हो गया|ಅಪ್ಲೈ ಆಗಿದೆ")
WROTE     = re.compile(r"(अपडेट कर दी|अपडेट कर दिया|सेव कर दिया|सेव कर दी|ಅಪ್‌ಡೇಟ್ ಮಾಡಿದ್ದೀನಿ|ಸೇವ್ ಮಾಡಿದ್ದೀನಿ)")
# The already-applied (row 1) line. Row 1 is only permissible on evidence: apply_job ran earlier in
# THIS call for THIS job, or contact_memory.jobs_applied names it. The model cannot read the tool
# error body (133 named errors on 2026-09-01..04 all produced the same generic line), so whenever it
# speaks row 1 off a bare 422 it is guessing -- and it guesses in BOTH directions: "technical issue"
# on real duplicates (tracker row 103) and "already applied" on unrelated errors (c5a10922,
# 5f0d3671 on USER_NOT_FOUND, 72112c10).
ROW1_LINE = re.compile(r"एप्लीकेशन पहले से लगी|पहले से लगी हुई|ಅಪ್ಲಿಕೇಶನ್ ಈಗಾಗಲೇ ಇದೆ|ಈಗಾಗಲೇ ಅಪ್ಲೈ")


def _job_in_memory(aa, job_id):
    """Return the matching jobs_applied entry if this call's memory already listed the job.

    Matching is on ROLE + COMPANY, not on job_id: memory is written in prose by the memory prompt
    ("2026-08-31: Computer Operator / Data Entry, NIIT Ltd, Ghaziabad") and carries no uuid. Resolve
    the job_id to its role/company through the call's own `recommendations`, then look for both in a
    memory entry, ignoring Ltd/Limited/Pvt Ltd suffixes and case.
    """
    rec = aa.get("recommendations")
    if isinstance(rec, str):
        try:
            rec = json.loads(rec)
        except Exception:
            return ""
    job = next((j for j in (rec or []) if isinstance(j, dict) and j.get("job_id") == job_id), None)
    if not job:
        return ""
    cm = aa.get("contact_memory")
    if isinstance(cm, str):
        try:
            cm = json.loads(cm)
        except Exception:
            return ""
    entries = (cm or {}).get("jobs_applied") if isinstance(cm, dict) else None
    if not isinstance(entries, list):
        return ""
    def norm(x):
        x = str(x or "").lower()
        for junk in (" pvt ltd", " pvt. ltd", " private limited", " limited", " ltd", ".", ","):
            x = x.replace(junk, " ")
        return " ".join(x.split())
    role, comp = norm(job.get("role")), norm(job.get("company"))
    for e in entries:
        ne = norm(e)
        if role and comp and role in ne and comp in ne:
            return str(e)
    return ""


def get(path, tries=4):
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


def check(bot, uuid):
    d = get("/api/call/" + uuid)
    turns = d.get("call_transcript") or []
    said = " ".join(str(m.get("content") or "") for m in turns if m.get("role") == "assistant")
    tools_called = [ (tc.get("function") or {}).get("name")
                     for m in turns for tc in (m.get("tool_calls") or []) ]
    tool_out = " ".join(str(m.get("content") or "") for m in turns if m.get("role") == "tool")
    apply_ok = bool(re.search(r"'status':\s*'success'|\"status\":\s*\"success\"", tool_out))
    created = str(d.get("created_at"))[:19]
    base = dict(bot=bot, call=uuid, at=created)
    out = []
    f, o = bool(FAIL_LINE.search(said)), bool(OK_LINE.search(said))
    if f and o:
        out.append(dict(base, kind="X CONTRADICTORY APPLY RESULT",
                        detail="the call says both that the apply did not go through AND that it did"))
    if o and not apply_ok:
        out.append(dict(base, kind="Z SUCCESS WITH NO SUCCESS RESULT",
                        detail="spoke the apply-success line with no successful apply_job result in the transcript"))
    # W — what the model ASSERTED about duplication vs what the API then said
    for m in turns:
        for tc in (m.get("tool_calls") or []):
            fn = tc.get("function") or {}
            if fn.get("name") != "apply_job":
                continue
            try:
                args = json.loads(fn.get("arguments") or "{}")
            except Exception:
                continue
            dc = args.get("duplicate_check")
            if dc is None:
                continue
            if dc != "not-applied-before" or not re.search(r"ACTION_LIMIT_REACHED", tool_out):
                continue
            jid = args.get("job_id")
            in_mem = _job_in_memory(d.get("agent_args") or {}, jid)
            if in_mem:
                out.append(dict(base, kind="W FALSE DUPLICATE-CHECK ASSERTION",
                                detail=f"sent duplicate_check='not-applied-before' for job {jid}, but the call's own "
                                       f"contact_memory.jobs_applied already listed it ({in_mem!r}) — the check was "
                                       f"available and was not run"))
            else:
                out.append(dict(base, kind="W? MEMORY-COVERAGE GAP (info)",
                                detail=f"job {jid} was already applied in the backend but is NOT in this call's "
                                       f"contact_memory.jobs_applied, so the bot could not have known. Not a prompt "
                                       f"bug — the fix is either richer memory or the platform surfacing the error body"))
    # V — the already-applied line spoken with no evidence for it. Distinct from W: W is about what the
    # model asserted BEFORE the call; this is about what it told the CALLER after an error it cannot
    # read. Telling someone their application is already in place when it is not stops them applying.
    if ROW1_LINE.search(said):
        applied_jobs, ran_twice = [], False
        seen_jobs = []
        for m in turns:
            for tc in (m.get("tool_calls") or []):
                fn = tc.get("function") or {}
                if fn.get("name") != "apply_job":
                    continue
                try:
                    args = json.loads(fn.get("arguments") or "{}")
                except Exception:
                    continue
                jid = args.get("job_id")
                if jid in seen_jobs:
                    ran_twice = True            # same job attempted twice in this call = real evidence
                seen_jobs.append(jid)
                if _job_in_memory(d.get("agent_args") or {}, jid):
                    applied_jobs.append(jid)
        if not applied_jobs and not ran_twice:
            out.append(dict(base, kind="V UNEVIDENCED ALREADY-APPLIED",
                            detail="spoke the already-applied line, but no apply_job ran twice for the same job "
                                   "in this call and contact_memory.jobs_applied names none of the jobs attempted — "
                                   "the evidence gate allows neither, so the cause was guessed off an unreadable 422"))
    if WROTE.search(said) and not ({"update_profile", "create_profile"} & set(tools_called)):
        out.append(dict(base, kind="Y NARRATED WRITE",
                        detail=f"claimed a field was saved/updated; tools actually called: {sorted(set(filter(None, tools_called))) or 'none'}"))
    return out


def _bot_for_call(uuid, targets):
    """Label a --call finding with the bot that call ACTUALLY belongs to.

    This used to be `targets[0]["id"]` — the first target in the manifest, checked against nothing.
    On 2026-09-04 a real finding on call 4982c225 (agent 115b38a5 = kkb-hi-signals) was printed
    against `kkb-hi-out`, which is a different prompt file on a different backend. A report that
    names the wrong bot sends whoever reads it to the wrong prompt, so the label has to come from
    the call.
    """
    try:
        aid = (get("/api/call/" + uuid) or {}).get("agent_id")
    except Exception:
        aid = None
    if aid:
        for t in targets:
            if (t.get("raya_agent_id") or {}).get("prod") == aid:
                return t["id"]
        return "agent:" + str(aid)[:8]
    return "?"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--since", default=time.strftime("%Y-%m-%d", time.gmtime(time.time() - 86400)))
    ap.add_argument("--agent", default=None)
    ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("--call", action="append", default=[],
                    help="grade only these call uuids (repeatable) — the list API lags a few minutes")
    a = ap.parse_args()
    targets = [t for t in json.load(open(os.path.join(REPO, "raya/agents.json")))["targets"]
               if t.get("kind") == "conversation" and t["raya_agent_id"].get("prod")]
    if a.agent:
        targets = [t for t in targets if a.agent in (t["id"], t["raya_agent_id"]["prod"])]
    work = []
    if a.call:
        _bot = None   # resolved per call by _bot_for_call
        work = [(_bot, c) for c in a.call]
    if not a.call:
     for t in targets:
        off = 0
        while True:
            d = get(f"/api/call?agent_id={t['raya_agent_id']['prod']}&limit=100&offset={off}")
            cs = d.get("calls") or []
            if not cs:
                break
            older = False
            for c in cs:
                if str(c.get("created_at"))[:19] < a.since:
                    older = True
                    continue
                if (c.get("call_duration") or 0) >= 20:
                    work.append((t["id"], c["uuid"]))
            if older or len(cs) < 100:
                break
            off += 100
    print(f"apply-result integrity check | since {a.since} | {len(work)} calls", flush=True)
    bad, errs = [], 0
    with ThreadPoolExecutor(max_workers=a.workers) as ex:
        for res in ex.map(lambda i: _safe(check, i), work):
            if res is None:
                errs += 1
            else:
                bad.extend(res)
    print(f"fetch errors: {errs}\n")
    if not bad:
        print("  clean — no contradictory apply results and no narrated writes")
        return 0
    for f in bad:
        print(f"  {f['kind']:32} {f['at']}  {f['bot']:20} {f['call']}")
        print(f"        {f['detail']}")
    return 1


def _safe(fn, arg):
    try:
        return fn(*arg)
    except Exception:
        return None


if __name__ == "__main__":
    sys.exit(main())
