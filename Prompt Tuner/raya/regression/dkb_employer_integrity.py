#!/usr/bin/env python3
"""dkb_employer_integrity.py — the first runtime behaviour check for the EMPLOYER rail.

Until 2026-09-03 every runtime detector was seeker-side: jobs presented, apply outcomes, location
chain, consent-before-apply. DKB posts and updates real job vacancies for MSME owners and had NEVER
been graded on a transcript. `fleet_report.py` reported it NO-DETECTORS for exactly this reason.

Checks, per DKB call:

  P  POSTED WITH NO WRITE RESULT — the bot told the owner the job is posted/updated while no
     successful create_job or update_job result exists in the call. This is the employer-side twin of
     the seeker bug on 19616c90/29c4f152, and it is worse: the owner stops looking for candidates and
     no vacancy exists. (The narration guard on create_job/update_job was added the same day.)
  N  NARRATED A WRITE — the reply contains a stage direction like "(calling create_job)". The caller
     hears it, and it means nothing was written.
  C  POSTED WITHOUT CONSENT — a create_job with no posting-consent question ("post कर दूँ?" /
     "post ಮಾಡಲಾ?") anywhere before it.
  G  CLAIMED TO BE GOVERNMENT — DKB introduces as the city administration's employment initiative,
     never as a government programme. Fixed on 2026-09-03; this keeps it fixed.
  F  FABRICATED A JOB DETAIL — spoke a salary or vacancy count while the corresponding input arg was
     absent or the "Not Available" sentinel. DKB inventing an expiry, a role, a salary or a vacancy
     count was a real reported bug.

Usage: python3 raya/regression/dkb_employer_integrity.py [--since YYYY-MM-DDTHH:MM:SS] [--agent id]
Times are UTC. Exit 1 if any P/N/C finding is present (G and F are reported as major, P/N/C blocking).
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

POSTED = re.compile(u"post कर दिया|पोस्ट कर दिया|post हो गया|पोस्ट हो गया|डाल दिया|"
                    u"ಪೋಸ್ಟ್ ಆಗಿದೆ|ಪೋಸ್ಟ್ ಮಾಡಿದೆ|ಹಾಕಿದೆ|update कर दिया|अपडेट कर दिया")
CONSENT = re.compile(u"post कर दूँ|post कर दूं|पोस्ट कर दूँ|ಪೋಸ್ಟ್ ಮಾಡಲಾ|post ಮಾಡಲಾ")
NARRATE = re.compile(r"\([^)]{0,30}(create_job|update_job|tool call)[^)]{0,30}\)", re.I)
# Self-identification only. "government job" as a TOPIC is legitimate; claiming to BE the
# government is the bug -- b1b71d68 said "main government employment program ki taraf se call kar
# rahi hoon", which is what the 2026-09-03 identity fix removed.
GOVT = re.compile(u"गवर्नमेंट एम्प्लॉयमेंट|सरकारी एम्प्लॉयमेंट|गवर्नमेंट की तरफ|सरकार की तरफ|"
                  u"गवर्नमेंट के साथ मिलकर|ಸರ್ಕಾರದ ಪರವಾಗಿ|ಸರ್ಕಾರಿ ಉದ್ಯೋಗ ಕಾರ್ಯಕ್ರಮ")


def get(path):
    req = urllib.request.Request(BASE + path, headers={"X-API-Key": TOKEN, "User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=90) as r:
        return json.loads(r.read() or b"{}")


def grade(bot, uuid):
    d = get("/api/call/" + uuid)
    tr = d.get("call_transcript") or []
    said = " ".join(str(t.get("content") or "") for t in tr if t.get("role") == "assistant")
    args = d.get("agent_args") or {}
    writes, ok_writes = 0, 0
    for t in tr:
        for tc in (t.get("tool_calls") or []):
            if (tc.get("function") or {}).get("name") in ("create_job", "update_job"):
                writes += 1
        if t.get("role") == "tool":
            c = str(t.get("content") or "")
            if ("item_id" in c or "'success'" in c) and "Error" not in c:
                ok_writes += 1
    at = str(d.get("created_at"))[:19]
    base = dict(bot=bot, call=uuid, at=at)
    out = []
    if POSTED.search(said) and ok_writes == 0:
        out.append(dict(base, kind="P POSTED WITH NO WRITE RESULT", sev="blocking",
                        detail="told the owner the vacancy is posted/updated with no successful "
                               "create_job or update_job result in the call (%d write attempts)" % writes))
    if NARRATE.search(said):
        out.append(dict(base, kind="N NARRATED A WRITE", sev="blocking",
                        detail="a stage direction about the write tool was spoken to the owner"))
    if writes and not CONSENT.search(said):
        out.append(dict(base, kind="C POSTED WITHOUT CONSENT", sev="blocking",
                        detail="create_job/update_job ran with no posting-consent question before it"))
    if GOVT.search(said):
        out.append(dict(base, kind="G CLAIMED TO BE GOVERNMENT", sev="major",
                        detail="DKB is the city administration's initiative, never a government programme"))
    # F must fire on an ASSERTION, never on the question. Collecting these values IS the job: with
    # salary absent the bot rightly asks "is kaam ke liye salary kya soch rahe hain aap?", and an
    # earlier version of this check called that a fabrication. Only a stated number counts, and only
    # when the bot is telling the owner the value rather than asking for it.
    ASSERT_SAL = re.compile(u"सैलरी[^?।\n]{0,24}?(?:है|होगी|रखी|तय)|ಸ್ಯಾಲರಿ[^?।\n]{0,24}?(?:ಇದೆ|ಇರುತ್ತೆ)")
    ASSERT_VAC = re.compile(u"(?:वैकेंसी|पोज़िशन|पोजीशन)[^?।\n]{0,24}?(?:है|हैं)|(?:ಖಾಲಿ|ಪೊಸಿಷನ್)[^?।\n]{0,24}?(?:ಇದೆ|ಇವೆ)")
    for field, pat in (("salary", ASSERT_SAL), ("num_vacancies", ASSERT_VAC)):
        v = str(args.get(field) or "").strip()
        if not (not v or v.lower() in ("not available", "na", "none")):
            continue
        for m in pat.finditer(said):
            frag = m.group(0)
            # a number in the asserted clause, and the owner never supplied one
            if re.search(u"[0-9]|हज़ार|हजार|ಸಾವಿರ", frag):
                out.append(dict(base, kind="F ASSERTED AN UNSUPPLIED JOB DETAIL", sev="major",
                                detail="stated %s as fact (%r) while the input arg was %r — DKB may ASK "
                                       "for a missing value, never state one" % (field, frag.strip()[:60], v or "absent")))
                break
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
               if t.get("agent") == "DKB" and (t.get("raya_agent_id") or {}).get("prod")]
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
    print("dkb employer-integrity check | since %s | %d calls" % (a.since, len(work)), flush=True)
    findings = []
    with ThreadPoolExecutor(max_workers=a.workers) as ex:
        for res in ex.map(lambda w: grade(*w), work):
            findings.extend(res)
    for f in sorted(findings, key=lambda x: x["kind"]):
        print("  %-32s %-19s %-16s %s" % (f["kind"], f["at"], f["bot"], f["call"]))
        print("        %s" % f["detail"])
    if not findings:
        print("  clean — no false posting claims, no narrated writes, consent present, no fabricated details")
    sys.exit(1 if any(f["sev"] == "blocking" for f in findings) else 0)


if __name__ == "__main__":
    main()
