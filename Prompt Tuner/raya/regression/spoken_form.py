#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""spoken_form.py — did the bot READ a stored value out instead of SAYING it?

The bug class (2026-09-08, QA calls 5035574 and 5061404). Every script rule in these prompts is
backed by a CLOSED LIST — Canonical Location Spellings, Maya's "Common conversions", the
first-name list. A value ON the relevant list is converted correctly; a value that is not on any
list was passed straight through into speech, in Latin, digits and all. Four proofs, three
different lists, one mechanism:

  7b841e6b  location: "Sarjapur, 110045"        → said "लोकेशन Sarjapur, 110045 है"   (off the location list)
  1536830c  company: "SARA ENTERPRISES"         → said "SARA ENTERPRISES"              (no company list exists)
  9d5e9848  company: "MAHARAJA ENGINEERING…"    → said it, plus "Qualification:"       (the prompt's own label)
  b6353cfb  college_name: "VMLG College"        → said "VMLG College"                  (off Common conversions)

On each of those calls a value that WAS on a list came out right in the same breath — `7b841e6b`
said गाज़ियाबाद, `02c5f7f0` said "ग्लोबल केमिकल्स" out of `GLOBAL CHEMICALS`. So this is not a
transliteration weakness and not model whim: it is a coverage boundary, and it is deterministic.

WHAT THIS FLAGS. An assistant turn that is Indic speech (contains Devanagari or Kannada) and also
carries one of:
  * a Latin word of 3+ letters that is NOT deliberate Hinglish (see HINGLISH below),
  * two or more consecutive ASCII digits — a PIN, a salary or a count that was never spoken,
  * an English field label read aloud ("Qualification:", "Salary:", "Location:").

WHAT IT DELIBERATELY IGNORES. These bots code-mix on purpose and the prompts script it: a Hindi
speaker really does say "अप्लाई", "posting", "vacancy", "shortlist", "technical issue". Flagging
those would bury the real finding under hundreds of false positives — the first version of this
check reported 585 turns, of which the overwhelming majority were the prompts' own scripted
Hinglish. HINGLISH is therefore an explicit allow-list, and anything added to it needs to be a word
the prompt itself writes into a spoken line.

Usage: python3 raya/regression/spoken_form.py [--since YYYY-MM-DD[THH:MM:SS]] [--agent <id>]
       python3 raya/regression/spoken_form.py --call <uuid>
       python3 raya/regression/spoken_form.py --selftest
Times are UTC. Exit 1 if any blocking finding is present.
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

INDIC = re.compile(u"[ऀ-ॿಀ-೿]")
LATIN = re.compile(r"[A-Za-z][A-Za-z.&'\-]{2,}")
ASCII_DIGITS = re.compile(r"[0-9]{2,}")
LABEL = re.compile(r"\b(Qualification|Salary|Vacancy|Vacancies|Location|Company|Role|Experience"
                   r"|Job[_ ]?id|Qty|Positions)\s*[:=]")
# A PLACEHOLDER read out to a caller is never legitimate in any language, so it is matched
# separately and is always blocking. It also must never be reachable through HINGLISH: the first
# version of this file allow-listed "not" and "available" individually, and the DKB opener bug
# ("क्या आप Not Available से बोल रहे हैं?", 7 live calls) walked straight through the check. The
# selftest below exists to keep that hole shut.
PLACEHOLDER = re.compile(r"\bNot Available\b|\bN/?A\b|\bnull\b|\bundefined\b|\bNone\b"
                         r"|\$\{[A-Za-z_][A-Za-z0-9_]*\}", re.I)

# Deliberate code-mixing the prompts script into spoken lines. Lower-cased on comparison.
HINGLISH = set("""
apply applied posting postings post vacancy vacancies candidate candidates record recorded
personal details company share shared ok okay hello hi goodbye bye yes sir madam ma'am
whatsapp sms otp pdf hr wfh work from home part time full time shortlist shortlisted
employer employers call calls message messages experience fresher freshers qualification
salary interview interviews update updated active minimum specific area address name role
technical issue unclear assistant exact and the for you your eligible
data entry operator supervisor helper fitter electrician driver marketing sales
mba bca mca bba iti pf esi cv resume email id link app google form
phone option options timing exact process update team service free note noted
""".split())
# "phone" (from "Phone interview भी हो सकती है"), "option" (from "एक और option है") and "exact"
# (from "Exact timing अलग हो सकती है") are words the prompts WRITE into spoken lines. They surfaced
# as info-level noise on 317bd6e0 and would have trained a reader to skim this check's output.


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


def conv_targets():
    man = json.load(open(os.path.join(REPO, "raya/agents.json"), encoding="utf-8"))
    out = []
    for t in man["targets"]:
        if t.get("kind") != "conversation":
            continue
        uuid = (t.get("raya_agent_id") or {}).get("prod")
        if uuid:
            out.append((t["id"], uuid))
    return out


def scan_turn(text):
    """Return (latin, digits, labels) that survive the allow-list. Empty tuple means clean."""
    if not INDIC.search(text):
        return [], [], [], []      # not Indic speech — an all-English turn is a different bug
    latin = [m.group(0) for m in LATIN.finditer(text) if m.group(0).lower().strip(".&'-") not in HINGLISH]
    digits = ASCII_DIGITS.findall(text)
    labels = [m.group(1) for m in LABEL.finditer(text)]
    holders = [m.group(0) for m in PLACEHOLDER.finditer(text)]
    return latin, digits, labels, holders


def check(bot, uuid):
    c = get("/api/call/" + uuid)
    at = str(c.get("created_at"))[:19]
    args = c.get("agent_args") or {}
    out = []
    for t in (c.get("call_transcript") or []):
        if t.get("role") != "assistant":
            continue
        text = str(t.get("content") or "")
        if not text:
            continue
        latin, digits, labels, holders = scan_turn(text)
        if not (latin or digits or labels or holders):
            continue
        # A hit that matches one of THIS call's own argument values is the confirmed bug: the
        # written value went to the caller untouched. Anything else is still reported, one
        # severity lower, because it may be a model-invented English word rather than a leak.
        argblob = json.dumps(args, ensure_ascii=False)
        from_args = [w for w in latin + digits if w in argblob]
        sev = "blocking" if (holders or from_args or labels) else "info"
        kind = ("PLACEHOLDER SPOKEN TO THE CALLER" if holders else
                "WRITTEN VALUE SPOKEN VERBATIM" if from_args else
                "FIELD LABEL SPOKEN ALOUD" if labels else
                "LATIN / DIGITS IN INDIC SPEECH (info)")
        out.append(dict(bot=bot, call=uuid, at=at, sev=sev, kind=kind,
                        detail="%s%s%s%s :: %s" % (
                            ("placeholder=%s " % holders[:2]) if holders else "",
                            ("latin=%s " % latin[:4]) if latin else "",
                            ("digits=%s " % digits[:4]) if digits else "",
                            ("label=%s " % labels[:2]) if labels else "",
                            text[:150].replace("\n", " "))))
    return out


SELFTEST = [
    # (text, args, expect_blocking, why)
    (u"हमारे पास आपकी जॉब की लोकेशन Sarjapur, 110045 है", {"location": "Sarjapur, 110045"}, True,
     "7b841e6b — the argument value spoken verbatim"),
    (u"हमारे पास आपकी जॉब की लोकेशन मुराद नगर है", {"location": "Muradnagar, 110045"}, False,
     "55a44edb — converted correctly, must not flag"),
    (u"मार्केटिंग, SARA ENTERPRISES में, गाज़ियाबाद", {"recommendations": '[{"company": "SARA ENTERPRISES"}]'}, True,
     "1536830c — company name straight out of the payload"),
    (u"तीन पोज़िशन हैं। Qualification: आईटीआई वेल्डिंग।", {}, True,
     "9d5e9848 — the prompt's own field label read aloud"),
    (u"अप्लाई हो गया है। आमतौर पर अगर shortlist होता है तो employer की तरफ़ से call आता है।", {}, False,
     "02c5f7f0 — deliberate Hinglish the prompt scripts, must not flag"),
    (u"नमस्ते। मैं माया, VMLG College की ओर से बात कर रही हूँ।", {"college_name": "VMLG College"}, True,
     "b6353cfb — college name spoken in Latin"),
    (u"नमस्ते। मैं माया, वीएमएलजी कॉलेज की ओर से बात कर रही हूँ।", {"college_name": "VMLG College"}, False,
     "the fixed form, must not flag"),
    (u"क्या आप Not Available से बोल रहे हैं?", {}, True,
     "564e1d45 — the placeholder string spoken as the business name"),
    (u"ನೀವು Not Available ನಿಂದ ಮಾತಾಡ್ತಾ ಇದ್ದೀರಾ?", {}, True,
     "be4ab8c3 — the same leak in Kannada"),
    (u"आपकी एक posting है — Not Available, Not Available vacancies, सैलरी Not Available।", {}, True,
     "09a7b6c8 — three placeholders in one posting recap"),
    (u"नमस्ते। मैं माया, ${college_name} की ओर से बात कर रही हूँ।", {}, True,
     "718aa8ab — a raw dollar-brace token read aloud (D67)"),
    (u"हैलो, क्या आप एक बिज़नेस ओनर हैं?", {}, False,
     "the correct DKB fallback opener, must not flag"),
]


def selftest():
    bad = 0
    for text, args, want, why in SELFTEST:
        latin, digits, labels, holders = scan_turn(text)
        argblob = json.dumps(args, ensure_ascii=False)
        from_args = [w for w in latin + digits if w in argblob]
        got = bool(holders or from_args or labels)
        mark = "ok  " if got == want else "FAIL"
        if got != want:
            bad += 1
        print("%s want=%-5s got=%-5s  %s" % (mark, want, got, why))
        if got != want:
            print("       latin=%s digits=%s labels=%s placeholders=%s" % (latin, digits, labels, holders))
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
        fs = check("(--call)", a.call)
        for f in fs:
            print("  %-34s %s  %s\n        %s" % (f["kind"], f["at"], f["call"][:8], f["detail"]))
        if not fs:
            print("  (no finding)")
        sys.exit(1 if any(f["sev"] == "blocking" for f in fs) else 0)

    targets = conv_targets()
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
    print("spoken-form check | since %s | %d calls | fetch errors: %d" % (a.since, seen, errs))
    if not jobs:
        print("  NO CALLS IN WINDOW — this check proved nothing. Not a pass.")
        sys.exit(0)
    hard = [f for f in findings if f["sev"] == "blocking"]
    for f in sorted(findings, key=lambda f: (f["sev"] != "blocking", f["at"])):
        print("  %-34s %-19s %-20s %s" % (f["kind"], f["at"], f["bot"], f["call"][:8]))
        print("        %s" % f["detail"])
    if not findings:
        print("  clean")
    sys.exit(1 if hard else 0)


if __name__ == "__main__":
    main()
