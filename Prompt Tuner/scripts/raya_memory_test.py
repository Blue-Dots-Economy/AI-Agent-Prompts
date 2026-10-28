#!/usr/bin/env python3
"""Memory test for a Raya voice bot: does the second call remember the first?

  check  <bot>                          read-only: is memory wired up for this bot?
  run    <bot> --fact name=Aisha [--fact area=Malpe ...] [--reask name="your name"]
               [--direction out|in] [--gap 180] [--seed P1.md] [--recall P2.md] [--args a.json]
                                        call 1 (the caller gives the facts), wait for the memory to be
                                        written, call 2 from the SAME number, then grade call 2
  grade  <call1_uuid> <call2_uuid> --fact ... [--reask ...]
                                        grade two calls that already happened (e.g. from the console)
  platform                              is Raya carrying memory between calls AT ALL on this account?
                                        Two calls to the memory probe (an agent that reads its stored
                                        memory aloud); run it when a bot forgets, before blaming the bot
  restore-tester <saved.json>           put the shared tester back if a run was cut off
  probe-create --like <bot>             make the memory probe on a new account (copies the bot's
                                        language, voice and outbound number), then records its uuid

<bot> is an agents.json target id or a raw agent uuid.

How Raya memory works (each point proven on live calls, see the /voice-test skill, "Memory"):
  * memory_enabled=true + memory_instructions (the writer prompt) on the agent. After every call the
    writer turns the call into a stored memory for that phone number; on the next call the platform
    puts it into ${contact_memory}. contact_memory sent in agent_args is DISCARDED when memory is on.
  * The bot only sees it if its conversation prompt has the injection block, verbatim:
        ### Contact context / Here is the caller context: / {${contact_memory}}
  * There is no API to read a stored memory. The probe (reads its OWN memory aloud) and the console
    (https://console.getraya.app/memories) are the only views. 2026-10-28: on the EkStep account memory
    was NOT carried over at all (probe calls bd332b65, 63ce32c9, 51359f4b, 8d872d33 all "Nothing
    stored"; Orange Dots asked "Aisha" for her name again 4 times over 2 days). Run `platform` first.
  * Direction: "out" = the bot dials the tester (memory is kept against the tester's in_did); "in" =
    the tester dials the bot's in_did, a real inbound call (memory is kept against the tester's
    out_did). Keep both calls in the same direction unless you are testing exactly that.

Writes raya/testcases/runs/memory-<date>/<label>/ : the personas, both full call JSONs, report.md.
Env: raya/.env (RAYA_BASE_URL, RAYA_API_TOKEN). The token is never printed.
"""
import argparse, datetime, json, os, re, subprocess, sys, time, urllib.error, urllib.request

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_env = {}
_envp = os.path.join(REPO, "raya/.env")
if os.path.exists(_envp):
    for _l in open(_envp):
        _l = _l.strip()
        if "=" in _l and not _l.startswith("#"):
            k, v = _l.split("=", 1); _env[k.strip()] = v.strip()
for _k in ("RAYA_BASE_URL", "RAYA_API_TOKEN"):
    if os.environ.get(_k):
        _env[_k] = os.environ[_k].strip()
BASE = _env.get("RAYA_BASE_URL", "").rstrip("/")
KEY = _env.get("RAYA_API_TOKEN", "")
ENV = os.environ.get("RAYA_ENV", "prod")
TESTER = "f60e0899-aa3a-4be7-9b4f-0296bd28ef48"     # "Testing Agent- Blue Dots" (see /voice-test → Setup)
BLOCK = "### Contact context\nHere is the caller context:\n{${contact_memory}}"
PROBE_FILE = os.path.join(REPO, "raya/memory-probe.json")   # this account's probe agent (not carried by /upgrade)
PROBE_DIR = os.path.join(REPO, ".claude/skills/voice-test/reference/memory-probe")


