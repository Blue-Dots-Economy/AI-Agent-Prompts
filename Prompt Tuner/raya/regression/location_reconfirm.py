#!/usr/bin/env python3
"""location_reconfirm.py — the campaign sent a `location`; did the bot actually USE it?

Three failures live here, all seen on real calls (analyser D53):

  A. OPEN ASK ON A KNOWN LOCATION — the input named a real place, at least one job is there, and the
     bot still asked the caller from scratch ("किस इलाके या शहर के पास काम करना चाहेंगे?") instead of
     reconfirming it ("आपको <जगह> के आसपास जॉब चाहिए, या कहीं और भी चलेगा?"). The caller experiences this
     as "I gave you my location and you asked me anyway".
  B. FALSE PLACE CLAIM — the input named a place NO job is in, and the bot told the caller we have jobs
     there ("आपके लिए दिल्ली में कुछ जॉब्स हैं" on a call whose 8 jobs were all in Ghaziabad).
  C. MISMATCH NOT NAMED — the input place holds no job and the bot never said so; it silently switched
     to the job city (or asked openly), throwing away the location the call was given.

It also reports the campaign-targeting signal on every call: whether the input location had ANY job in
it. A run where most calls say NO is a campaign problem, not a bot problem — surface it either way.

Exit 1 if any A/B/C finding is present.

Usage: python3 raya/regression/location_reconfirm.py [--since YYYY-MM-DD] [--agent <id|uuid>]
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

# Sentinels the prompt defines as EMPTY — never treat these as a location.
EMPTY = {"", "-", "any", "na", "n/a", "none", "null", "not available", "not_available"}

# Latin -> the canonical Devanagari the prompt is required to speak. Keep in step with the
# "Canonical Location Spellings" section; a name missing here is simply not asserted on.
CANON = {
    "ghaziabad": "गाज़ियाबाद", "delhi": "दिल्ली", "noida": "नोएडा", "meerut": "मेरठ",
    "indirapuram": "इंदिरापुरम", "vasundhara": "वसुंधरा", "vaishali": "वैशाली",
    "kaushambi": "कौशांबी", "sahibabad": "साहिबाबाद", "loni": "लोनी",
    "modinagar": "मोदीनगर", "muradnagar": "मुराद नगर", "surajpur": "सूरजपुर",
    "raj nagar": "राज नगर", "govindpuram": "गोविंदपुरम", "kavi nagar": "कवि नगर",
    "mohan nagar": "मोहननगर", "rajendra nagar": "राजेंद्रनगर",
}
RECONFIRM = re.compile(r"के आसपास (जॉब|काम)")                      # "…के आसपास जॉब चाहिए?"
OPEN_ASK  = re.compile(r"किस (इलाके|तरफ़?|जगह)|किसी खास इलाके")     # the UNKNOWN-branch wordings
MISMATCH  = re.compile(r"में अभी कोई जॉब नहीं|में जॉब नहीं")          # the LOCATION MISMATCH line


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


def job_places(rec):
    """Every place string carried by the call's jobs, lowercased."""
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
    if loc.lower() in EMPTY or loc.startswith("${") or loc.isdigit():
        return []
    places = job_places(aa.get("recommendations"))
    if not places:
        return []
    key = loc.lower()
    had_jobs = any(key in p for p in places)
    dev = CANON.get(key)
    turns = d.get("call_transcript") or []
    text = " ".join(str(m.get("content") or "") for m in turns if m.get("role") == "assistant")
    created = str(d.get("created_at"))[:19]
    base = dict(bot=bot, call=uuid, at=created, loc=loc, had_jobs="Yes" if had_jobs else "No")
    out = []
    said_reconfirm = bool(RECONFIRM.search(text)) and (dev is None or dev in text)
    said_mismatch = bool(MISMATCH.search(text))
    said_open = bool(OPEN_ASK.search(text))
    if had_jobs:
        if not said_reconfirm and said_open:
            out.append(dict(base, kind="A OPEN ASK ON KNOWN LOC",
                            detail=f"input {loc!r} has jobs, but the bot asked openly instead of reconfirming"))
    else:
        # the input place holds no job — the bot must say so, and must never claim jobs are there
        if dev and re.search(re.escape(dev) + r"\s*(में|मे)\s*(कुछ )?(जॉब|काम)", text) and not said_mismatch:
            out.append(dict(base, kind="B FALSE PLACE CLAIM",
                            detail=f"said jobs are in {loc!r}; no job in the call carries that place"))
        elif not said_mismatch:
            out.append(dict(base, kind="C MISMATCH NOT NAMED",
                            detail=f"input {loc!r} holds no job and the bot never told the caller"))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--since", default=time.strftime("%Y-%m-%d", time.gmtime(time.time() - 86400)))
    ap.add_argument("--agent", default=None)
    ap.add_argument("--workers", type=int, default=4)
    a = ap.parse_args()
    targets = [t for t in json.load(open(os.path.join(REPO, "raya/agents.json")))["targets"]
               if t.get("kind") == "conversation" and t["raya_agent_id"].get("prod")]
    if a.agent:
        targets = [t for t in targets if a.agent in (t["id"], t["raya_agent_id"]["prod"])]
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
                if str(c.get("created_at"))[:19] < a.since:
                    older = True
                    continue
                if (c.get("call_duration") or 0) >= 20:
                    work.append((t["id"], c["uuid"]))
            if older or len(cs) < 100:
                break
            off += 100
    print(f"location reconfirm check | since {a.since} | {len(work)} calls", flush=True)
    bad, errs = [], 0
    with ThreadPoolExecutor(max_workers=a.workers) as ex:
        for res in ex.map(lambda i: _safe(check, i), work):
            if res is None:
                errs += 1
            else:
                bad.extend(res)
    print(f"fetch errors: {errs}\n")
    no_stock = [f for f in bad if f["had_jobs"] == "No"]
    if no_stock:
        print(f"  CAMPAIGN SIGNAL: {len(no_stock)} call(s) were dialled for a place holding no job "
              f"({', '.join(sorted({f['loc'] for f in no_stock}))}) — targeting, not the bot\n")
    if not bad:
        print("  clean — every supplied location was reconfirmed, or its mismatch was named")
        return 0
    for f in bad:
        print(f"  {f['kind']:26} {f['at']}  {f['bot']:20} {f['call']}  location={f['loc']!r} had_jobs={f['had_jobs']}")
        print(f"        {f['detail']}")
    return 1


def _safe(fn, arg):
    try:
        return fn(*arg)
    except Exception:
        return None


if __name__ == "__main__":
    sys.exit(main())
