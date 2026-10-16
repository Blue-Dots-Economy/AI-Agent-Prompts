#!/usr/bin/env python3
"""inbound_location_consent.py — the two checks that only make sense on an INBOUND call.

Why this exists: `location_reconfirm.py` reads the location from `agent_args.location` — the value a
CAMPAIGN supplies. Inbound calls have no such arg: the caller dials in and the location comes from
`get_profile` or `${contact_memory}`. So every inbound call fell straight through that detector's
first guard and was never graded on location at all. On 2026-09-03 `bbdb6eaf` fetched a profile
carrying "Delhi, India", asked the caller openly which area she wanted anyway, and then read out
Ghaziabad jobs. The nightly reported that bot as clean on location.

Checks:

  L OPEN ASK ON KNOWN PROFILE LOCATION — `get_profile` returned a usable `location` and the bot asked
    the open area question ("किस इलाके में देखें …") instead of confirming what it already held. The
    prompt's rule is confirm-then-wait; re-asking a fact we hold is the bug the caller notices.

  M PRESENTED JOBS IN ANOTHER CITY WITHOUT NAMING THE MISMATCH — the profile location and the cities
    of the jobs read aloud do not overlap, and the bot never said so.

  K CONSENT DISCLOSURE DROPPED — `apply_job` ran and the caller was asked to apply, but the
    data-sharing SENTENCE was never spoken. This is deliberately narrower than
    `consent_before_apply.py`: it fires when the apply QUESTION is present and the DISCLOSURE half is
    missing, which is how it actually fails — on `bbdb6eaf` the bot said "क्या मैं आपकी तरफ़ से अप्लाई
    कर दूँ?" and dropped "आपकी personal details company के साथ share होंगी". The model keeps the half
    that advances the call and drops the half that does not.

Usage: python3 raya/regression/inbound_location_consent.py [--since YYYY-MM-DDTHH:MM:SS] [--agent id]
Times are UTC. Exit 1 on any finding.
"""
import argparse, json, os, re, sys, time, urllib.request
from concurrent.futures import ThreadPoolExecutor

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
_env = {}
for _l in open(os.path.join(REPO, "raya/.env")):
    _l = _l.strip()
    if "=" in _l and not _l.startswith("#"):
        k, v = _l.split("=", 1); _env[k.strip()] = v.strip().strip('"').strip("'")
BASE = _env["RAYA_BASE_URL"].rstrip("/"); TOKEN = _env["RAYA_API_TOKEN"]

EMPTY = {"", "none", "null", "na", "n/a", "not available", "any", "-"}
OPEN_ASK = re.compile(u"किस इलाके में देखें|किस इलाके के पास|कोई खास जगह|ಯಾವ ಏರಿಯಾ|ಯಾವ ಕಡೆ")
CONFIRM = re.compile(u"के आसपास ही देखें|आसपास ही देखें|ಸುತ್ತಮುತ್ತ")
MISMATCH = re.compile(u"में अभी|वहाँ अभी|में जॉब्स नहीं|ಅಲ್ಲಿ ಈಗ|ಇಲ್ಲ")
APPLY_Q = re.compile(u"अप्लाई कर दूँ|अप्लाई कर दूं|ಅಪ್ಲೈ ಮಾಡ್ಲಾ|ಅಪ್ಲೈ ಮಾಡಲಾ")
DISCLOSE = re.compile(u"personal details|ಮಾಹಿತಿ ಕಂಪನಿ|details company")
CANON = {
    "ghaziabad": u"गाज़ियाबाद", "delhi": u"दिल्ली", "noida": u"नोएडा", "meerut": u"मेरठ",
    "indirapuram": u"इंदिरापुरम", "vasundhara": u"वसुंधरा", "vaishali": u"वैशाली",
    "kaushambi": u"कौशांबी", "sahibabad": u"साहिबाबाद", "greater noida": u"नोएडा",
    "bengaluru": u"बेंगलुरु", "bangalore": u"बेंगलुरु", "koramangala": u"कोरमंगला",
    "hubballi": u"ಹುಬ್ಬಳ್ಳಿ", "hubli": u"ಹುಬ್ಬಳ್ಳಿ", "dharwad": u"ಧಾರವಾಡ",
}
CITY = re.compile(u"गाज़ियाबाद|गाजियाबाद|नोएडा|दिल्ली|बेंगलुरु|ಹುಬ್ಬಳ್ಳಿ|ಧಾರವಾಡ|ಬೆಂಗಳೂರು")