def req(method, path, body=None):
    data = json.dumps(body).encode() if body is not None else None
    h = {"X-API-Key": KEY, "User-Agent": "Mozilla/5.0"}
    if data is not None:
        h["Content-Type"] = "application/json"
    r = urllib.request.Request(BASE + path, data=data, headers=h, method=method)
    try:
        with urllib.request.urlopen(r, timeout=60) as f:
            raw = f.read().decode()
            d = json.loads(raw) if raw.strip() else {}
            return f.status, (d.get("data", d) if isinstance(d, dict) and "data" in d and isinstance(d["data"], dict) else d)
    except urllib.error.HTTPError as e:
        return e.code, {"_error": e.read().decode()[:400]}


def agent(u):
    st, a = req("GET", "/api/agent/" + u)
    if st != 200:
        sys.exit(f"cannot read agent {u}: HTTP {st} (another Raya account? see raya/agents.json 'account')")
    return a


def uuid_for(t):
    if len(t) == 36 and t.count("-") == 4:
        return t
    rows = json.load(open(os.path.join(REPO, "raya/agents.json"), encoding="utf-8"))["targets"]
    row = next((r for r in rows if r["id"] == t), None)
    if not row:
        sys.exit(f"unknown bot {t!r}: an agents.json id or an agent uuid")
    u = (row.get("raya_agent_id") or {}).get(ENV, "")
    return u or sys.exit(f"{t}: no {ENV} uuid in raya/agents.json")


def mask(n):
    s = re.sub(r"\D", "", str(n or ""))
    return ("XXXXXX" + s[-4:]) if len(s) >= 10 else (str(n) if n else "none")


# ---------------------------------------------------------------- check
def check(bot_uuid, direction="out", quiet=False):
    """Return a list of (ok, line). Problems that make a memory test meaningless are ok=False."""
    a = agent(bot_uuid)
    ins = a.get("instructions") or ""
    out = []
    out.append((bool(a.get("memory_enabled")), "memory switched on (memory_enabled)"))
    out.append((bool((a.get("memory_instructions") or "").strip()),
                "memory writer prompt present (memory_instructions)"))
    out.append((BLOCK in ins, "conversation prompt has the memory block word for word "
                              "(### Contact context / Here is the caller context: / {${contact_memory}})"))
    if direction == "in":
        out.append((bool(a.get("in_did")), f"bot has an inbound number to dial (in_did {mask(a.get('in_did'))})"))
    else:
        out.append((bool(a.get("out_did")), f"bot has an outbound number (out_did {mask(a.get('out_did'))})"))
    # Not a blocker: every bot proven to remember also has an output prompt; recorded so a failure can
    # be compared against it.
    out.append((None, "call report prompt present (output_instructions): "
                      + ("yes" if (a.get("output_instructions") or "").strip() else "no")))
    if not quiet:
        print(f"{a.get('name')}  ({bot_uuid})")
        for ok, line in out:
            print(("  ok    " if ok else "  info  " if ok is None else "  FAIL  ") + line)
        if not all(ok for ok, _ in out if ok is not None):
            print("\n  -> fix the FAIL lines first: a memory test on this bot cannot pass until they are fixed.")
    return out


# ---------------------------------------------------------------- personas
def personas(facts, run_dir):
    told = "\n".join(f"- {k.replace('_', ' ')}: {v}" for k, v in facts)
    seed = f"""# Tester persona: memory test, call 1 (the first call)

You are a caller phoning this helpline for the first time. Speak the same language the agent speaks.
Keep every reply short (one or two sentences), like a real person on the phone.

These are your details. Say each of them in this call, clearly, the first time it fits: if the agent
asks, answer; if it has not asked by your third reply, say the rest yourself.
{told}

Do not make up any other personal details. When the agent has your details and has helped you, say
thank you and goodbye.
"""
    recall = f"""# Tester persona: memory test, call 2 (calling back)

You are calling this helpline AGAIN. You called a little while ago and told the agent these details:
{told}

Speak the same language the agent speaks. Keep every reply short, like a real person on the phone.

1. Open with: "Hi, I called a little while ago." Then ask for help with the same thing as last time.
2. Do NOT repeat any of your details yourself. If the agent asks for one you already gave, say
   "I told you that last time" once, and only if it asks again, give the detail.
3. Before saying goodbye, ask: "Do you remember what I told you last time?" Listen to the answer.
4. Then say thank you and goodbye.
"""
    p1, p2 = os.path.join(run_dir, "persona-call1.md"), os.path.join(run_dir, "persona-call2.md")
    open(p1, "w", encoding="utf-8").write(seed)
    open(p2, "w", encoding="utf-8").write(recall)
    return p1, p2


