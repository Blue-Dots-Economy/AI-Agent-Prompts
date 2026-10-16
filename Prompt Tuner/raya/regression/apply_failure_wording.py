#!/usr/bin/env python3
"""apply_failure_wording.py — assert the apply-failure line matches the error the tool returned.

The prompt's Apply Failure Handling is a single slot with a two-row lookup:
  row 1  ACTION_LIMIT_REACHED / "already exists"  -> "इस जॉब के लिए आपकी एप्लीकेशन पहले से लगी हुई है …"
  row 2  anything else                            -> "अभी इस जॉब में अप्लाई पूरा नहीं हो पाया …"
and NO line may diagnose a cause ("तकनीकी दिक्कत" and friends are banned outright).

UPDATE 2026-09-01 — "ROW 1 MISSED" was, until today, unfixable by any prompt wording. Across 9 real
`ACTION_LIMIT_REACHED` calls (3 bots, 2 languages, 2 directions, 3 successive prompt structures, and
one with the mapping written into the `apply_job` tool description itself) the explicit line was
spoken **zero** times. The conversation model does not receive the HTTP error body: the tool message
is `[Error: apply_job request failed (HTTP 422).]` and the `ACTION_LIMIT_REACHED` string lives in a
`__RAYA_TOOL_DEBUG__` block that is not fed back. So row 1 is now reached WITHOUT the error string —
from this call's own apply history and from `jobs_applied` in `${contact_memory}`, checked BEFORE the
tool fires (see "Already applied — check BEFORE you call the tool" in the prompts). A ROW 1 MISSED
finding here therefore now means the *memory pre-check* did not fire, which is a real prompt bug —
it is no longer the expected state.

Forcing the condition on the harness: do NOT pre-apply a (profile, job) pair through the backend. The
tester DID carries five live Ghaziabad profiles and the bot picks the most COMPLETE one, not
`items[0]`, so the pair you prepared is usually not the pair it uses (this silently produced a
meaningless pass). Instead pass the precondition through `agent_args`:
`contact_memory: {"jobs_applied": ["<date>: <role>, <company>, <city>"]}` with that job present in
`recommendations` — per-call, deterministic, and it leaves no residue on the shared DID.

Exit 1 if any call spoke the wrong row, or diagnosed a cause.

Usage: python3 raya/regression/apply_failure_wording.py [--since YYYY-MM-DD] [--agent <id|uuid>]
"""
import argparse, json, os, re, sys, time, urllib.request
from concurrent.futures import ThreadPoolExecutor

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
_env = {}
for _l in open(os.path.join(REPO, "raya/.env")):
    _l = _l.strip()
    if "=" in _l and not _l.startswith("#"):
        k, v = _l.split("=", 1)
        _env[k.strip()] = v.strip().strip('"').strip("'")
BASE = _env["RAYA_BASE_URL"].rstrip("/")
KEY = _env["RAYA_API_TOKEN"]

ROW1 = "एप्लीकेशन पहले से लगी हुई है"          # truthful already-applied line
ROW2 = "अप्लाई पूरा नहीं हो पाया"              # causeless fallback
CAUSE = re.compile(r"तकनीकी दिक्कत|technical (issue|problem)|सिस्टम की दिक्कत|सर्वर")
DUP = re.compile(r"ACTION_LIMIT_REACHED|already exists")


def get(path, tries=4):
    for i in range(tries):
        try:
            r = urllib.request.Request(BASE + path, headers={
                "X-API-Key": KEY, "User-Agent": "Mozilla/5.0", "Accept": "application/json"})
            with urllib.request.urlopen(r, timeout=120) as resp:
                return json.loads(resp.read())
        except Exception:
            if i == tries - 1:
                raise
            time.sleep(1.5 * (i + 1))


def check(bot, uuid):
    d = get("/api/call/" + uuid)
    turns = d.get("call_transcript") or []
    tool_blob = " ".join(str(m.get("content") or "") for m in turns if m.get("role") == "tool")
    if "apply_job request failed" not in tool_blob and "apply_job" not in tool_blob:
        return []
    errored = "request failed" in tool_blob or '"status":"error"' in tool_blob or "'status': 'error'" in tool_blob
    if not errored:
        return []
    agent_text = " ".join(str(m.get("content") or "") for m in turns if m.get("role") == "assistant")
    out = []
    is_dup = bool(DUP.search(tool_blob))
    said_row1 = ROW1 in agent_text
    said_row2 = ROW2 in agent_text
    cause = CAUSE.search(agent_text)
    created = str(d.get("created_at"))[:19]
    if cause:
        out.append(dict(bot=bot, call=uuid, at=created, kind="DIAGNOSED A CAUSE",
                        detail=cause.group(0)))
    if is_dup and not said_row1:
        out.append(dict(bot=bot, call=uuid, at=created, kind="ROW 1 MISSED",
                        detail="duplicate apply but the already-applied line was not spoken"
                               + (" (said the fallback instead)" if said_row2 else "")))
    if (not is_dup) and said_row1:
        out.append(dict(bot=bot, call=uuid, at=created, kind="ROW 1 WRONGLY USED",
                        detail="said 'already applied' on an error that was not a duplicate"))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--since", default=time.strftime("%Y-%m-%d", time.gmtime(time.time() - 86400)))
    ap.add_argument("--agent", default=None)
    ap.add_argument("--workers", type=int, default=4)
    a = ap.parse_args()
    targets = [t for t in json.load(open(os.path.join(REPO, "raya/agents.json")))["targets"]
               if t.get("kind") == "conversation" and t["raya_agent_id"].get("prod")]
    if a.agent:
        targets = [t for t in targets if a.agent in (t["id"], t["raya_agent_id"]["prod"])]
    work = []
    for t in targets:
        off = 0
        while True:
            d = get(f"/api/call?agent_id={t['raya_agent_id']['prod']}&limit=100&offset={off}")
            cs = d.get("calls") or []
            if not cs:
                break
            older = False
            for c in cs:
                if str(c.get("created_at"))[:19] < a.since:
                    older = True
                    continue
                if (c.get("call_duration") or 0) >= 20:
                    work.append((t["id"], c["uuid"]))
            if older or len(cs) < 100:
                break
            off += 100
    print(f"apply-failure wording check | since {a.since} | {len(work)} calls", flush=True)
    bad, errs = [], 0
    with ThreadPoolExecutor(max_workers=a.workers) as ex:
        for res in ex.map(lambda i: _safe(check, i), work):
            if res is None:
                errs += 1
            else:
                bad.extend(res)
    print(f"fetch errors: {errs}\n")
    if not bad:
        print("  clean — every apply-failure line matched its error, and none diagnosed a cause")
        return 0
    for f in bad:
        print(f"  {f['kind']:20} {f['at']}  {f['bot']:20} {f['call']}")
        print(f"        {f['detail']}")
    return 1


def _safe(fn, arg):
    try:
        return fn(*arg)
    except Exception:
        return None


if __name__ == "__main__":
    sys.exit(main())
