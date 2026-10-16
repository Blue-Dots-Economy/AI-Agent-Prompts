#!/usr/bin/env python3
"""Run ONE agent-to-agent voice test end-to-end and dump the graded transcript.

A TESTER agent (inbound DID, non-interruptable, short max-duration) role-plays a human persona;
the BOT UNDER TEST (outbound agent) is triggered to call the tester's DID; they converse; we
pull the transcript + call_output to grade against the checklists in
.claude/skills/voice-test/reference/checklists/.

Flow: fire `POST /api/call` (agent_id = bot, to_number = tester 10-digit DID, out_did OMITTED)
-> poll to terminal -> dump bot transcript (with tool_calls) + call_output + the tester leg.

Reality of the platform (learned the hard way — see the /voice-test skill):
  * `POST /api/call` is rate-limited ~1 per ~13s (429 -> back off).
  * Bridging is INTERMITTENT: some dials fail immediately (outcome Failure/Unanswered, dur=0,
    no transcript). We retry the connect CONNECT_TRIES times with a cooldown.
  * Passing out_did explicitly gave 'Unanswered'; omitting it connects.
  * `GET /api/call/{uuid}` LAGS after a call (shows Pending/dur=0 briefly) -> keep polling.
  * The tester (callee) receives NO agent_args -> a scenario cannot be selected per call via
    agent_args; select the persona by PATCHing the tester prompt (scripts/raya_testcall.py persona).

Usage: raya_testrun.py <bot_uuid> <to_10digit> <args_json> <tester_uuid> [label]
Env: raya/.env (RAYA_BASE_URL, RAYA_API_TOKEN). Token never printed.
"""
import json, os, sys, time, urllib.request, urllib.error

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_env = {}
for _l in open(os.path.join(REPO, "raya/.env")):
    _l = _l.strip()
    if "=" in _l and not _l.startswith("#"):
        k, v = _l.split("=", 1); _env[k.strip()] = v.strip()
BASE = _env["RAYA_BASE_URL"].rstrip("/"); KEY = _env["RAYA_API_TOKEN"]
CONNECT_TRIES = 4
# Measured 2026-09-02 over 115 harness dials: bridging is NOT random telephony flakiness, it is
# contention on the single tester DID. Bridge rate against how long the line had been free:
#     0-30s after the previous call ended   4/15   27%
#     30-90s                               15/80   19%   <- the old 45s backoff lived here
#     90s-10min                             3/7    43%
#     >10min (line idle)                    8/13   62%
# Real numbers, which have no such contention, bridge at 11/16 (69%). Redialling a line that has not
# finished releasing just burns the attempt, so give it real time. This costs wall-clock and buys back
# far more of it than it spends.
CONNECT_BACKOFF = 90   # measured sweet spot: >90s idle recovers most of the bridge rate without burning 13 min per failed pass


def req(method, path, body=None, tries=4):
    for a in range(tries):
        data = json.dumps(body).encode() if body is not None else None
        h = {"X-API-Key": KEY, "User-Agent": "Mozilla/5.0"}
        if data is not None:
            h["Content-Type"] = "application/json"
        r = urllib.request.Request(BASE + path, data=data, headers=h, method=method)
        try:
            with urllib.request.urlopen(r, timeout=30) as resp:
                raw = resp.read().decode()
                return resp.status, (json.loads(raw) if raw.strip() else {})
        except urllib.error.HTTPError as e:
            return e.code, {"_err": e.read().decode()[:300]}
        except Exception as e:
            if a == tries - 1:
                return 0, {"_err": str(e)[:150]}
            time.sleep(4)


# Unbuffered stdout. When this script's output is redirected to a file, Python block-buffers it, so
# `tail -f run.log` shows an EMPTY file while the call is running and a stale one after it finishes.
# On 2026-09-23 that cost a wrong conclusion: two calls that completed fine (8ae650f2, ab98be47) were
# read as "nothing connects" off a log that had not been flushed, and a shared DID was reassigned on
# the strength of it. Reconfigure immediately -- before any print in this module runs.
try:
    sys.stdout.reconfigure(line_buffering=True)
except Exception:
    pass


