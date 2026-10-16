#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""location_said.py — WHICH place did the bot name in the location sentence, and was it the
caller's?

The location sentence is one sentence with two slots:

    "हमारे पास आपकी जॉब की लोकेशन ${location} है, और अभी जॉब्स [शहर] में हैं — क्या यह ठीक रहेगा?"

Slot 1 is the caller's place, substituted by the platform. Slot 2 is the jobs' city, read off the
array. Measured over the calls below, that ONE sentence produces FOUR different outcomes, and three
of them are wrong:

    OK           the arg's place words, converted to the target script     36802370, 52689e6c, 09978532
    RAW          the argument verbatim — Latin and/or digits intact        7b841e6b, a5ba6894
    SUBSTITUTED  a different place the model knows in the target script    1450f797 (गाज़ियाबाद),
                                                                          8eb83bc2 (साहिबाबाद)
    ABSENT       no location sentence at all, jobs presented anyway        8674462f

SUBSTITUTED is the worst of the three and the reason this detector exists separately from
`spoken_form.py`, which only catches RAW. A raw value is ugly but true; a substituted one is a
false statement about the caller that also **hides the mismatch the sentence exists to expose** —
on `1450f797` the caller was dialled about Sarjapur and heard "your job location is Ghaziabad, and
the jobs are in Ghaziabad", so the one thing the sentence is for never reached them.

It happens on the SLIM prompt (68k) and the FAT prompt (219k) alike, in the same proportions, so it
is not caused by the surrounding prose and shrinking the prompt does not fix it. See
`ESCALATION-data-team.md` §5 — the fix is an upstream `location_spoken` argument.

Usage: python3 raya/regression/location_said.py [--since YYYY-MM-DD] [--agent <id>]
       python3 raya/regression/location_said.py --call <uuid>
       python3 raya/regression/location_said.py --selftest
