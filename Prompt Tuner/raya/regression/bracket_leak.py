#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""bracket_leak.py — did the bot read a SLOT MARKER or a stage direction out to the caller?

Every spoken template in these prompts is built from `[slot]` markers — `[company_name]`,
`[job_role]`, `[role]`, `[शहर]`. They are instructions about what belongs in that position. On 13
live calls across 6 bots the model spoke the marker instead of filling it, and the prompts had no
rule about it at all: they cover `*( )*` stage directions and tool payloads, and say nothing about
the brackets their own templates are made of.

The worst of them are not placeholders but INTERNAL notes:

    1131d79c  "क्या आप [company_name] से बोल रहे हैं?"                       asked of that business's owner
    1131d79c  "आपकी एक posting है — [job_role], [num_vacancies] vacancies"
    f391ab35  "[Proceeding to Phase 2]"  and
              "[INTERNAL: update_job_status called with status \"open\" …]"
    1b7fb500  "[UUID from create_profile result]"                            spoken aloud
    78ef362f  "[UUID from create_profile]"

FLAGS (blocking) any assistant turn containing a bracketed marker, a `*( )*` stage direction, or a
line beginning `INTERNAL`. There is no legitimate reason for any of them to reach a caller, so
unlike the other spoken-form checks this one has no allow-list and no info tier.

Usage: python3 raya/regression/bracket_leak.py [--since YYYY-MM-DD] [--agent <id>]
       python3 raya/regression/bracket_leak.py --call <uuid>
       python3 raya/regression/bracket_leak.py --selftest
Exit 1 on any finding.
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

# A slot marker: [snake_case], [CamelCase], [Some words], [देवनागरी]. Deliberately NOT matching a
# bare number in brackets, which never appears in these templates.
MARKER = re.compile(r"\[[A-Za-z_][A-Za-z0-9_ :\"'.]{2,60}\]|\[[ऀ-ॿಀ-೿][^\]]{0,30}\]")
STAGE = re.compile(r"\*\([^)]{3,}\)\*")
INTERNAL = re.compile(r"(?m)^\s*\[?INTERNAL\b")


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


def scan(text):
    return MARKER.findall(text) + STAGE.findall(text) + (["INTERNAL line"] if INTERNAL.search(text) else [])


def check(bot, uuid):
    c = get("/api/call/" + uuid)
    out = []
    for t in (c.get("call_transcript") or []):
        if t.get("role") != "assistant":
            continue
        text = str(t.get("content") or "")
        hits = scan(text) if text else []
        if hits:
            out.append(dict(bot=bot, call=uuid, at=str(c.get("created_at"))[:19],
                            hits=hits[:3], line=text[:130].replace("\n", " ")))
    return out


def targets():
    man = json.load(open(os.path.join(REPO, "raya/agents.json"), encoding="utf-8"))
    return [(t["id"], t["raya_agent_id"]["prod"]) for t in man["targets"]
            if t.get("kind") == "conversation" and (t.get("raya_agent_id") or {}).get("prod")]


SELFTEST = [
    (u"हैलो! क्या आप [company_name] से बोल रहे हैं?", True, "1131d79c — the slot marker asked aloud"),
    (u"आपकी एक posting है — [job_role], [num_vacancies] vacancies, सैलरी [salary]।", True,
     "1131d79c — three markers in one line"),
    (u"[INTERNAL: update_job_status called with status \"open\" for the job]", True,
     "f391ab35 — an internal note spoken"),
    (u"[Proceeding to Phase 2]", True, "f391ab35 — a stage direction spoken"),
    (u"profile_id: [UUID from create_profile result]", True, "1b7fb500 / 78ef362f"),
    (u"*(Silent tool call: apply_job)*", True, "29c4f152 — a parenthetical stage direction"),
    (u"हैलो! क्या आप वैन्स ट्रेडिंग कंपनी से बोल रहे हैं?", False, "the filled form must not flag"),
    (u"पहला: डेटा एंट्री ऑपरेटर, काशी इंफोटेक, गाज़ियाबाद, सैलरी बारह हज़ार से सोलह हज़ार.", False,
     "a normal job line must not flag"),
    (u"आपके पास कितने साल का काम का experience है?", False, "plain speech must not flag"),
]


def selftest():
    bad = 0
    for text, want, why in SELFTEST:
        got = bool(scan(text))
        ok = got == want
        print("%s want=%-5s got=%-5s  %s" % ("ok  " if ok else "FAIL", want, got, why))
        if not ok:
            print("       hits=%s" % scan(text)); bad += 1
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
            print("  SPOKEN MARKER %s %s\n        %s :: %s" % (f["at"], f["call"][:8], f["hits"], f["line"]))
        if not fs:
            print("  (no finding)")
        sys.exit(1 if fs else 0)

    tg = targets()
    if a.agent:
        tg = [t for t in tg if a.agent in t]
    jobs = []
    for bot, uu in tg:
        off = 0
        while off < 600:
            d = get("/api/call?agent_id=%s&limit=100&offset=%d" % (uu, off))
            calls = d.get("calls") or d.get("data") or []
            if not calls:
                break
            for c in calls:
                if c["created_at"] >= a.since and (c.get("call_duration") or 0) >= 15:
                    jobs.append((bot, c["uuid"]))
            if calls[-1]["created_at"] < a.since:
                break
            off += 100
        time.sleep(0.2)
    findings, errs, seen = [], 0, 0
    with ThreadPoolExecutor(max_workers=6) as ex:
        for r in ex.map(lambda bu: _safe(check, bu), jobs):
            if r is None:
                errs += 1
            else:
                findings += r; seen += 1
    print("bracket-leak check | since %s | %d calls | fetch errors: %d" % (a.since, seen, errs))
    if not jobs:
        print("  NO CALLS IN WINDOW — this check proved nothing. Not a pass.")
        sys.exit(0)
    for f in sorted(findings, key=lambda f: f["at"]):
        print("  SPOKEN MARKER %-19s %-22s %s" % (f["at"], f["bot"], f["call"][:8]))
        print("        %s :: %s" % (f["hits"], f["line"]))
    if not findings:
        print("  clean — no marker, stage direction or INTERNAL line reached a caller")
    sys.exit(1 if findings else 0)


def _safe(fn, arg):
    try:
        return fn(*arg)
    except Exception:
        return None


if __name__ == "__main__":
    main()