def preflight_did(tester, to, bot=None):
    """Refuse to dial a DID that is not bound to the tester agent.

    Why: DIDs are shared and get rebound. On 2026-09-23 the long-standing tester DID 7946350285 had
    been reassigned as the `in_did` of Purple-dots-with-APIs-V2-Inbound, so every "test" call reached
    that bot instead of our tester -- two agents talked past each other and the transcript looked like
    a bot bug. Later the tester's own new number (911204404272) accepted nothing at all: every poll
    returned outcome='Pending', dur=0, turns=0. Both failures are invisible in the dump unless you
    already suspect them, so check the binding BEFORE burning four minutes on a call.
    """
    # REVERSE-DIRECTION TEST: when the dialling agent IS the tester, the tester is the CALLER and the
    # bot under test is the receiver -- so the DID being dialled is the BOT's in_did, not the tester's.
    # Check that instead. (This guard blocked the first inbound run on 2026-09-23: it assumed the
    # tester always answers, which is only true for the outbound direction.)
    if bot and bot == tester:
        st, d = req("GET", "/api/agent/" + tester)
        d = (d or {}).get("data", d) or {}
        want = str(to).lstrip("+")[-10:]
        owner = None
        for off in (0, 50):
            s2, page = req("GET", f"/api/agent?limit=50&offset={off}")
            for a in (page.get("agents") or page.get("data") or []):
                s3, ad = req("GET", "/api/agent/" + a["id"])
                ad = (ad or {}).get("data", ad) or {}
                if str(ad.get("in_did") or "").endswith(want):
                    owner = ad.get("name"); break
            if owner:
                break
        if not owner:
            print(f"!! PREFLIGHT: nothing answers on {to} -- no agent has it as an in_did. Refusing to dial.")
            sys.exit(2)
        print(f"[preflight] reverse test: tester dials {to} -> answered by {owner!r}  OK")
        return
    st, d = req("GET", "/api/agent/" + tester)
    d = (d or {}).get("data", d) or {}
    in_did = str(d.get("in_did") or "")
    want = str(to).lstrip("+")
    if not in_did:
        print(f"!! PREFLIGHT: tester {d.get('name')!r} has NO in_did -- it cannot receive a call. "
              f"Bind one, or pass the DID that actually rings it.")
        sys.exit(2)
    if not in_did.endswith(want[-10:]):
        print(f"!! PREFLIGHT: you are dialling {to}, but tester {d.get('name')!r} answers on {in_did}. "
              f"That call would reach whichever agent owns {to} -- not the tester. Refusing to dial.")
        sys.exit(2)
    print(f"[preflight] {to} -> in_did {in_did} on {d.get('name')!r}  OK")


def main():
    if len(sys.argv) < 5 or sys.argv[1].startswith("-"):
        sys.exit(__doc__ or "usage: raya_testrun.py <bot_uuid> <tester_10digit_DID> <args.json> <tester_uuid> [label]")
    bot, to, args_path, tester = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4]
    label = sys.argv[5] if len(sys.argv) > 5 else "test"
    preflight_did(tester, to, bot)
    agent_args = json.load(open(args_path, encoding="utf-8"))
    body = {"agent_id": bot, "to_number": to, "agent_args": agent_args,
            "country_code": "91", "timezone": "Asia/Kolkata"}  # out_did omitted on purpose

    def fire():
        for _ in range(6):
            st, resp = req("POST", "/api/call", body)
            if st == 429:
                ra = 15
                try: ra = int(json.loads(resp["_err"]).get("retry_after", 15))
                except Exception: pass
                print(f"[{label}] 429; waiting {ra + 2}s"); time.sleep(ra + 2); continue
            print(f"[{label}] POST /api/call -> {st} {json.dumps(resp)[:140]}")
            return resp.get("uuid") if isinstance(resp, dict) else None
        return None

    def poll(uuid):
        # Poll fast at first, then slow down. A dial that is never going to bridge resolves to
        # Failure within a couple of seconds, but the old fixed 18s sleep BEFORE the first check
        # meant every dead dial still cost 18s -- and at a 27% bridge rate most dials are dead ones.
        # A live call then only needs coarse polling, since it runs 90-180s.
        c = {}
        waits = [3, 3, 4, 5] + [15] * 24
        for i, w in enumerate(waits):
            time.sleep(w)
            _, c = req("GET", f"/api/call/{uuid}")
            oc = c.get("outcome"); turns = len(c.get("call_transcript") or [])
            print(f"[{label}] poll {i}: outcome={oc!r} dur={c.get('call_duration')} turns={turns}")
            if oc == "Completed" and turns > 0:
                return c
            if oc in ("Failure", "Unanswered", "No Answer", "Rejected"):
                return c
        return c

    final = None
    for attempt in range(CONNECT_TRIES):
        uuid = fire()
        if not uuid:
            print(f"[{label}] no call uuid; abort"); return
        c = poll(uuid)
        if c.get("outcome") == "Completed" and len(c.get("call_transcript") or []) > 0:
            final = c; break
        print(f"[{label}] connect attempt {attempt + 1} did not bridge "
              f"(outcome={c.get('outcome')}); letting the tester line settle for {CONNECT_BACKOFF}s")
        time.sleep(CONNECT_BACKOFF)

    if final is None:
        print(f"\n[{label}] NEVER BRIDGED after {CONNECT_TRIES} attempts (flaky telephony)."); return

    print("\n" + "=" * 76)
    print(f"[{label}] BOT {final.get('uuid')} outcome={final.get('outcome')} dur={final.get('call_duration')}")
    print("call_output:", json.dumps(final.get("call_output"), ensure_ascii=False, indent=2))
    print("\nTRANSCRIPT:")
    for t in (final.get("call_transcript") or []):
        role = t.get("role")
        for tc in (t.get("tool_calls") or []):
            fn = tc.get("function") or {}
            print(f"[{role}->TOOL] {fn.get('name')}({fn.get('arguments')})")
        content = t.get("content")
        if content:
            content = content if role == "tool" else str(content).replace("\n", " ")
            print(f"[{role}] {content[:600]}")

    _, td = req("GET", f"/api/call?agent_id={tester}&limit=1")
    tc = (td.get("calls") or [])
    if tc:
        _, tcc = req("GET", f"/api/call/{tc[0]['uuid']}")
        print(f"\n[{label}] TESTER leg {tc[0]['uuid'][:8]}: outcome={tcc.get('outcome')} "
              f"dur={tcc.get('call_duration')} turns={len(tcc.get('call_transcript') or [])} "
              f"call_output={json.dumps(tcc.get('call_output'), ensure_ascii=False)[:200]}")


if __name__ == "__main__":
    main()