# ---------------------------------------------------------------- calls
def turns(call):
    return [(t.get("role"), str(t.get("content") or "")) for t in (call.get("call_transcript") or [])
            if t.get("role") in ("user", "assistant") and t.get("content")]


def tester_busy(minutes=8):
    """Another wave on the shared tester line ruins both runs (one persona at a time)."""
    ps = subprocess.run(["ps", "aux"], capture_output=True, text=True).stdout
    if re.search(r"raya_testrun|overnight_sweep|run_smoke", ps):
        return "a test run is already going on this machine"
    st, d = req("GET", f"/api/call?agent_id={TESTER}&limit=1")
    for c in (d.get("calls") or [])[:1]:
        age = (datetime.datetime.utcnow() - datetime.datetime.strptime(c["created_at"][:19], "%Y-%m-%dT%H:%M:%S")).total_seconds()
        if age < minutes * 60:
            return f"the tester placed a call {int(age // 60)} min ago (someone may be mid-run)"
    return None


def save_tester(run_dir):
    """The tester is shared: keep its persona and language on disk BEFORE changing anything."""
    t = agent(TESTER)
    saved = {k: t.get(k) for k in ("instructions", "language_id", "voice_id")}
    path = os.path.join(run_dir, "tester-before.json")
    json.dump(saved, open(path, "w", encoding="utf-8"), ensure_ascii=False)
    return saved, path


def restore_tester(saved, path):
    """Put the tester back, retrying for ~10 minutes. On 2026-10-28 a dropped connection skipped the
    restore and other people's calls ran on a memory-test persona for 10 hours."""
    for i in range(20):
        try:
            st, d = req("PATCH", "/api/agent/" + TESTER, saved)
            if st == 200 and (d.get("instructions") or "").strip() == (saved["instructions"] or "").strip():
                print("tester persona and language restored")
                return
        except Exception as e:
            print(f"tester restore attempt {i + 1} failed: {e}")
        time.sleep(30)
    print(f"!! THE TESTER WAS NOT RESTORED. Other people's test calls will use the memory-test persona.\n"
          f"   Restore it now: python3 scripts/raya_memory_test.py restore-tester {os.path.relpath(path, REPO)}")


def one_call(bot_uuid, direction, args_path, label, log_dir):
    """Place one call through raya_testrun.py (it retries the connect and polls). Returns the bot leg."""
    t0 = datetime.datetime.utcnow()
    if direction == "in":
        b = agent(bot_uuid)
        to = re.sub(r"\D", "", str(b.get("in_did")))[-10:]
        cmd = [sys.executable, os.path.join(REPO, "scripts/raya_testrun.py"), TESTER, to, args_path, TESTER, label]
    else:
        t = agent(TESTER)
        to = re.sub(r"\D", "", str(t.get("in_did")))[-10:]
        cmd = [sys.executable, os.path.join(REPO, "scripts/raya_testrun.py"), bot_uuid, to, args_path, TESTER, label]
    log = subprocess.run(cmd, capture_output=True, text=True).stdout
    open(os.path.join(log_dir, f"{label}.log"), "w", encoding="utf-8").write(log)
    if direction == "out":
        m = re.search(r"BOT ([0-9a-f-]{36}) outcome=Completed", log)
        if not m:
            return None
        return req("GET", "/api/call/" + m.group(1))[1]
    # inbound: the bot's own leg is a separate call on the bot agent
    for _ in range(12):
        st, d = req("GET", f"/api/call?agent_id={bot_uuid}&limit=3")
        for c in d.get("calls") or []:
            if c["created_at"][:19] >= t0.strftime("%Y-%m-%dT%H:%M:%S"):
                full = req("GET", "/api/call/" + c["uuid"])[1]
                if full.get("outcome") == "Completed" and turns(full):
                    return full
        time.sleep(15)
    return None


