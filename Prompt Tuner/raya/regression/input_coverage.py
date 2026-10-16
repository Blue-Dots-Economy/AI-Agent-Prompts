#!/usr/bin/env python3
"""input_coverage.py — is the bot USING every argument the campaign sends it?

The bug this closes (D68, 2026-09-04). Maya outbound asked every caller for their area from scratch.
Three detectors flagged it, and it survived a fix to the confirm branch and a fix to the closed set,
because neither was the cause: `${location}` appears 9 times in the KKB Signals master and **zero**
times in any Maya prompt, while the campaign had been sending it all along. The open ask was not a
mis-ranked branch — it was the only reachable one.

Nothing in the prompt was wrong, so no amount of reading the prompt finds it. Something was ABSENT.
The only way to see it is to compare what the platform actually sends against what the prompt knows,
per bot — a variable declared in the master says nothing about the mirror or a spin-off.

REPORTS, per conversation bot with a prod uuid:
  UNUSED ARG   an agent_args key seen on real calls that the prompt never mentions -> being paid for
               and thrown away. This is the D68 class and it is a hard finding.
  UNSENT VAR   a ${var} the prompt reads that no recent call carried. Informational: it may be a
               genuinely optional field, or the campaign may have stopped sending it.

Keys that are platform plumbing rather than content are ignored (see IGNORE).

Usage: python3 raya/regression/input_coverage.py [--limit 40] [--agent <id>]
Exit 1 if any UNUSED ARG is found.
"""
import argparse, json, os, re, sys, time, urllib.error, urllib.request

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
_env = {}
for _l in open(os.path.join(REPO, "raya/.env")):
    _l = _l.strip()
    if "=" in _l and not _l.startswith("#"):
        _k, _v = _l.split("=", 1); _env[_k.strip()] = _v.strip().strip('"').strip("'")
BASE = _env["RAYA_BASE_URL"].rstrip("/"); TOKEN = _env["RAYA_API_TOKEN"]

# Plumbing the prompt is not expected to name, or that it names by another route.
IGNORE = {"country_code", "contact_phone", "phoneNumber", "phone_number", "out_did", "to_number",
          "caller_no", "agent_id", "call_id", "uuid"}
# Keys the PLATFORM adds for its own scheduling/bookkeeping. They are not campaign content and no
# prompt should name them. Matched by prefix so a new one does not become a false finding.
IGNORE_PREFIXES = ("_",)


def get(path, tries=6):
    for i in range(tries):
        try:
            req = urllib.request.Request(BASE + path, headers={"X-API-Key": TOKEN, "User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=60) as r:
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


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--limit", type=int, default=40, help="calls to sample per bot")
    ap.add_argument("--agent", default="")
    a = ap.parse_args()
    man = json.load(open(os.path.join(REPO, "raya/agents.json"), encoding="utf-8"))
    targets = [t for t in man["targets"]
               if t.get("kind") == "conversation" and (t.get("raya_agent_id") or {}).get("prod")]
    if a.agent:
        targets = [t for t in targets if t["id"] == a.agent]
    fails = 0
    any_args = False
    print("input-coverage check | %d bots | %d calls sampled each" % (len(targets), a.limit))
    for t in targets:
        path = os.path.join(REPO, t["file"])
        if not os.path.exists(path):
            print("  ??   %-22s prompt file missing: %s" % (t["id"], t["file"])); continue
        text = open(path, encoding="utf-8").read()
        known = set(re.findall(r"\$\{([a-zA-Z_][a-zA-Z0-9_]*)\}", text))
        # a bare mention counts too: some prompts name an arg without the ${} wrapper
        seen = set()
        try:
            d = get("/api/call?agent_id=%s&limit=%d" % (t["raya_agent_id"]["prod"], a.limit))
        except Exception as e:
            print("  ??   %-22s could not list calls: %s" % (t["id"], str(e)[:40])); continue
        # The LIST endpoint does not return agent_args -- only the per-call GET does. The first
        # version of this script read the list and reported "INPUT COVERAGE CLEAN" for all 18 bots off
        # `args seen: 0`, i.e. it checked nothing and passed. Fetch the calls.
        # Judge CAMPAIGN coverage from CAMPAIGN traffic only. Our own harness dials go to the tester
        # DID and carry whatever a fixture happened to set, which is not evidence the campaign sends
        # a field: dkb-kn-signals showed `contact_name` as an "unused arg" on three calls whose value
        # was literally 'ಪರೀಕ್ಷೆ' ("test"), while the Hindi twin's real campaign traffic never carries
        # the key at all.
        TESTERS = ("1204404272", "7946350285")   # current tester DID, and the pre-2026-09-23 one in older history
        listed = [c for c in (d.get("calls") or d.get("data") or [])
                  if (c.get("call_duration") or 0) >= 10
                  and not any(t in str(c.get("to_number") or "") or t in str(c.get("caller_no") or "") for t in TESTERS)]
        fetched = 0
        for c in listed:
            try:
                full = get("/api/call/" + c["uuid"])
            except Exception:
                continue
            fetched += 1
            for k in (full.get("agent_args") or {}):
                seen.add(k)
        if not fetched:
            print("  ??   %-22s no call could be fetched — NOT a pass" % t["id"])
            continue
        if not seen:
            print("  ??   %-22s %d call(s) fetched and none carried ANY agent_args — inbound bots are"
                  " expected here; for an OUTBOUND bot this is itself the finding"
                  % (t["id"], fetched))
        any_args = any_args or bool(seen)
        unused = sorted(k for k in seen - known - IGNORE
                        if not k.startswith(IGNORE_PREFIXES)
                        and not re.search(r"(?<![A-Za-z0-9_])%s(?![A-Za-z0-9_])" % re.escape(k), text))
        unsent = sorted(k for k in known - seen - IGNORE if not k.startswith(IGNORE_PREFIXES))
        status = "FAIL" if unused else "OK"
        print("  %-4s %-22s args seen: %-2d  prompt knows: %-2d  (%d call(s) read)"
              % (status, t["id"], len(seen), len(known), fetched))
        for k in unused:
            print("        UNUSED ARG   %-24s sent on real calls, never mentioned in the prompt" % k)
            fails += 1
        for k in unsent:
            print("        unsent var   %-24s (info) prompt reads it; no sampled call carried it" % k)
    print("")
    if fails:
        print("INPUT COVERAGE: %d argument(s) sent and never used" % fails); sys.exit(1)
    if not any_args:
        print("INPUT COVERAGE INCONCLUSIVE — no bot produced a single agent_args key, so nothing was"
              " actually compared. Do NOT read this as a pass."); sys.exit(1)
    print("INPUT COVERAGE CLEAN — every argument the campaigns send is named in the prompt")


if __name__ == "__main__":
    main()
