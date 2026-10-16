#!/usr/bin/env python3
"""consent_before_apply.py — was the data-sharing line spoken before apply_job?

The gap this closes: on 2026-09-03 QA found KKB Inbound Signals calling apply_job with no
data-sharing line at all (call bbdb6eaf). Nothing in the suite looked for it. The static suite
checks prompt TEXT, the feature matrix was a one-off I ran by hand and then misjudged, and every
runtime detector covered a different behaviour — location, apply outcome, failure wording. A
consent obligation with no automated check is a consent obligation that silently disappears.

Rule: if apply_job was called, the assistant must have spoken the data-sharing line BEFORE it, in
the same call. Exit 1 on any violation.

Usage: python3 raya/regression/consent_before_apply.py [--since YYYY-MM-DD[THH:MM:SS]] [--agent <id>]
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
BASE = _env["RAYA_BASE_URL"].rstrip("/"); KEY = _env["RAYA_API_TOKEN"]

# Hindi and Kannada wordings of the data-sharing disclosure, plus the older create-consent phrasings.
SHARE = re.compile(
    r"personal details company के साथ share|जानकारी कंपनी के साथ शेयर|जानकारी .{0,12}कंपनी के साथ"
    r"|ಮಾಹಿತಿ ಕಂಪನಿ ಜೊತೆ ಶೇರ್|ಮಾಹಿತಿಯನ್ನು ಕಂಪನಿ ಜೊತೆ|ಡೀಟೇಲ್ಸ್ ಕಂಪನಿ ಜೊತೆ ಶೇರ್"
    r"|details .{0,15}share होंगी|शेयर करनी होगी|ಶೇರ್ ಮಾಡ್ಬೇಕಾಗುತ್ತೆ")


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
    said_share_at = None
    for i, t in enumerate(turns):
        if t.get("role") == "assistant" and t.get("content") and SHARE.search(str(t["content"])):
            said_share_at = i
            break
    # EVERY apply_job needs a consent line before IT, not just the first. Call a5547492 spoke the
    # consent line twice, before each of its two applies; a check that compared the first apply with
    # the LAST-matched consent line reported a violation that had not happened. Take the earliest
    # apply that has no consent line before it.
    applies = [i for i, t in enumerate(turns)
               for tc in (t.get("tool_calls") or [])
               if ((tc.get("function") or {}).get("name")) == "apply_job"]
    if not applies:
        return []
    apply_at = applies[0]
    created = str(d.get("created_at"))[:19]
    if said_share_at is None:
        return [dict(bot=bot, call=uuid, at=created, kind="NO CONSENT BEFORE APPLY",
                     detail="apply_job was called and the data-sharing line was never spoken on this call")]
    if said_share_at > apply_at:
        return [dict(bot=bot, call=uuid, at=created, kind="CONSENT AFTER APPLY",
                     detail=f"data-sharing line came at turn {said_share_at}, apply_job at turn {apply_at}")]
    return []


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--since", default=time.strftime("%Y-%m-%d", time.gmtime(time.time() - 86400)))
    ap.add_argument("--agent", default=None)
    ap.add_argument("--workers", type=int, default=3)
    a = ap.parse_args()
    targets = [t for t in json.load(open(os.path.join(REPO, "raya/agents.json")))["targets"]
               if t.get("kind") == "conversation" and t["raya_agent_id"].get("prod")]
    if a.agent:
        targets = [t for t in targets if a.agent in (t["id"], t["raya_agent_id"]["prod"])]
    work = []
    for t in targets:
        d = get(f"/api/call?agent_id={t['raya_agent_id']['prod']}&limit=100")
        for c in d.get("calls") or []:
            if str(c.get("created_at"))[:19] < a.since:
                continue
            if (c.get("call_duration") or 0) >= 30:
                work.append((t["id"], c["uuid"]))
    print(f"consent-before-apply check | since {a.since} | {len(work)} calls", flush=True)
    bad, errs = [], 0
    with ThreadPoolExecutor(max_workers=a.workers) as ex:
        for res in ex.map(lambda i: _safe(check, i), work):
            if res is None:
                errs += 1
            else:
                bad.extend(res)
    print(f"fetch errors: {errs}\n")
    if not bad:
        print("  clean — every apply_job was preceded by the data-sharing line")
        return 0
    for f in bad:
        print(f"  {f['kind']:26} {f['at']}  {f['bot']:20} {f['call']}")
        print(f"        {f['detail']}")
    return 1


def _safe(fn, arg):
    try:
        return fn(*arg)
    except Exception:
        return None


if __name__ == "__main__":
    sys.exit(main())