Exit 1 if any RAW or SUBSTITUTED call is present.
"""
import argparse, io, json, os, re, sys, time, urllib.error, urllib.request
from concurrent.futures import ThreadPoolExecutor

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
_env = {}
for _l in open(os.path.join(REPO, "raya/.env")):
    _l = _l.strip()
    if "=" in _l and not _l.startswith("#"):
        _k, _v = _l.split("=", 1); _env[_k.strip()] = _v.strip().strip('"').strip("'")
BASE = _env["RAYA_BASE_URL"].rstrip("/"); TOKEN = _env["RAYA_API_TOKEN"]

# slot 1 of the location sentence, both languages
SENT_HI = re.compile(u"जॉब की लोकेशन\\s*(.{1,60}?)\\s*है")
SENT_KN = re.compile(u"ಜಾಬ್\\s*ಲೊಕೇಶನ್\\s*(.{1,60}?)\\s*ಅಂತ")
JOBLINE = re.compile(u"सैलरी|ಸ್ಯಾಲರಿ")
LATIN = re.compile(r"[A-Za-z]{3,}")
DIGIT = re.compile(r"[0-9०-९೦-೯]")

# Canonical spellings the prompts carry. A spoken place from this list that is NOT in the argument
# is the substitution signature: the model reached for a place it already knew in the script.
CANON = {
    u"गाज़ियाबाद": "ghaziabad", u"इंदिरापुरम": "indirapuram", u"मोहननगर": "mohan nagar",
    u"राजेंद्रनगर": "rajendra nagar", u"वसुंधरा": "vasundhara", u"वैशाली": "vaishali",
    u"कौशांबी": "kaushambi", u"साहिबाबाद": "sahibabad", u"लोनी": "loni", u"मोदीनगर": "modinagar",
    u"मुराद नगर": "muradnagar", u"सूरजपुर": "surajpur", u"राज नगर": "raj nagar",
    u"गोविंदपुरम": "govindpuram", u"कवि नगर": "kavi nagar", u"नोएडा": "noida",
    u"दिल्ली": "delhi", u"मेरठ": "meerut", u"बेंगलुरु": "bengaluru",
    u"ಹುಬ್ಬಳ್ಳಿ": "hubli", u"ಧಾರವಾಡ": "dharwad", u"ಕೊರಮಂಗಲ": "koramangala",
}


def get(path, tries=6):
    for i in range(tries):
        try:
            req = urllib.request.Request(BASE + path, headers={"X-API-Key": TOKEN,
                                                               "User-Agent": "Mozilla/5.0"})
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
    raise RuntimeError(path)


def classify(arg_location, agent_turns, caller_turns, has_sentence=True):
    """-> (verdict, spoken, detail). Verdict in OK / RAW / SUBSTITUTED / ABSENT / NA.

    `caller_turns` must contain ONLY what the caller said BEFORE the location sentence. Passing the
    whole call excuses every substitution: the tester personas repeat proper nouns back to record
    what they heard, so the bot says साहिबाबाद, the caller echoes साहिबाबाद, and "the caller named it
    themselves" -- the exemption that exists for af627b9d -- fires on the bot's own mistake. That
    silently downgraded 8eb83bc2 and f90a0b97 to OK.
    """
    spoken = None
    for a in agent_turns:
        m = SENT_HI.search(a) or SENT_KN.search(a)
        if m:
            spoken = m.group(1).strip(u" ।,.-")
            break
    presented = any(JOBLINE.search(a) for a in agent_turns)

    if spoken is None:
        if not has_sentence:
            return "NA", None, "this bot's prompt has no two-slot location sentence to check"
        if presented and arg_location:
            return "ABSENT", None, "jobs were presented and the location sentence was never spoken"
        return "NA", None, "no location sentence and no job presented"

    if not arg_location or str(arg_location).startswith("${"):
        return "NA", spoken, "no location argument to compare against"

    # RAW: the spoken slot still carries Latin letters or digits
    if LATIN.search(spoken) or DIGIT.search(spoken):
        return "RAW", spoken, "the argument's written form was spoken as-is"

    # SUBSTITUTED: a canonical place was spoken whose English form is absent from the argument,
    # and the caller never said it either.
    #
    # Spelling variants matter here. The campaign sends "Hubballi" and the canonical Kannada form is
    # ಹುಬ್ಬಳ್ಳಿ, whose English key in CANON is "hubli" -- so a CORRECT conversion looked like a
    # substitution and 6286926f (a clean end-to-end success) was flagged. Same trap for
    # Bengaluru/Bangalore and Mysuru/Mysore. Normalise the argument through the aliases before
    # deciding anything.
    ALIASES = {"hubli": ("hubli", "hubballi", "hubbali"),
               "dharwad": ("dharwad", "dharwar"),
               "bengaluru": ("bengaluru", "bangalore", "bengalooru"),
               "mysuru": ("mysuru", "mysore"),
               "ghaziabad": ("ghaziabad", "gaziabad"),
               "muradnagar": ("muradnagar", "murad nagar"),
               "koramangala": ("koramangala", "koramangla")}
    argl = str(arg_location).lower()
    said_by_caller = " ".join(caller_turns)
    for dev, eng in CANON.items():
        forms = ALIASES.get(eng, (eng,))
        if dev in spoken and not any(f in argl for f in forms) and dev not in said_by_caller:
            return ("SUBSTITUTED", spoken,
                    "spoke %r; the argument was %r and the caller never named it" % (dev, arg_location))
    return "OK", spoken, "converted from the argument"


TESTER_DID = "1204404272"   # tester agent f60e0899 since 2026-09-23 (7946350285 was rebound to a Purple Dots bot)


def check(bot, uuid, has_sentence=True):
    c = get("/api/call/" + uuid)
    turns = c.get("call_transcript") or []
    agent = [str(t.get("content") or "") for t in turns if t.get("role") == "assistant" and t.get("content")]
    # caller turns BEFORE the location sentence only -- see classify()
    cut = len(turns)
    for i, t in enumerate(turns):
        if t.get("role") == "assistant" and t.get("content") and (
                SENT_HI.search(str(t["content"])) or SENT_KN.search(str(t["content"]))):
            cut = i
            break
    caller = [str(t.get("content") or "") for t in turns[:cut]
              if t.get("role") == "user" and t.get("content")]
    arg = (c.get("agent_args") or {}).get("location")
    v, spoken, detail = classify(arg, agent, caller, has_sentence)
    # HARNESS calls must be counted separately, never folded into a production rate. The tester
    # DID's stored profile carries `location: "Sahibabad, Ghaziabad, India"`, so a fixture that
    # sends any other place creates a profile-vs-argument conflict on EVERY harness dial -- exactly
    # the condition the precedence bug needs. Nine "substitution" calls were reported as a
    # production rate of 8-in-16 before this split was added; all nine were harness dials and not
    # one was a real caller. (input_coverage.py had the identical flaw for the identical reason.)
    harness = TESTER_DID in str(c.get("to_number") or "") or TESTER_DID in str(c.get("caller_no") or "")
    return dict(bot=bot, call=uuid, at=str(c.get("created_at"))[:19], verdict=v,
                arg=arg, spoken=spoken, detail=detail, harness=harness)


# The two-slot location SENTENCE does not exist in every prompt. Maya and the KKB
# outbound/inbound prompts ask about the area with their own wording, so "the location sentence was
# never spoken" is meaningless for them -- the first version of this file reported 3 such calls as
# ABSENT failures (maya-hi-signals 08a8ff4f, maya-hi-out 78ef362f, kkb-kn-out 1b7fb500) when Maya
# had in fact asked "आप गाज़ियाबाद में किस इलाके के पास काम करना चाहेंगे". Scope is therefore read
# from the PROMPT FILES rather than hard-coded, so adding the sentence to another prompt brings that
# bot into the check automatically and removing it takes the bot out.
SENTENCE_MARKERS = (u"जॉब की लोकेशन", u"ಜಾಬ್ ಲೊಕೇಶನ್")


def targets():
    man = json.load(open(os.path.join(REPO, "raya/agents.json"), encoding="utf-8"))
    out = []
    for t in man["targets"]:
        if t.get("kind") != "conversation" or (t.get("agent") or "").upper() not in ("KKB", "MAYA"):
            continue
        uu = (t.get("raya_agent_id") or {}).get("prod")
        if not uu:
            continue
        try:
            body = io.open(os.path.join(REPO, t["file"]), encoding="utf-8").read()
        except Exception:
            continue
        has_sentence = any(m in body for m in SENTENCE_MARKERS)
        out.append((t["id"], uu, has_sentence))
    return out


SELFTEST = [
    ("Sarjapur, 110045", [u"हमारे पास आपकी जॉब की लोकेशन सरजापुर है, और अभी जॉब्स गाज़ियाबाद में हैं"], [],
     "OK", "09978532 / 52689e6c — converted off-list value"),
    ("Sarjapur, 110045", [u"हमारे पास आपकी जॉब की लोकेशन Sarjapur, 110045 है, और अभी जॉब्स गाज़ियाबाद में हैं"], [],
     "RAW", "7b841e6b — raw Latin + PIN"),
    ("10987, Sarhanpur", [u"हमारे पास आपकी जॉब की लोकेशन 10987, Sarhanpur है, और अभी जॉब्स गाज़ियाबाद में हैं"], [],
     "RAW", "a5ba6894 — PIN-first shape, raw"),
    ("Sarjapur, 110045", [u"हमारे पास आपकी जॉब की लोकेशन गाज़ियाबाद है, और अभी जॉब्स गाज़ियाबाद, वसुंधरा में हैं"], [],
     "SUBSTITUTED", "1450f797 — spoke the jobs' city as the caller's place"),
    ("Sarjapur, 110045", [u"हमारे पास आपकी जॉब की लोकेशन साहिबाबाद है, और अभी जॉब्स गाज़ियाबाद, नोएडा में हैं"], [],
     "SUBSTITUTED", "8eb83bc2 — same failure on the SLIM prompt"),
    ("Muradnagar, 110045", [u"हमारे पास आपकी जॉब की लोकेशन मुराद नगर है, और अभी जॉब्स गाज़ियाबाद में हैं"], [],
     "OK", "55a44edb — on-list value, converted"),
    ("Hubballi", [u"ನಮ್ಮ ಹತ್ರ ನಿಮ್ಮ ಜಾಬ್ ಲೊಕೇಶನ್ ಹುಬ್ಬಳ್ಳಿ ಅಂತ ಇದೆ, ಮತ್ತೆ ಈಗ ಜಾಬ್‌ಗಳು ಹುಬ್ಬಳ್ಳಿಯಲ್ಲಿ ಇವೆ"], [],
     "OK", "6286926f — Hubballi -> ಹುಬ್ಬಳ್ಳಿ is CORRECT; the alias must not read as a substitution"),
    ("Muradnagar, 110045", [u"पहला: फील्ड मार्केटिंग एग्जीक्यूटिव, बेलिंक, सैलरी अठारह हज़ार"], [],
     "ABSENT", "8674462f — jobs presented, location turn skipped"),
    ("Sarjapur, 110045", [u"आपके लिए गाज़ियाबाद में कुछ जॉब्स हैं। आप गाज़ियाबाद में किस इलाके के पास काम करना चाहेंगे?",
                          u"कैशियर और पैकर, क्वेस कॉर्प लिमिटेड में — सैलरी तेरह हज़ार"], [],
     "NA", "08a8ff4f — Maya has no two-slot sentence; asking its own way is not a failure", False),
    ("Muradnagar, 110045", [u"हमारे पास आपकी जॉब की लोकेशन बेंगलुरु है, और अभी जॉब्स वसुंधरा में हैं"],
     [u"बेंगलुरु में कहीं भी ठीक है"],
     "OK", "af627b9d — the CALLER said Bengaluru BEFORE the sentence, so it is not a substitution"),
    ("Sarjapur, 110045", [u"हमारे पास आपकी जॉब की लोकेशन साहिबाबाद है, और अभी जॉब्स गाज़ियाबाद में हैं"], [],
     "SUBSTITUTED", "8eb83bc2 / f90a0b97 / fa9a16c0 — साहिबाबाद is a CANONICAL-LIST member, not the "
     "argument; the caller echoing it afterwards must NOT excuse it"),
]


def selftest():
    bad = 0
    for row in SELFTEST:
        arg, agent, caller, want, why = row[:5]
        has_sentence = row[5] if len(row) > 5 else True
        got, spoken, detail = classify(arg, agent, caller, has_sentence)
        ok = got == want
        print("%s want=%-11s got=%-11s  %s" % ("ok  " if ok else "FAIL", want, got, why))
        if not ok:
            print("       spoken=%r detail=%s" % (spoken, detail)); bad += 1
    print("\nselftest: %d/%d" % (len(SELFTEST) - bad, len(SELFTEST)))
    sys.exit(1 if bad else 0)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--since", default=time.strftime("%Y-%m-%d", time.gmtime()))
    ap.add_argument("--agent", default="")
    ap.add_argument("--call", default="")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()

    if a.selftest:
        selftest()
    if a.call:
        r = check("(--call)", a.call)
        print("  %-12s %s  arg=%r spoken=%r\n        %s"
              % (r["verdict"], r["call"][:8], r["arg"], r["spoken"], r["detail"]))
        sys.exit(1 if r["verdict"] in ("RAW", "SUBSTITUTED") else 0)

    tg = targets()
    if a.agent:
        tg = [t for t in tg if a.agent in (t[0], t[1])]
    scoped = [t[0] for t in tg if t[2]]
    print("bots whose prompt carries the location sentence: %s" % (", ".join(scoped) or "(none)"))
    jobs = []
    for bot, uu, has_sentence in tg:
        off = 0
        while off < 600:
            d = get("/api/call?agent_id=%s&limit=100&offset=%d" % (uu, off))
            calls = d.get("calls") or d.get("data") or []
            if not calls:
                break
            for c in calls:
                if c["created_at"] >= a.since and (c.get("call_duration") or 0) >= 20:
                    jobs.append((bot, c["uuid"], has_sentence))
            if calls[-1]["created_at"] < a.since:
                break
            off += 100
        time.sleep(0.2)

    rows, errs = [], 0
    with ThreadPoolExecutor(max_workers=6) as ex:
        for r in ex.map(lambda bu: _safe(check, bu), jobs):
            if r is None:
                errs += 1
            else:
                rows.append(r)
    print("location-said check | since %s | %d calls | fetch errors: %d" % (a.since, len(rows), errs))
    if not rows:
        print("  NO CALLS IN WINDOW — this check proved nothing. Not a pass.")
        sys.exit(0)
    real = [r for r in rows if not r["harness"]]
    harn = [r for r in rows if r["harness"]]
    for label, sel in (("REAL CALLERS", real), ("harness dials", harn)):
        if not sel:
            print("  %-14s (none in window)" % label); continue
        t = {}
        for r in sel:
            t[r["verdict"]] = t.get(r["verdict"], 0) + 1
        print("  %-14s %s" % (label, "  ".join("%s=%d" % (k, t[k]) for k in sorted(t))))
    tally = {}
    for r in real:
        tally[r["verdict"]] = tally.get(r["verdict"], 0) + 1
    for r in sorted(rows, key=lambda r: (r["verdict"] not in ("RAW", "SUBSTITUTED"), r["at"])):
        if r["verdict"] in ("OK", "NA"):
            continue
        print("  %-12s %-19s %-22s %s%s" % (r["verdict"], r["at"], r["bot"], r["call"][:8],
                                            "  [harness]" if r["harness"] else ""))
        print("        %s" % r["detail"])
    bad = tally.get("RAW", 0) + tally.get("SUBSTITUTED", 0)
    if not bad:
        print("  no RAW or SUBSTITUTED calls FROM A REAL CALLER (harness findings above, if any, "
              "may be fixture artefacts -- check the tester profile's stored location first)")
    sys.exit(1 if bad else 0)


def _safe(fn, arg):
    try:
        return fn(*arg)
    except Exception:
        return None


if __name__ == "__main__":
    main()
