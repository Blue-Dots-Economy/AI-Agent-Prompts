#!/usr/bin/env python3
"""Detect a bot offering jobs that were never in its ${recommendations} array.

Why this exists (2026-09-08). Slim A/B call 45e2cb3b was given ONE job and deep-dived
four, naming companies that appear only in *previous* calls' arrays. Cause: the Raya
memory store carries `last_options_presented` (KKB/KKB Memory.md:77) into the next call
and the model serves it as current inventory. See raya/overnight/EOD-2026-09-08.md.

Two traps this detector is built to avoid, both of which produced false findings first:

  1. REPETITION. A bot restating the same job three times is not four jobs
     (efaae1b6). We count DISTINCT company names, never line occurrences.
  2. PROMPT-EMBEDDED INVENTORY. Inbound prompts legitimately carry 28-53 hardcoded
     job_id rows, because an inbound caller has no campaign array. Naming a job outside
     the array is CORRECT there (d479bfbc / Udyogini). We skip any bot whose prompt
     carries an inventory table, detected by real UUIDs in the prompt.

Counts distinct Devanagari/Kannada company names spoken in salary lines, so it keeps
working now that role/company/location are converted to native script at point of use.

KNOWN BLIND SPOT -- a clean run is NOT proof of absence. This reads only the DEEP-DIVE
template, where the company is followed by a locative plus punctuation ("महाराजा
इंजीनियरिंग वर्क्स में, गाज़ियाबाद — सैलरी..."). The BATCH-LIST template is comma-only
("पहला: बिलिंग इंजीनियर, काल्को आलू सिस्टम्स प्राइवेट लिमिटेड, गाज़ियाबाद, सैलरी...") and is
NOT parsed, because splitting it on commas produced false positives on real traffic.
On 45e2cb3b -- the call that motivated this file -- the detector sees the one deep-dived
company and misses the two off-array companies in the list line. Widening it to the list
template needs an ordinal/role-position parser that has not been built. Until then, treat
findings as real and silence as unknown.
"""
import glob
import json
import os
import re
import sys

UUID = re.compile(r"\b[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}\b")
# company sits immediately before the locative particle in a deep-dive/list line
# NOTE: \b does not fire after a combining mark (में ends in U+0902), so the
# right-hand boundary is "not another letter of the same script", not \b.
COMPANY_HI = re.compile(r"([ऀ-ॿ][ऀ-ॿ\s\.]{2,40}?)\s*में\s*[,—–-]")
COMPANY_KN = re.compile(r"([ಀ-೿][ಀ-೿\s\.]{2,40}?)\s*(?:ನಲ್ಲಿ|ಯಲ್ಲಿ)\s*[,—–-]")
SALARY = re.compile(r"सैलरी|ಸಂಬಳ")

STOP = {
    # generic words that precede में/ನಲ್ಲಿ but are not company names
    "इस", "इसमें", "उस", "जॉब", "काम", "शहर", "आपके", "हमारे", "बीच", "आपकी",
    "दोनों", "इनमें", "किस", "जिस", "जगह", "पास", "बारे", "और", "यह", "वह",
}


def norm(s):
    return re.sub(r"[\s\.]+", "", s).strip()


def has_inventory(path):
    """True if this prompt carries a hardcoded job table (>=3 real UUIDs)."""
    try:
        with open(path, encoding="utf-8") as fh:
            return len(set(UUID.findall(fh.read()))) >= 3
    except OSError:
        return False


def inventory_bots(repo):
    """Map bot-slug fragment -> True when its prompt embeds an inventory."""
    out = {}
    for p in glob.glob(os.path.join(repo, "*", "*.md")):
        base = os.path.basename(p).lower()
        if "changelog" in base:
            continue
        out[p] = has_inventory(p)
    return out


def companies_spoken(call):
    seen = set()
    for t in call.get("call_transcript") or []:
        if t.get("role") != "assistant":
            continue
        ct = str(t.get("content") or "")
        if not SALARY.search(ct):
            continue
        for rx in (COMPANY_HI, COMPANY_KN):
            for m in rx.findall(ct):
                n = norm(m)
                # keep only the trailing 1-4 words; the regex can swallow lead-in prose
                words = [w for w in re.split(r"\s+", m.strip()) if w]
                tail = norm(" ".join(words[-4:]))
                if not tail or tail in STOP or len(tail) < 4:
                    continue
                if any(w in STOP for w in words[-1:]):
                    continue
                seen.add(tail)
    return collapse(seen)