# ---------------------------------------------------------------- grading
def grade(call1, call2, facts, reask):
    """Each fact: did call 1 carry it (the caller said it), and in call 2 did the bot use it before the
    caller repeated it, and did it ask for it again?"""
    rows, verdicts = [], []
    t1, t2 = turns(call1), turns(call2)
    for k, v in facts:
        val = v.lower()
        said = any(r == "user" and val in c.lower() for r, c in t1)
        first_user = next((i for i, (r, c) in enumerate(t2) if r == "user" and val in c.lower()), None)
        used_at = next((i for i, (r, c) in enumerate(t2) if r == "assistant" and val in c.lower()), None)
        used_before = used_at is not None and (first_user is None or used_at < first_user)
        pat = reask.get(k)
        asked = [c for r, c in t2 if r == "assistant" and pat and re.search(pat, c, re.I)]
        if not said:
            verdict = "INVALID (the caller never said it in call 1, so there was nothing to remember)"
        elif used_before and not asked:
            verdict = "REMEMBERED"
        elif used_before and asked:
            verdict = "MIXED (used it, but also asked for it again)"
        elif asked:
            verdict = "FORGOTTEN (asked for it again)"
        elif first_user is not None:
            verdict = "NOT USED (the caller said it again before the bot used it)"
        else:
            verdict = "NOT USED (never asked, never used)"
        verdicts.append(verdict.split()[0])
        rows.append((k, v, verdict, t2[used_at][1][:160] if used_before else "", asked[0][:160] if asked else ""))
    # The caller's own "do you remember?" question: quote the bot's answer, it is the plainest readout.
    ans = ""
    for i, (r, c) in enumerate(t2):
        if r == "user" and re.search(r"remember", c, re.I):
            nxt = next((c2 for r2, c2 in t2[i + 1:] if r2 == "assistant"), "")
            ans = nxt[:300]
    if "INVALID" in verdicts or not verdicts:
        overall = "INVALID"
    elif all(x == "REMEMBERED" for x in verdicts):
        overall = "PASS"
    else:
        overall = "FAIL"
    return overall, rows, ans


def report(overall, rows, ans, call1, call2, cfg, out_path, gap=None):
    L = [f"# Memory test: {overall}", ""]
    L.append(f"- Call 1 (caller gives the details): `{call1.get('uuid')}`  to {mask(call1.get('to_number'))}")
    L.append(f"- Call 2 (same number, calling back): `{call2.get('uuid')}`  to {mask(call2.get('to_number'))}"
             + (f", placed {gap} s after call 1 ended" if gap else ""))
    if call1.get("to_number") and call2.get("to_number") and call1.get("to_number") != call2.get("to_number"):
        L.append("- **The two calls went to DIFFERENT numbers, so memory could not carry over. Not a valid test.**")
    L.append("")
    L.append("| Detail | Value | Result | Bot's line that used it | Bot asked again |")
    L.append("|---|---|---|---|---|")
    for k, v, verdict, used, asked in rows:
        L.append(f"| {k} | {v} | {verdict} | {used or ''} | {asked} |")
    L.append("")
    L.append(f"**Asked \"do you remember what I told you?\", the bot said:** {ans or '(the question was not asked)'}")
    if cfg:
        bad = [line for ok, line in cfg if ok is False]
        if bad:
            L.append("")
            L.append("**Set-up problems found first (fix these, then re-run):**")
            L += [f"- {b}" for b in bad]
    L.append("")
    if overall == "FAIL":
        L.append("Before changing the bot, run `python3 scripts/raya_memory_test.py platform`: if the probe "
                 "also forgets, the cause is Raya, not this bot.")
    text = "\n".join(L) + "\n"
    if out_path:
        open(out_path, "w", encoding="utf-8").write(text)
    print(text)


# ---------------------------------------------------------------- platform probe
def probe_uuid():
    if not os.path.exists(PROBE_FILE):
        sys.exit("no memory probe on this account yet: python3 scripts/raya_memory_test.py probe-create --like <bot>")
    return json.load(open(PROBE_FILE))["uuid"]


