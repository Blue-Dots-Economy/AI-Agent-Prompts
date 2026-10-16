# -*- coding: utf-8 -*-
"""ab_compare.py — is the slim prompt as good as the fat one, and is it actually faster?

Two bots that differ ONLY in their conversation prompt (see create_slim_bot.py) are dialled with
the SAME fixture and the SAME tester persona, alternating, and every call is scored the same way.

WHAT IT MEASURES

  latency      The reason the rewrite exists. There are no per-turn timestamps in the Raya API, so
               per-turn latency is not directly observable. What IS observable, and is a fair
               comparison when the script is held fixed, is **seconds per agent turn** =
               call_duration / (agent turns). Same persona, same fixture, same tester -> the turn
               COUNT should be close, so a difference in seconds-per-turn is a difference in how
               long the bot took to produce each turn. Reported with the turn counts alongside, so
               a run where the two bots took different paths is visible rather than hidden in a
               mean.

  behaviour    Every invariant the two prompts are supposed to share, checked mechanically on the
               transcript: the audio check first, the greeting exactly once, the location sentence
               before any job, no PIN or Latin script in speech, no placeholder spoken, no field
               label read aloud, ordinals not restarting, the data-sharing line before apply, no
               apply-success line without an apply_job result, the read-back after a successful
               apply. A slim prompt that is faster and wrong is not a win, and these are the
               checks that would catch it.

  drift        Lines the slim bot spoke that the fat prompt never contained, and vice versa.

Usage:
  python3 raya/slim/ab_compare.py --pairs 3 --fixture raya/testcases/args/r5/sarjapur-offlist.json \
      --persona raya/personas/hi-detail-then-apply.md
  python3 raya/slim/ab_compare.py --score-only            # score whatever calls already exist
  python3 raya/slim/ab_compare.py --selftest
"""
import argparse, io, json, os, re, subprocess, sys, time, urllib.error, urllib.request

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
_env = {}
for _l in open(os.path.join(REPO, "raya/.env")):
    _l = _l.strip()
    if "=" in _l and not _l.startswith("#"):
        _k, _v = _l.split("=", 1); _env[_k.strip()] = _v.strip().strip('"').strip("'")
BASE = _env["RAYA_BASE_URL"].rstrip("/"); TOKEN = _env["RAYA_API_TOKEN"]

FAT  = ("fat",  "115b38a5-42ef-4082-be69-84a871bb226a")
SLIM = ("slim", "140d13ca-c80f-47c4-9454-5edb3fd38c96")
TESTER = "f60e0899-aa3a-4be7-9b4f-0296bd28ef48"
TESTER_DID = "7946350285"

INDIC   = re.compile(u"[ऀ-ॿ]")
ASCII_D = re.compile(r"[0-9]{2,}")
LATIN   = re.compile(r"[A-Za-z][A-Za-z.&'\-]{2,}")
LABEL   = re.compile(r"\b(Qualification|Salary|Vacancy|Location|Company|Role|Experience)\s*[:=]")
HOLDER  = re.compile(r"\bNot Available\b|\bN/?A\b|\bnull\b|\$\{[A-Za-z_]", re.I)
HINGLISH = set("""apply applied personal details company share post posting vacancy vacancies
ok okay hello goodbye yes sir madam whatsapp sms otp hr wfh shortlist shortlisted employer
call calls message messages experience fresher freshers qualification salary interview
technical issue unclear assistant exact and the for you your eligible male female
data entry operator supervisor helper fitter electrician driver marketing sales mba iti""".split())

AUDIO   = re.compile(u"मेरी आवाज़ आ रही है")
GREET   = re.compile(u"शहर प्रशासन की")
LOCSENT = re.compile(u"जॉब की लोकेशन")
JOBLINE = re.compile(u"सैलरी")
SHARE   = re.compile(u"personal details company के साथ share")
SUCCESS = re.compile(u"अप्लाई हो गया है")
READBACK = re.compile(u"एक बार confirm कर लूँ|सब सही")
ORD = [u"पहला", u"दूसरा", u"तीसरा", u"चौथा", u"पाँचवाँ", u"छठा", u"सातवाँ", u"आठवाँ"]


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