PREFIX = re.compile(r"^(?:यहजॉब|इसजॉब|जॉब|ಈಕೆಲಸ)")
SUFFIX = re.compile(r"(?:कंपनी|प्राइवेटलिमिटेड|लिमिटेड|ಕಂಪನಿ)$")


def collapse(names):
    """One company said several ways is one company.

    efaae1b6 said "संकल्प सेमीकंडक्टर", "यह जॉब संकल्प सेमीकंडक्टर" and
    "संकल्प सेमीकंडक्टर कंपनी" -- three surface forms, one employer. Strip the
    template prefix/suffix, then fold any name that contains another.
    """
    base = set()
    for n in names:
        n = PREFIX.sub("", n)
        n = SUFFIX.sub("", n)
        if len(n) >= 4:
            base.add(n)
    out = []
    for n in sorted(base, key=len):
        if not any(n in kept or kept in n for kept in out):
            out.append(n)
    return set(out)


def check(cache, repo, verbose=False):
    inv = inventory_bots(repo)
    inv_frag = set()
    for p, flag in inv.items():
        if flag:
            inv_frag.add(os.path.basename(p).lower())
    findings = []
    scanned = 0
    for p in sorted(glob.glob(os.path.join(cache, "*.json"))):
        try:
            call = json.load(open(p, encoding="utf-8"))
        except Exception:
            continue
        aa = call.get("agent_args") or {}
        recs = aa.get("recommendations")
        if not recs:
            continue
        try:
            arr = json.loads(recs) if isinstance(recs, str) else recs
        except Exception:
            continue
        if not isinstance(arr, list) or not arr:
            continue
        bot = str(call.get("_bot") or "")
        # inbound bots serve a prompt-embedded inventory: naming an off-array job is legal
        if any(k in bot for k in ("-in-", "-in", "inbound")) and any(
            "inbound" in f for f in inv_frag
        ):
            continue
        scanned += 1
        spoken = companies_spoken(call)
        if not spoken:
            continue
        if len(spoken) > len(arr):
            findings.append(
                {
                    "uuid": call.get("uuid", "")[:8],
                    "bot": bot,
                    "when": str(call.get("created_at", ""))[:16],
                    "supplied": len(arr),
                    "distinct_spoken": len(spoken),
                    "names": sorted(spoken)[:6],
                }
            )
    return scanned, findings