def probe_create(like):
    b = agent(uuid_for(like))
    rd = lambda f: open(os.path.join(PROBE_DIR, f), encoding="utf-8").read()
    body = {"name": "ZZ Lab - memory probe (Prompt Tuner)", "instructions": rd("probe-prompt.md"),
            "language_id": b.get("language_id"), "voice_id": b.get("voice_id"), "out_did": b.get("out_did"),
            "say_hello": True, "max_call_duration_mins": 3}
    st, d = req("POST", "/api/agent", body)          # create rejects the memory fields: PATCH them after
    u = (d or {}).get("uuid")
    if st not in (200, 201) or not u:
        sys.exit(f"create failed {st}: {str(d)[:300]}")
    st2, d2 = req("PATCH", "/api/agent/" + u, {"memory_enabled": True, "memory_instructions": rd("probe-memory.md")})
    if st2 != 200:
        sys.exit(f"probe {u} created but memory did not switch on ({st2}); PATCH it by hand or delete it")
    json.dump({"_note": "This account's memory probe (scripts/raya_memory_test.py platform).", "uuid": u,
               "name": body["name"]}, open(PROBE_FILE, "w"), indent=2)
    print(f"memory probe {u} created; recorded in raya/memory-probe.json")


def platform(gap, force):
    """Two calls to the probe from the tester's number. Call 2 should read back call 1's name."""
    u = probe_uuid()
    busy = tester_busy()
    if busy and not force:
        sys.exit(f"tester line busy: {busy}. Wait, or pass --force if you know it is free.")
    stamp = datetime.datetime.now().strftime("%Y-%m-%d")
    run_dir = os.path.join(REPO, "raya/testcases/runs", f"memory-{stamp}", "platform")
    os.makedirs(run_dir, exist_ok=True)
    args_path = os.path.join(run_dir, "args.json"); open(args_path, "w").write("{}")
    pr = agent(u)
    saved, saved_path = save_tester(run_dir)
    first = []
    try:
        req("PATCH", "/api/agent/" + TESTER, {"language_id": pr.get("language_id"), "voice_id": pr.get("voice_id")})
        subprocess.run([sys.executable, os.path.join(REPO, "scripts/raya_testcall.py"), "persona", TESTER,
                        os.path.join(PROBE_DIR, "persona.md")], check=True)
        for n in (1, 2):
            c = one_call(u, "out", args_path, f"platform-call{n}", run_dir)
            if not c:
                sys.exit(f"probe call {n} never connected; see {os.path.relpath(run_dir, REPO)}")
            json.dump(c, open(os.path.join(run_dir, f"{c['uuid']}.json"), "w"), ensure_ascii=False, indent=1)
            said = next((x for r, x in turns(c) if r == "assistant"), "")
            first.append((c["uuid"], said))
            print(f"probe call {n} {c['uuid']}: {said[:300]}")
            if n == 1:
                time.sleep(gap)
    finally:
        restore_tester(saved, saved_path)
    # The speech-to-text often mishears the name (Meera -> Meeta, Mita), so test for ANY stored memory,
    # not for the exact name. Memory from an earlier probe run also counts: it was carried over.
    ok = "nothing stored" not in first[1][1].lower()
    print("\nRaya memory on this account: " + ("WORKING (call 2 read back a stored memory)" if ok else
          "NOT CARRIED OVER (call 2 read back nothing from call 1). A bot that forgets is not the bot's "
          "fault until this passes; report it to the platform with these two call ids."))
    sys.exit(0 if ok else 1)


# ---------------------------------------------------------------- main
def parse_facts(items):
    out = []
    for f in items or []:
        if "=" not in f:
            sys.exit(f"--fact must be key=value, got {f!r}")
        k, v = f.split("=", 1); out.append((k.strip(), v.strip()))
    return out