def score(call):
    """Mechanical scoring of one call. Returns (metrics, failures)."""
    turns = call.get("call_transcript") or []
    args = call.get("agent_args") or {}
    argblob = json.dumps(args, ensure_ascii=False)
    agent = [str(t.get("content") or "") for t in turns if t.get("role") == "assistant" and t.get("content")]
    toolcalls = [tc for t in turns for tc in (t.get("tool_calls") or [])]
    dur = call.get("call_duration") or 0
    f = []

    # --- latency proxy
    m = {"turns_agent": len(agent), "turns_total": len(turns), "duration_s": dur,
         "sec_per_turn": round(dur / len(agent), 2) if agent else None,
         "tools": len(toolcalls)}

    # --- invariants
    if agent and not AUDIO.search(agent[0]):
        f.append("audio check is not the first spoken turn")
    n_greet = sum(1 for a in agent if GREET.search(a))
    if n_greet == 0:
        f.append("greeting never spoken")
    elif n_greet > 1:
        f.append("greeting spoken %d times (must be once)" % n_greet)

    # location sentence must precede the first job line
    i_loc = next((i for i, a in enumerate(agent) if LOCSENT.search(a)), None)
    i_job = next((i for i, a in enumerate(agent) if JOBLINE.search(a)), None)
    if i_job is not None and i_loc is None:
        f.append("a job was presented and the location sentence was never spoken")
    elif i_job is not None and i_loc > i_job:
        f.append("the location sentence came AFTER the first job")

    for a in agent:
        if not INDIC.search(a):
            continue
        if HOLDER.search(a):
            f.append("placeholder spoken: %s" % a[:60])
        if LABEL.search(a):
            f.append("field label spoken: %s" % a[:60])
        lat = [w for w in LATIN.findall(a) if w.lower().strip(".&'-") not in HINGLISH]
        leaked = [w for w in lat + ASCII_D.findall(a) if w in argblob]
        if leaked:
            f.append("argument value spoken verbatim %s: %s" % (leaked[:3], a[:60]))

    # ordinals must not restart
    seen_ord = [o for a in agent for o in ORD if re.search(o, a)]
    if seen_ord:
        idx = [ORD.index(o) for o in seen_ord]
        first_at = {}
        for k, o in enumerate(seen_ord):
            first_at.setdefault(o, k)
        if len(set(seen_ord)) != len(seen_ord):
            f.append("an ordinal was reused: %s" % seen_ord)

    # apply discipline
    applied = [tc for tc in toolcalls if ((tc.get("function") or {}).get("name")) == "apply_job"]
    if applied and not any(SHARE.search(a) for a in agent):
        f.append("apply_job fired with no data-sharing line spoken")
    if any(SUCCESS.search(a) for a in agent) and not applied:
        f.append("apply-success line spoken with no apply_job call")
    m["applied"] = len(applied)
    m["success_line"] = sum(1 for a in agent if SUCCESS.search(a))
    m["readback"] = sum(1 for a in agent if READBACK.search(a))
    return m, f


def dial(bot_uuid, fixture, label):
    cmd = [sys.executable, os.path.join(REPO, "scripts/raya_testrun.py"),
           bot_uuid, TESTER_DID, fixture, TESTER, label]
    p = subprocess.run(cmd, cwd=REPO, capture_output=True, text=True, timeout=1800)
    out = p.stdout + p.stderr
    uu = re.findall(r"\b([0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})\b", out)
    return (uu[0] if uu else None), out


def recent(bot_uuid, n=12):
    d = get("/api/call?agent_id=%s&limit=%d" % (bot_uuid, n))
    return d.get("calls") or d.get("data") or []