def selftest():
    def mk(nrec, lines, bot="kkb-hi-signals"):
        return {
            "uuid": "deadbeef-0000",
            "_bot": bot,
            "created_at": "2026-09-08T00:00",
            "agent_args": {
                "recommendations": json.dumps(
                    [{"job_id": "x%d" % i, "role": "R", "company": "C%d" % i} for i in range(nrec)]
                )
            },
            "call_transcript": [{"role": "assistant", "content": l} for l in lines],
        }

    cases = [
        ("one job, one company", mk(1, ["श्री कृष्णा इंडस्ट्री में, सैलरी दस हज़ार"]), 0),
        (
            "one job, three DISTINCT companies -> flag",
            mk(
                1,
                [
                    "श्री कृष्णा इंडस्ट्री में, सैलरी दस हज़ार",
                    "काल्को आलू सिस्टम्स में, सैलरी बारह हज़ार",
                    "ग्रे फैशन प्राइवेट लिमिटेड में, सैलरी चौदह हज़ार",
                ],
            ),
            1,
        ),
        (
            "same company restated 3x -> NOT a finding",
            mk(
                1,
                [
                    "संकल्प सेमीकंडक्टर में, सैलरी दस हज़ार",
                    "संकल्प सेमीकंडक्टर में, सैलरी दस हज़ार",
                    "संकल्प सेमीकंडक्टर में, सैलरी दस हज़ार",
                ],
            ),
            0,
        ),
        (
            "inbound bot naming off-array job -> skipped by design",
            mk(1, ["उद्योगिनी में, सैलरी बारह हज़ार", "सारथी स्टाफिंग में, सैलरी चौदह हज़ार"],
               bot="kkb-hi-in-signals"),
            0,
        ),
        ("no salary line -> ignored", mk(1, ["नमस्ते, कैसे हैं आप?"]), 0),
        (
            "12 supplied, 4 spoken -> fine",
            mk(
                12,
                [
                    "अ कंपनी में, सैलरी दस हज़ार",
                    "ब कंपनी में, सैलरी दस हज़ार",
                    "स कंपनी में, सैलरी दस हज़ार",
                ],
            ),
            0,
        ),
        (
            "kannada, one job two companies -> flag",
            mk(1, ["ಸಂಕಲ್ಪ ಸೆಮಿಕಂಡಕ್ಟರ್ ನಲ್ಲಿ, ಸಂಬಳ ಹತ್ತು ಸಾವಿರ",
                   "ಗ್ರೇ ಫ್ಯಾಶನ್ ನಲ್ಲಿ, ಸಂಬಳ ಹನ್ನೆರಡು ಸಾವಿರ"]),
            1,
        ),
        ("generic 'इस जॉब में' not a company", mk(1, ["इस जॉब में सैलरी दस हज़ार है"]), 0),
        (
            "one employer said 3 ways + a place -> NOT a finding (efaae1b6)",
            mk(
                1,
                [
                    "मुराद नगर में पी.सी.बी. असेंबली टेक्नीशियन की जॉब है। संकल्प सेमीकंडक्टर में, सैलरी दस हज़ार",
                    "यह जॉब संकल्प सेमीकंडक्टर में, सैलरी दस हज़ार",
                    "संकल्प सेमीकंडक्टर कंपनी में, सैलरी दस हज़ार",
                ],
            ),
            0,
        ),
        (
            "locative place before role is not a company",
            mk(1, ["गाज़ियाबाद में सुपरवाइज़र की जॉब है, सैलरी दस हज़ार"]), 0,
        ),
    ]
    import tempfile

    ok = 0
    with tempfile.TemporaryDirectory() as td:
        repo = os.path.join(td, "repo")
        os.makedirs(os.path.join(repo, "KKB"))
        with open(os.path.join(repo, "KKB", "KKB Placeholder Inbound Signals.md"), "w") as fh:
            fh.write("\n".join("| %s | job |" % u for u in
                     ["d479bfbc-1111-2222-3333-444455556666",
                      "aa11bbbb-1111-2222-3333-444455556666",
                      "bb22cccc-1111-2222-3333-444455556666"]))
        for name, call, want in cases:
            cache = os.path.join(td, "c")
            os.makedirs(cache, exist_ok=True)
            for old in glob.glob(os.path.join(cache, "*.json")):
                os.remove(old)
            json.dump(call, open(os.path.join(cache, "a.json"), "w"))
            _, f = check(cache, repo)
            got = len(f)
            mark = "ok  " if got == want else "FAIL"
            if got == want:
                ok += 1
            print("  %s %-46s want=%d got=%d" % (mark, name, want, got))
    print("\nselftest %d/%d" % (ok, len(cases)))
    return 0 if ok == len(cases) else 1


if __name__ == "__main__":
    if "--selftest" in sys.argv:
        sys.exit(selftest())
    cache = os.environ.get(
        "CALLCACHE",
        "/private/tmp/claude-502/-Users-parthbansal-EkStep-Prompt-Tuner/"
        "cad28c14-40a4-477d-993b-eff663bfb052/scratchpad/callcache",
    )
    repo = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    repo = os.path.dirname(repo)
    n, f = check(cache, repo)
    print("offarray_jobs: scanned %d outbound calls with a job array" % n)
    if not f:
        print("  no bot offered more distinct companies than it was given")
        sys.exit(0)
    print("  %d call(s) named MORE distinct companies than supplied:" % len(f))
    for x in f:
        print("   %s %-20s %s supplied=%d spoken=%d %s"
              % (x["uuid"], x["bot"], x["when"], x["supplied"], x["distinct_spoken"], x["names"]))
    sys.exit(1)