def get(path):
    req = urllib.request.Request(BASE + path, headers={"X-API-Key": TOKEN, "User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=90) as r:
        return json.loads(r.read() or b"{}")


def profile_location(tr):
    for t in tr:
        if t.get("role") == "tool" and "user_id" in str(t.get("content") or ""):
            c = str(t["content"])
            if "profile_1.0" not in c:
                continue
            m = re.search(r"'location': '([^']*)'", c)
            if m:
                return m.group(1).strip()
    return ""


def check(bot, uuid):
    d = get("/api/call/" + uuid)
    tr = d.get("call_transcript") or []
    said = " ".join(str(t.get("content") or "") for t in tr if t.get("role") == "assistant")
    loc = profile_location(tr)
    applies = sum(1 for t in tr for tc in (t.get("tool_calls") or [])
                  if (tc.get("function") or {}).get("name") == "apply_job")
    at = str(d.get("created_at"))[:19]
    base = dict(bot=bot, call=uuid, at=at, loc=loc or "-")
    out = []
    if loc and loc.lower() not in EMPTY:
        if OPEN_ASK.search(said) and not CONFIRM.search(said):
            out.append(dict(base, kind="L OPEN ASK ON KNOWN PROFILE LOCATION",
                            detail="profile carried %r and the bot asked the open area question anyway" % loc))
        # Compare EVERY comma-part of the profile location, transliterated, against the cities
        # actually spoken. Two earlier mistakes here: taking only the first part (so
        # "Vasundhara, Ghaziabad" vs जॉब्स in गाज़ियाबाद read as a mismatch when it is a match), and
        # comparing Latin profile text against Devanagari speech, which never matches — the same
        # trap written up as D49.
        cities = set(CITY.findall(said))
        parts = [p.strip().lower() for p in loc.split(",") if p.strip()]
        spoken_forms = {CANON[p] for p in parts if p in CANON}
        overlap = bool(spoken_forms & cities)
        known = bool(spoken_forms)
        if cities and known and not overlap and not MISMATCH.search(said):
            out.append(dict(base, kind="M JOBS IN ANOTHER CITY, MISMATCH NOT NAMED",
                            detail="profile %r (%s), jobs read aloud in %s, no mismatch spoken"
                                   % (loc, "/".join(sorted(spoken_forms)), sorted(cities))))
    if applies and APPLY_Q.search(said) and not DISCLOSE.search(said):
        out.append(dict(base, kind="K CONSENT DISCLOSURE DROPPED",
                        detail="asked to apply and called apply_job, but never said the details would be shared"))
    return out


def _bot_for_call(uuid, targets):
    """Label a --call finding with the bot that call ACTUALLY belongs to.

    This used to be `targets[0]["id"]` — the first target in the manifest, checked against nothing.
    On 2026-09-04 a real finding on call 4982c225 (agent 115b38a5 = kkb-hi-signals) printed against
    `kkb-hi-out`, a different prompt file on a different backend. A report that names the wrong bot
    sends whoever reads it to the wrong prompt.
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
    ap.add_argument("--workers", type=int, default=3)
    ap.add_argument("--call", action="append", default=[])
    a = ap.parse_args()
    targets = [t for t in json.load(open(os.path.join(REPO, "raya/agents.json")))["targets"]
               if t.get("direction") == "inbound" and (t.get("raya_agent_id") or {}).get("prod")]
    if a.agent:
        targets = [t for t in targets if t["id"] == a.agent]
    work = []
    if a.call:
        work = [(_bot_for_call(c, targets), c) for c in a.call]
    else:
        for t in targets:
            for c in (get("/api/call?agent_id=%s&limit=60" % t["raya_agent_id"]["prod"]).get("calls") or []):
                if str(c.get("created_at"))[:19] < a.since:
                    continue
                if (c.get("call_duration") or 0) >= 40:
                    work.append((t["id"], c["uuid"]))
    print("inbound location+consent check | since %s | %d calls" % (a.since, len(work)), flush=True)
    findings = []
    with ThreadPoolExecutor(max_workers=a.workers) as ex:
        for res in ex.map(lambda w: check(*w), work):
            findings.extend(res)
    for f in sorted(findings, key=lambda x: x["kind"]):
        print("  %-40s %-19s %-20s %s" % (f["kind"], f["at"], f["bot"], f["call"]))
        print("        %s" % f["detail"])
    if not findings:
        print("  clean — known locations confirmed rather than re-asked, and no apply without the disclosure")
    sys.exit(1 if findings else 0)


if __name__ == "__main__":
    main()