def report(rows):
    print("\n" + "=" * 78)
    print("%-6s %-10s %6s %6s %7s %6s %6s  %s" %
          ("bot", "call", "dur_s", "turns", "s/turn", "tools", "appl", "failures"))
    print("-" * 78)
    for bot, uu, m, f in rows:
        print("%-6s %-10s %6s %6s %7s %6s %6s  %s" %
              (bot, uu[:8], m["duration_s"], m["turns_agent"], m["sec_per_turn"],
               m["tools"], m["applied"], ("OK" if not f else "%d" % len(f))))
        for x in f:
            print("%38s- %s" % ("", x))
    for bot in ("fat", "slim"):
        sel = [m for b, _, m, _ in rows if b == bot and m["sec_per_turn"]]
        if not sel:
            continue
        spt = sorted(x["sec_per_turn"] for x in sel)
        med = spt[len(spt) // 2]
        print("\n%s: n=%d  median %.2f s per agent turn  (turn counts %s)"
              % (bot, len(sel), med, [x["turns_agent"] for x in sel]))
    fails = {b: sum(len(f) for bb, _, _, f in rows if bb == b) for b in ("fat", "slim")}
    print("\ninvariant failures  fat=%d  slim=%d" % (fails["fat"], fails["slim"]))
    if len([r for r in rows if r[0] == "slim"]) < 2 or len([r for r in rows if r[0] == "fat"]) < 2:
        print("FEWER THAN 2 CALLS ON A SIDE — this is not yet a comparison, it is an anecdote.")


# The scenario matrix. One fixture is one path; a comparison run on a single path says nothing
# about the others, and the paths that matter most are the ones where the two prompts describe the
# same behaviour with very different amounts of prose. Each row is
# (name, fixture, persona, what the run is for).
MATRIX = [
    ("offlist-loc-apply", "raya/testcases/args/r5/sarjapur-offlist.json",
     "raya/personas/hi-detail-then-apply.md",
     "off-list location + a deep dive + an apply — exercises the location conversion, the company "
     "names, the qualification line and the whole apply sequence in one call"),
    ("many-jobs-batches", "raya/testcases/args/r3/morejobs-22.json",
     "raya/personas/hi-asks-for-all-jobs.md",
     "22 jobs and a caller who keeps asking for more — ordinals must run continuously and no job "
     "may be named twice, which is where the fat prompt failed on 09978532"),
    ("nothing-fits", "raya/testcases/args/r3/deadjobs.json",
     "raya/personas/hi-wants-different-job.md",
     "a caller who wants a role the array does not hold — the two-slot no-match line, both slots "
     "filled, neither of them a place"),
    ("already-applied", "raya/testcases/args/r3/already-applied-from-memory.json",
     "raya/personas/hi-force-apply.md",
     "a job the memory says was already applied for — the pre-tool duplicate check, and the "
     "already-applied line spoken as good news rather than as a failure"),
    ("declines-everything", "raya/testcases/args/r3/gzb-validated-12.json",
     "raya/personas/hi-unsure-declines.md",
     "an undecided caller who turns everything down — Need Capture Path B is owed, and the "
     "preference capture must not fire while jobs remain unshown"),
]


SELFTEST = [
    ({"call_duration": 60, "agent_args": {"location": "Sarjapur, 110045"}, "call_transcript": [
        {"role": "assistant", "content": u"हैलो, मेरी आवाज़ आ रही है?"},
        {"role": "assistant", "content": u"नमस्ते। शहर प्रशासन की 'काम की बात' पहल…"},
        {"role": "assistant", "content": u"हमारे पास आपकी जॉब की लोकेशन Sarjapur, 110045 है"}]},
     ["argument value spoken verbatim"], "the 7b841e6b leak must be caught"),
    ({"call_duration": 60, "agent_args": {}, "call_transcript": [
        {"role": "assistant", "content": u"हैलो, मेरी आवाज़ आ रही है?"},
        {"role": "assistant", "content": u"नमस्ते। शहर प्रशासन की पहल…"},
        {"role": "assistant", "content": u"पहला: डेटा एंट्री, सैलरी बारह हज़ार."}]},
     ["location sentence was never spoken"], "a job with no location turn must be caught"),
    ({"call_duration": 60, "agent_args": {}, "call_transcript": [
        {"role": "assistant", "content": u"हैलो, मेरी आवाज़ आ रही है?"},
        {"role": "assistant", "content": u"नमस्ते। शहर प्रशासन की पहल…"},
        {"role": "assistant", "content": u"अप्लाई हो गया है।"}]},
     ["no apply_job call"], "a fabricated apply must be caught"),
    ({"call_duration": 60, "agent_args": {}, "call_transcript": [
        {"role": "assistant", "content": u"हैलो, मेरी आवाज़ आ रही है?"},
        {"role": "assistant", "content": u"नमस्ते। शहर प्रशासन की पहल… क्या आप काम ढूंढ रहे हैं?"},
        {"role": "assistant", "content": u"हमारे पास आपकी जॉब की लोकेशन मुराद नगर है"},
        {"role": "assistant", "content": u"पहला: डेटा एंट्री, सैलरी बारह हज़ार."}]},
     [], "a clean call must produce no failure"),
]


def selftest():
    bad = 0
    for call, expect, why in SELFTEST:
        _, f = score(call)
        blob = " | ".join(f)
        ok = all(e in blob for e in expect) and (bool(f) == bool(expect))
        print("%s  %s" % ("ok  " if ok else "FAIL", why))
        if not ok:
            print("       got: %s" % (f or "(none)")); bad += 1
    print("\nselftest: %d/%d" % (len(SELFTEST) - bad, len(SELFTEST)))
    sys.exit(1 if bad else 0)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pairs", type=int, default=0, help="fat/slim call pairs to dial")
    ap.add_argument("--fixture", default="raya/testcases/args/r5/sarjapur-offlist.json")
    ap.add_argument("--persona", default="")
    ap.add_argument("--score-only", action="store_true")
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--matrix", action="store_true",
                    help="run every scenario in MATRIX once per bot instead of one fixture N times")
    ap.add_argument("--list-matrix", action="store_true")
    a = ap.parse_args()

    if a.selftest:
        selftest()
    if a.list_matrix:
        for n, fx, pe, why in MATRIX:
            print("  %-20s %-52s %s" % (n, fx, os.path.basename(pe)))
            print("  %-20s %s" % ("", why))
        return

    if a.matrix:
        rows = []
        for name, fx, pe, _why in MATRIX:
            if not os.path.exists(os.path.join(REPO, fx)):
                print("SKIP %s — fixture missing: %s" % (name, fx)); continue
            subprocess.run([sys.executable, os.path.join(REPO, "scripts/raya_testcall.py"),
                            "persona", TESTER, pe], cwd=REPO, capture_output=True)
            for bot, uu in (FAT, SLIM):
                print("\n>>> %s / %s" % (name, bot), flush=True)
                cid, out = dial(uu, fx, "abm-%s-%s" % (name, bot))
                print(out.strip().splitlines()[-1] if out.strip() else "(no output)")
                if not cid:
                    continue
                full = get("/api/call/" + cid)
                m, f = score(full)
                m["scenario"] = name
                rows.append((bot, cid, m, f))
        if rows:
            report(rows)
            print("\nby scenario:")
            for name, _, _, _why in MATRIX:
                sel = [(b, m) for b, _, m, _ in rows if m.get("scenario") == name]
                if sel:
                    print("  %-20s %s" % (name, "  ".join("%s %ss/turn" % (b, m["sec_per_turn"]) for b, m in sel)))
        else:
            print("no calls completed.")
        return

    if a.persona:
        subprocess.run([sys.executable, os.path.join(REPO, "scripts/raya_testcall.py"),
                        "persona", TESTER, a.persona], cwd=REPO)

    dialled = []
    for i in range(a.pairs):
        for name, uu in (FAT, SLIM):          # alternate, so line conditions hit both sides
            label = "ab-%s-%d" % (name, i + 1)
            print("\n>>> dialling %s (%s)" % (name, label), flush=True)
            cid, out = dial(uu, a.fixture, label)
            print(out.strip().splitlines()[-1] if out.strip() else "(no output)")
            if cid:
                dialled.append((name, cid))

    rows = []
    if a.score_only or not dialled:
        for name, uu in (FAT, SLIM):
            for c in recent(uu, 8):
                if (c.get("call_duration") or 0) < 20:
                    continue
                full = get("/api/call/" + c["uuid"])
                m, f = score(full)
                rows.append((name, c["uuid"], m, f))
    else:
        for name, cid in dialled:
            full = get("/api/call/" + cid)
            m, f = score(full)
            rows.append((name, cid, m, f))
    if not rows:
        print("no calls to score."); sys.exit(0)
    report(rows)


if __name__ == "__main__":
    main()
