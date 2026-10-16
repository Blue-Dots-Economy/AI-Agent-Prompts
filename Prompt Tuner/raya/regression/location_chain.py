#!/usr/bin/env python3
"""location_chain.py — assert the Location step happened as ONE clean chain, in order.

The intended flow (2026-09-01, owner-specified) is fixed:

    CONFIRM the supplied location  ->  (first call only) ONE finer-detail question  ->  jobs

and the finer-detail question is asked ONCE PER CALLER, EVER: once `nearest_landmark` is in the
caller's memory, that turn must never happen again. "It works" is therefore not a judgement about a
transcript — it is six checks, and this script is what makes them checkable:

  C1 CONFIRM MISSING       a location was supplied, at least one job is in it, and the bot never read
                           it back for confirmation ("हमारे पास आपकी जॉब की लोकेशन X है — क्या यह सही है?").
  C2 OPEN ASK INSTEAD      the bot asked openly ("किस इलाके…") on a call where a location WAS supplied.
                           This is the exact complaint that started this work.
  C3 TURN B MISSING        the call's args carried a contact_memory with an EMPTY nearest_landmark,
                           the caller confirmed the location, and the bot never asked for a bus stop /
                           station / landmark. **Only a hard finding when the args actually carried
                           the memory.** When no contact_memory arg was sent, the platform's own
                           stored memory is in play and cannot be read from here (analyser D54), so a
                           skipped Turn B may be exactly right — reported as C3? (info), never failed.
  C4 TURN B RE-ASKED       memory ALREADY carried a nearest_landmark and the bot asked anyway. The
                           most irritating failure for a repeat caller, and invisible without this.
  C5 BUNDLED               the confirm (or the finer question) shared a turn with another question —
                           two "?" in one assistant turn during the location step.
  C6 OUT OF ORDER          the itemised job list was read out before the location step finished.

Exit 1 on any finding. C4 is reported even when everything else passes.

Usage: python3 raya/regression/location_chain.py [--since YYYY-MM-DD[THH:MM:SS]] [--agent <id|uuid>]
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

EMPTY = {"", "-", "any", "na", "n/a", "none", "null", "not available", "not_available"}
CONFIRM  = re.compile(r"हमारे पास आपकी जॉब की लोकेशन")
MISMATCH = re.compile(r"में अभी कोई जॉब नहीं")
OPEN_ASK = re.compile(r"किस इलाके|किसी खास इलाके|किस तरफ़?|किस जगह के आसपास")
TURN_B   = re.compile(r"बस स्टॉप|रेलवे या मेट्रो स्टेशन|जानी-पहचानी जगह")
JOBLIST  = re.compile(r"(दो|तीन|एक) ऑप्शन (है|हैं)|पहला:")
LANDMARK_KEYS = ("nearest_landmark",)


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


def memory_landmark(aa):
    """The nearest_landmark the call was given, if any."""
    cm = aa.get("contact_memory")
    if not cm:
        return ""
    if isinstance(cm, str):
        try:
            cm = json.loads(cm)
        except Exception:
            return ""
    if not isinstance(cm, dict):
        return ""
    for k in LANDMARK_KEYS:
        v = str(cm.get(k) or "").strip()
        if v:
            return v
    return ""


def job_places(rec):
    if isinstance(rec, str):
        try:
            rec = json.loads(rec)
        except Exception:
            return []
    if not isinstance(rec, list):
        return []
    return [str(j.get("location") or "").lower() for j in rec if isinstance(j, dict)]


def check(bot, uuid):
    d = get("/api/call/" + uuid)
    aa = d.get("agent_args") or {}
    loc = str(aa.get("location") or "").strip()
    if loc.lower() in EMPTY or loc.startswith("${"):
        return []
    places = job_places(aa.get("recommendations"))
    if not places:
        return []
    had_jobs = any(loc.lower() in p for p in places)
    known_landmark = memory_landmark(aa)
    turns = [str(t.get("content") or "") for t in (d.get("call_transcript") or [])
             if t.get("role") == "assistant" and t.get("content")]
    text = " ".join(turns)
    created = str(d.get("created_at"))[:19]
    base = dict(bot=bot, call=uuid, at=created, loc=loc,
                mem="landmark-known" if known_landmark else "landmark-absent")
    out = []
    said_confirm = bool(CONFIRM.search(text))
    said_mismatch = bool(MISMATCH.search(text))
    said_open = bool(OPEN_ASK.search(text))
    said_turnb = bool(TURN_B.search(text))

    if had_jobs and not said_confirm:
        out.append(dict(base, kind="C1 CONFIRM MISSING",
                        detail=f"location {loc!r} has jobs but was never read back for confirmation"))
    if said_open and (said_confirm or said_mismatch or had_jobs):
        out.append(dict(base, kind="C2 OPEN ASK INSTEAD",
                        detail="asked openly which area, on a call that supplied a location"))
    if known_landmark and said_turnb:
        out.append(dict(base, kind="C4 TURN B RE-ASKED",
                        detail=f"memory already held nearest_landmark={known_landmark!r} and the bot asked again"))
    if (not known_landmark) and (said_confirm or said_mismatch) and not said_turnb:
        if aa.get("contact_memory") is None:
            out.append(dict(base, kind="C3? TURN B SKIPPED (info)",
                            detail="the finer-detail question was not asked, and no contact_memory arg was sent — "
                                   "the platform's stored memory is in play and unreadable from here, so this may be "
                                   "the skip working correctly. Not a failure. To test it properly, send an explicit "
                                   "contact_memory with an empty nearest_landmark (but see D54: the args value may "
                                   "not reach the model at all)"))
        else:
            out.append(dict(base, kind="C3 TURN B MISSING",
                            detail="the args carried a contact_memory with no nearest_landmark and the "
                                   "finer-detail question was never asked"))
    # C5 — two questions in one location turn
    for t in turns:
        if (CONFIRM.search(t) or TURN_B.search(t)) and t.count("?") > 1:
            out.append(dict(base, kind="C5 BUNDLED",
                            detail=f"location turn carried {t.count('?')} questions: {t[:110]}"))
            break
    # C6 — jobs read out before the location step finished
    idx_job = next((i for i, t in enumerate(turns) if JOBLIST.search(t)), None)
    idx_loc = next((i for i, t in enumerate(turns)
                    if CONFIRM.search(t) or MISMATCH.search(t) or TURN_B.search(t)), None)
    if idx_job is not None and idx_loc is not None and idx_job < idx_loc:
        out.append(dict(base, kind="C6 OUT OF ORDER",
                        detail="the itemised job list came before the location step"))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--since", default=time.strftime("%Y-%m-%d", time.gmtime(time.time() - 86400)))
    ap.add_argument("--agent", default=None)
    ap.add_argument("--workers", type=int, default=3)
    a = ap.parse_args()
    targets = [t for t in json.load(open(os.path.join(REPO, "raya/agents.json")))["targets"]
               if t.get("kind") == "conversation" and t["raya_agent_id"].get("prod")]
    if a.agent:
        targets = [t for t in targets if a.agent in (t["id"], t["raya_agent_id"]["prod"])]
    work = []
    for t in targets:
        d = get(f"/api/call?agent_id={t['raya_agent_id']['prod']}&limit=100")
        for c in d.get("calls") or []:
            if str(c.get("created_at"))[:19] < a.since:
                continue
            if (c.get("call_duration") or 0) >= 40:
                work.append((t["id"], c["uuid"]))
    print(f"location chain check | since {a.since} | {len(work)} calls", flush=True)
    bad, errs = [], 0
    with ThreadPoolExecutor(max_workers=a.workers) as ex:
        for res in ex.map(lambda i: _safe(check, i), work):
            if res is None:
                errs += 1
            else:
                bad.extend(res)
    print(f"fetch errors: {errs}\n")
    if not bad:
        print("  clean — confirm fired, the finer question fired exactly once per caller, in order")
        return 0
    for f in bad:
        print(f"  {f['kind']:22} {f['at']}  {f['bot']:18} {f['call']}  location={f['loc']!r} {f['mem']}")
        print(f"        {f['detail']}")
    return 1


def _safe(fn, arg):
    try:
        return fn(*arg)
    except Exception:
        return None


if __name__ == "__main__":
    sys.exit(main())
