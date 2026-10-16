#!/usr/bin/env python3
"""jobs_presented.py — count jobs actually READ ALOUD, script-independently.

Why this exists: twice now I have graded "how many jobs did it name?" with a Latin-vs-Devanagari
substring match and got 0 when the real answer was 3. The job array is Latin ("Sales executive",
"Alien Energy"); the bot speaks Devanagari ("सेल्स एग्जीक्यूटिव", "एलियन एनर्जी"). Any matcher built on
the array's own strings is a false-negative machine — it is written up as D49 in the analyser and I
walked into it again.

The reliable signal is script-native and language-native: the ORDINAL MARKERS the presentation format
mandates. Hindi "पहला:/दूसरा:/तीसरा:/चौथा:…", Kannada "ಒಂದು:/ಎರಡು:/ಮೂರು:…", plus the "one option"
singular forms. Counting those counts presented jobs without ever touching the array.

Reports, per call: jobs supplied, distinct jobs presented, whether the caller asked for more, and
whether a "that is all we have" line was spoken while any job was still unnamed (the real defect).
Exit 1 only on that last one.

Usage: python3 raya/regression/jobs_presented.py [--since ...] [--agent <id>]
"""
import argparse, json, os, re, sys, time, urllib.request
from concurrent.futures import ThreadPoolExecutor

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
_env = {}
for _l in open(os.path.join(REPO, "raya/.env")):
    _l = _l.strip()
    if "=" in _l and not _l.startswith("#"):
        k, v = _l.split("=", 1); _env[k.strip()] = v.strip().strip('"').strip("'")
BASE = _env["RAYA_BASE_URL"].rstrip("/"); KEY = _env["RAYA_API_TOKEN"]

# Kannada ran only to 6 here, so a Kannada bot could never score above 6 however many jobs it named
# -- arr-kn-1 read out all EIGHT and this list could not see the last two. Both languages run to ten.
ORDINALS = [
    (u"पहला", 1), (u"दूसरा", 2), (u"तीसरा", 3), (u"चौथा", 4),
    (u"पाँचवाँ", 5), (u"पांचवां", 5), (u"छठा", 6),
    (u"सातवाँ", 7), (u"आठवाँ", 8), (u"नौवाँ", 9), (u"नौवां", 9), (u"दसवाँ", 10),
    (u"ಒಂದು", 1), (u"ಎರಡು", 2), (u"ಮೂರು", 3), (u"ನಾಲ್ಕು", 4),
    (u"ಐದು", 5), (u"ಆರು", 6), (u"ಏಳು", 7), (u"ಎಂಟು", 8),
    (u"ಒಂಬತ್ತು", 9), (u"ಹತ್ತು", 10),
    # The prompts now hand the model ordinals to twenty-two (a real campaign sent 22 jobs on
    # c472f2c8). A detector that stops at ten under-counts and turns a good call into a finding.
    (u"ग्यारहवाँ", 11), (u"बारहवाँ", 12), (u"तेरहवाँ", 13), (u"चौदहवाँ", 14), (u"पंद्रहवाँ", 15),
    (u"सोलहवाँ", 16), (u"सत्रहवाँ", 17), (u"अठारहवाँ", 18), (u"उन्नीसवाँ", 19), (u"बीसवाँ", 20),
    (u"इक्कीसवाँ", 21), (u"बाईसवाँ", 22),
    (u"ಹನ್ನೊಂದು", 11), (u"ಹನ್ನೆರಡು", 12), (u"ಹದಿಮೂರು", 13), (u"ಹದಿನಾಲ್ಕು", 14), (u"ಹದಿನೈದು", 15),
    (u"ಹದಿನಾರು", 16), (u"ಹದಿನೇಳು", 17), (u"ಹದಿನೆಂಟು", 18), (u"ಹತ್ತೊಂಬತ್ತು", 19), (u"ಇಪ್ಪತ್ತು", 20),
    (u"ಇಪ್ಪತ್ತೊಂದು", 21), (u"ಇಪ್ಪತ್ತೆರಡು", 22),
]
ONE_OPTION = re.compile(u"एक ऑप्शन है|ಒಂದು ಆಪ್ಷನ್ ಇದೆ")
ASK_MORE = re.compile(u"और कौन|और क्या|बाकी|जो भी जॉब|सारी जॉब|ಬೇರೆ ಯಾವ|ಎಲ್ಲಾ ಹೇಳಿ|ಇನ್ನೇನು")
ALL_TOLD = re.compile(u"सब मैंने बता दीं|इतने ही|इवಿಷ್ಟೇ|ಇವಿಷ್ಟೇ|ಎಲ್ಲಾ ಜಾಬ್‌ಗಳನ್ನ ನಾನು ಹೇಳಿದ್ದೀನಿ|और कोई जॉब नहीं")


