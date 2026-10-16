#!/usr/bin/env python3
"""location_integrity.py — detect a profile written with a location the caller never gave.

Bug found 2026-08-31 on call 924e611f: a caller declined to give her area, and
`create_profile` went out with `location: "Bengaluru, Karnataka, India"` — the work city of a
JOB in `${recommendations}`. Her stored profile now claims she lives in a city she never named,
which silently mis-ranks every future recommendation for her.

The fix (Phase-1 city gate + a two-entry candidate list) cannot be exercised by the voice harness:
`contact_phone` is overridden by the dialled number, so every harness call uses the tester DID, and
that number now has a live profile — so the new-caller gate never triggers. This detector closes
the loop on production traffic instead.

FLAGS a call when a profile-write's `location` matches a JOB's location from the same call's
`${recommendations}` and the caller never said that place aloud. Exit 1 if any call is flagged.

Usage: python3 raya/regression/location_integrity.py [--since YYYY-MM-DD] [--agent <uuid>]
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

# Latin <-> Devanagari for the places this fleet actually speaks, so "did the caller say it?"
# is answered script-agnostically. A Latin-only match reports false clean.
TRANSLIT = {
    "ghaziabad": ["गाज़ियाबाद", "गाजियाबाद"], "bengaluru": ["बेंगलुरु", "बंगलोर"],
    "bangalore": ["बेंगलुरु", "बंगलोर"], "noida": ["नोएडा"], "delhi": ["दिल्ली"],
    "meerut": ["मेरठ"], "vasundhara": ["वसुंधरा"], "vaishali": ["वैशाली"],
    "kaushambi": ["कौशांबी"], "sahibabad": ["साहिबाबाद"], "loni": ["लोनी"],
    "indirapuram": ["इंदिरापुरम"], "modinagar": ["मोदीनगर"], "pune": ["पुणे"],
    "nashik": ["नासिक"], "bhopal": ["भोपाल"], "surajpur": ["सूरजपुर"],
    "raj nagar": ["राज नगर"], "govindpuram": ["गोविंदपुराम"], "kavi nagar": ["कवि नगर"],
    "muradnagar": ["मुरादनगर"], "hubli": ["ಹುಬ್ಬಳ್ಳಿ", "हुबली"], "dharwad": ["ಧಾರವಾಡ"],
}


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


def spoken_forms(place):
    """Every string that would count as the caller having said this place."""
    p = place.strip().lower()
    out = {p}
    for token in re.split(r"[,/]", p):
        token = token.strip()
        if len(token) > 2:
            out.add(token)
            out.update(TRANSLIT.get(token, []))
    return {o for o in out if len(o) > 2}


def check(bot, uuid):
    d = get("/api/call/" + uuid)
    args = d.get("agent_args") or {}
    raw = args.get("recommendations") or ""
    # a truncated payload still yields usable job locations by regex (see analyser D42)
    job_locs = set()
    for m in re.finditer(r'"location":\s*"([^"]{2,60})"', raw):
        job_locs.add(m.group(1).strip())
    turns = d.get("call_transcript") or []
    caller = " ".join(str(m.get("content") or "") for m in turns if m.get("role") == "user").lower()
    writes = []
    for m in turns:
        for tc in (m.get("tool_calls") or []):
            fn = tc.get("function") or {}
            if fn.get("name") in ("create_profile", "update_profile"):
                try:
                    a = json.loads(fn.get("arguments") or "{}")
                except Exception:
                    a = {}
                if a.get("location"):
                    writes.append((fn["name"], str(a["location"])))
    findings = []
    for tool, loc in writes:
        said = any(f in caller for f in spoken_forms(loc))
        if said:
            continue
        borrowed = [j for j in job_locs if spoken_forms(j) & spoken_forms(loc)]
        if borrowed:
            findings.append(dict(bot=bot, call=uuid, tool=tool, location=loc,
                                 matched_job_location=borrowed[0],
                                 created_at=str(d.get("created_at"))[:19]))
    return findings


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--since", default=time.strftime("%Y-%m-%d", time.gmtime(time.time() - 86400)))
    ap.add_argument("--agent", default=None)
    ap.add_argument("--workers", type=int, default=4)
    a = ap.parse_args()

    targets = [t for t in json.load(open(os.path.join(REPO, "raya/agents.json")))["targets"]
               if t.get("kind") == "conversation" and t["raya_agent_id"].get("prod")]
    if a.agent:
        targets = [t for t in targets if t["raya_agent_id"]["prod"] == a.agent or t["id"] == a.agent]

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

    print(f"location-integrity check | since {a.since} | {len(work)} calls", flush=True)
    flagged, errors = [], 0
    with ThreadPoolExecutor(max_workers=a.workers) as ex:
        for res in ex.map(lambda i: _safe(check, i), work):
            if res is None:
                errors += 1
            else:
                flagged.extend(res)
    print(f"fetch errors: {errors}")
    print(f"\nprofile writes using a JOB's city the caller never said: {len(flagged)}")
    for f in flagged:
        print(f"  BAD {f['created_at']}  {f['bot']:20} {f['call']}")
        print(f"      {f['tool']}.location = {f['location']!r}  (job location: {f['matched_job_location']!r})")
    if not flagged:
        print("  none — no borrowed job cities detected")
    return 1 if flagged else 0


def _safe(fn, arg):
    try:
        return fn(*arg)
    except Exception:
        return None


if __name__ == "__main__":
    sys.exit(main())