def main():
    p = argparse.ArgumentParser(description="Memory test for a Raya voice bot (two calls, same number).")
    sub = p.add_subparsers(dest="cmd", required=True)
    c = sub.add_parser("check"); c.add_argument("bot"); c.add_argument("--direction", choices=["out", "in"], default="out")
    for name in ("run", "grade"):
        s = sub.add_parser(name)
        if name == "run":
            s.add_argument("bot")
            s.add_argument("--direction", choices=["out", "in"], default="out")
            s.add_argument("--gap", type=int, default=180, help="seconds to wait after call 1 for the memory to be written")
            s.add_argument("--seed"); s.add_argument("--recall")
            s.add_argument("--args", help="agent_args JSON for the bot (default {})")
            s.add_argument("--label", default="memory")
            s.add_argument("--force", action="store_true", help="run even if the tester line looks busy")
        else:
            s.add_argument("call1"); s.add_argument("call2")
        s.add_argument("--fact", action="append", required=True, help="key=value the caller gives in call 1")
        s.add_argument("--reask", action="append", default=[], help='key="regex" for the bot asking for it again')
    pl = sub.add_parser("platform"); pl.add_argument("--gap", type=int, default=180); pl.add_argument("--force", action="store_true")
    rt = sub.add_parser("restore-tester"); rt.add_argument("saved_json")
    pc = sub.add_parser("probe-create"); pc.add_argument("--like", required=True, help="a bot on this account to copy language, voice and number from")
    a = p.parse_args()

    if a.cmd == "check":
        res = check(uuid_for(a.bot), a.direction)
        sys.exit(0 if all(ok for ok, _ in res if ok is not None) else 1)
    if a.cmd == "platform":
        return platform(a.gap, a.force)
    if a.cmd == "restore-tester":
        return restore_tester(json.load(open(a.saved_json, encoding="utf-8")), a.saved_json)
    if a.cmd == "probe-create":
        return probe_create(a.like)

    facts = parse_facts(a.fact)
    reask = {}
    for x in a.reask:
        k, _, v = x.partition("="); reask[k.strip()] = v.strip().strip('"')

    if a.cmd == "grade":
        c1, c2 = req("GET", "/api/call/" + a.call1)[1], req("GET", "/api/call/" + a.call2)[1]
        cfg = check(c1.get("agent_id"), quiet=True) if c1.get("agent_id") else None
        return report(*grade(c1, c2, facts, reask), c1, c2, cfg, None)

    bot = uuid_for(a.bot)
    cfg = check(bot, a.direction)
    if any(ok is False for ok, _ in cfg):
        sys.exit(1)
    busy = tester_busy()
    if busy and not a.force:
        sys.exit(f"tester line busy: {busy}. Wait, or pass --force if you know it is free.")
    stamp = datetime.datetime.now().strftime("%Y-%m-%d")
    run_dir = os.path.join(REPO, "raya/testcases/runs", f"memory-{stamp}", a.label)
    os.makedirs(run_dir, exist_ok=True)
    p1, p2 = personas(facts, run_dir)
    p1, p2 = a.seed or p1, a.recall or p2
    args_path = a.args or os.path.join(run_dir, "args.json")
    if not a.args:
        open(args_path, "w").write("{}")

    # The tester is shared: remember its persona and language, put them back afterwards.
    saved, saved_path = save_tester(run_dir)
    b = agent(bot)
    try:
        req("PATCH", "/api/agent/" + TESTER, {"language_id": b.get("language_id"), "voice_id": b.get("voice_id")})
        subprocess.run([sys.executable, os.path.join(REPO, "scripts/raya_testcall.py"), "persona", TESTER, p1], check=True)
        c1 = one_call(bot, a.direction, args_path, f"{a.label}-call1", run_dir)
        if not c1:
            sys.exit("call 1 never connected (see the log in " + os.path.relpath(run_dir, REPO) + "); nothing graded")
        json.dump(c1, open(os.path.join(run_dir, f"{c1['uuid']}.json"), "w"), ensure_ascii=False, indent=1)
        print(f"call 1 {c1['uuid']} done; waiting {a.gap}s for the memory to be written")
        time.sleep(a.gap)
        subprocess.run([sys.executable, os.path.join(REPO, "scripts/raya_testcall.py"), "persona", TESTER, p2], check=True)
        c2 = one_call(bot, a.direction, args_path, f"{a.label}-call2", run_dir)
        if not c2:
            sys.exit(f"call 2 never connected; call 1 was {c1['uuid']}. Re-run call 2 only with `grade` once it connects")
        json.dump(c2, open(os.path.join(run_dir, f"{c2['uuid']}.json"), "w"), ensure_ascii=False, indent=1)
    finally:
        restore_tester(saved, saved_path)
    report(*grade(c1, c2, facts, reask), c1, c2, cfg, os.path.join(run_dir, "report.md"), a.gap)


if __name__ == "__main__":
    main()