def get(path, tries=4):
    for i in range(tries):
        try:
            r = urllib.request.Request(BASE + path, headers={
                "X-API-Key": KEY, "User-Agent": "Mozilla/5.0", "Accept": "application/json"})
            with urllib.request.urlopen(r, timeout=120) as resp:
                return json.loads(resp.read())
        except Exception:
            if i == tries - 1: raise
            time.sleep(1.5 * (i + 1))


def check(bot, uuid):
    d = get("/api/call/" + uuid)
    aa = d.get("agent_args") or {}
    rec = aa.get("recommendations")
    if isinstance(rec, str):
        try: rec = json.loads(rec)
        except Exception: rec = None
    supplied = len(rec) if isinstance(rec, list) else 0
    # Count the SUPPLIED array under the SAME key the spoken side uses (role + company, lowercased).
    # Comparing a role+company-keyed spoken count against the raw array length is apples-to-oranges:
    # on 4982c225 the array held 22 entries but only 18 distinct role+company pairs — five distinct
    # McDonald's Crew Member postings at five Ghaziabad branches and two CY FUTURE posts at different
    # Noida addresses, each with its own job_id. The bot walked all 22 in order, exactly as
    # instructed, and was reported for "naming the same job under two ordinals". A duplicate is only
    # a duplicate when the key is spoken MORE times than the array contains it.
    supplied_key_counts = {}
    if isinstance(rec, list):
        for _j in rec:
            if not isinstance(_j, dict):
                continue
            _k = u", ".join(x for x in (str(_j.get("role") or ""), str(_j.get("company") or "")) if x)
            _k = re.sub(u"\\s+", u" ", _k).strip().lower()
            if _k:
                supplied_key_counts[_k] = supplied_key_counts.get(_k, 0) + 1
    supplied_distinct = len(supplied_key_counts) or supplied
    if not supplied:
        return []
    turns = [str(t.get("content") or "") for t in (d.get("call_transcript") or [])
             if t.get("role") == "assistant" and t.get("content")]
    user = " ".join(str(t.get("content") or "") for t in (d.get("call_transcript") or [])
                    if t.get("role") == "user")
    said = " ".join(turns)
    # Highest ordinal spoken is NOT the presented count: on live call 54a0daa8 the bot reached
    # आठवाँ by naming Solar Energy Consultant twice, under तीसरा AND सातवाँ, leaving the eighth
    # job unspoken. Count DISTINCT job identities instead, read off the words after each ordinal.
    highest = 0
    slots = {}
    for word, n in ORDINALS:
        # Anchor on the mandated "<ordinal>:" -- Kannada number-words nest, so ಹದಿನೆಂಟು ("eighteen",
        # inside a salary) contains ಎಂಟು ("eight") and a bare substring test read a salary as the
        # eighth job -- a bogus duplicate on 15f6d453 and d9bf1f43.
        if re.search(re.escape(word) + u"\\s*:", said):
            highest = max(highest, n)
            m = re.search(u"(?:^|[\\s\u2014\\-*(])" + re.escape(word) + u"\\s*:\\s*([^।\\n]{2,90})", said)
            if m:
                # key on role AND company: two different jobs can share a role ("Data Entry
                # Operator" at two firms) and keying on the role alone called that a duplicate.
                seg = re.sub(u"\\s+", u" ", m.group(1)).strip().lower()
                # Job identity is the job_id and the bot never says it, so this key is the best
                # available proxy: role + company. It cannot be made exact. Two fields raise a false
                # positive on payloads holding posts that differ only by location (a5443b59: two CY
                # FUTURE Customer Support posts, five McDonald's Crew Member posts); three fields
                # raise a false NEGATIVE when one job is described slightly differently on its two
                # mentions, which lost the confirmed duplicate on 54a0daa8. Two fields, erring toward
                # flagging, and the finding is INFORMATIONAL in fleet_report for exactly this reason.
                slots[n] = u", ".join(seg.split(u",")[:2]).strip()
    distinct = len(set(slots.values())) if slots else highest
    _spoken = list(slots.values())
    # Flag only a key spoken MORE times than the supplied array holds it. A payload that carries the
    # same role+company five times (five real postings at five branches) legitimately produces five
    # ordinals; that is the data's shape, not the bot re-presenting anything.
    # The spoken key is a Devanagari/Kannada transliteration and the supplied key is Latin, so they
    # cannot be matched to each other by string equality. What CAN be established is whether the
    # payload contained duplicates at all: if it did not, a repeated spoken key is the bot
    # re-presenting a job; if it did, the repetition is indistinguishable from the bot faithfully
    # walking two array entries that share a role and company, and the check must say so instead of
    # asserting a fault. On 4982c225 the array held five distinct McDonald's Crew Member postings at
    # five Ghaziabad branches, each with its own job_id.
    supplied_has_dupes = any(n > 1 for n in supplied_key_counts.values())
    dupes = sorted(v for v in set(_spoken) if _spoken.count(v) > 1)
    if highest == 0 and ONE_OPTION.search(said):
        highest = distinct = 1
    asked = bool(ASK_MORE.search(user))
    all_told = bool(ALL_TOLD.search(said))
    created = str(d.get("created_at"))[:19]
    base = dict(bot=bot, call=uuid, at=created, supplied=supplied, presented=distinct, asked=asked)
    out = []
    if dupes and not supplied_has_dupes:
        out.append(dict(base, kind="SAME JOB NAMED UNDER TWO ORDINALS",
                        detail=f"ordinals reached {highest} but only {distinct} distinct jobs, and the payload "
                               f"held no duplicate role+company; repeated: {'; '.join(dupes)}"))
    elif dupes:
        out.append(dict(base, kind="REPEAT NOT SEPARABLE FROM PAYLOAD (info)",
                        detail=f"ordinals reached {highest} for {distinct} distinct spoken jobs, but the payload "
                               f"itself holds the same role+company more than once ({supplied} entries, "
                               f"{supplied_distinct} distinct), so a repeat cannot be told from a faithful "
                               f"array walk; repeated: {'; '.join(dupes)}"))
    if all_told and distinct < supplied_distinct:
        out.append(dict(base, kind="ALL-TOLD WHILE JOBS UNNAMED",
                        detail=f"said it had told the caller everything after presenting {distinct} of "
                               f"{supplied_distinct} distinct job(s) ({supplied} array entries)"))
    elif asked and distinct < supplied_distinct:
        out.append(dict(base, kind="ASKED FOR MORE, NOT ALL SHOWN (info)",
                        detail=f"caller asked to hear more; {distinct} of {supplied_distinct} distinct "
                               f"job(s) were presented ({supplied} array entries)"))
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
    ap.add_argument("--workers", type=int, default=3)
    ap.add_argument("--call", action="append", default=[],
                    help="grade only these call uuids (repeatable) -- the list API lags a few minutes")
    a = ap.parse_args()
    targets = [t for t in json.load(open(os.path.join(REPO, "raya/agents.json")))["targets"]
               if t.get("kind") == "conversation" and t["raya_agent_id"].get("prod")]
    if a.agent:
        targets = [t for t in targets if a.agent in (t["id"], t["raya_agent_id"]["prod"])]
    work = []
    if a.call:
        bot = None   # resolved per call by _bot_for_call
        work = [(_bot_for_call(c, targets), c) for c in a.call]
    else:
     for t in targets:
      for c in (get(f"/api/call?agent_id={t['raya_agent_id']['prod']}&limit=100").get("calls") or []):
            if str(c.get("created_at"))[:19] < a.since: continue
            if (c.get("call_duration") or 0) >= 40: work.append((t["id"], c["uuid"]))
    print(f"jobs-presented check | since {a.since} | {len(work)} calls", flush=True)
    bad, errs = [], 0
    with ThreadPoolExecutor(max_workers=a.workers) as ex:
        for res in ex.map(lambda i: _safe(check, i), work):
            if res is None: errs += 1
            else: bad.extend(res)
    print(f"fetch errors: {errs}\n")
    hard = [f for f in bad if "info" not in f["kind"]]
    if not bad:
        print("  clean — no call claimed to be out of jobs while any remained unnamed")
    for f in bad:
        print(f"  {f['kind']:36} {f['at']}  {f['bot']:18} {f['call']}")
        print(f"        supplied={f['supplied']} presented={f['presented']} asked_for_more={f['asked']} — {f['detail']}")
    return 1 if hard else 0


def _safe(fn, arg):
    try: return fn(*arg)
    except Exception: return None


if __name__ == "__main__":
    sys.exit(main())
